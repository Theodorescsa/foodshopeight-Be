from decimal import Decimal
from collections import defaultdict

from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from app_order.models import Order, OrderItem
from app_menu.models import MenuItem, RecipeItem
from app_inventory.models import Ingredient


# -------- OrderItem serializers --------

class OrderItemWriteSerializer(serializers.ModelSerializer):
    """
    Dùng cho ghi (tạo/cập nhật) – chỉ cần menu_item & quantity.
    unit_price/name sẽ snapshot theo MenuItem nếu không truyền.
    """
    menu_item = serializers.PrimaryKeyRelatedField(queryset=MenuItem.objects.all())

    class Meta:
        model = OrderItem
        fields = ("menu_item", "quantity", "unit_price", "name")
        extra_kwargs = {
            "quantity": {"required": True, "min_value": 1},
            "unit_price": {"required": False},
            "name": {"required": False},
        }

    def validate_quantity(self, v):
        if v is None or int(v) <= 0:
            raise serializers.ValidationError("Số lượng phải > 0.")
        return v


class OrderItemReadSerializer(serializers.ModelSerializer):
    """
    Dùng cho đọc – show đủ thông tin snapshot.
    """
    menu_item_name = serializers.CharField(source="menu_item.name", read_only=True)

    class Meta:
        model = OrderItem
        fields = ("id", "menu_item", "menu_item_name", "name", "unit_price", "quantity", "total")


# -------- Order serializer with stock check --------

class OrderSerializer(serializers.ModelSerializer):
    # Ghi: nhận mảng items (ghi)
    items = OrderItemWriteSerializer(many=True, write_only=True)
    # Đọc: trả mảng items (đọc)
    items_detail = OrderItemReadSerializer(many=True, read_only=True, source="items")

    class Meta:
        model = Order
        fields = (
            "id",
            "order_number",
            "customer_name",
            "customer_phone",
            "order_type",
            "table",
            "order_status",
            "payment_status",
            "created_at",
            "completed_at",
            "notes",
            "items",         # write-only
            "items_detail",  # read-only
            "subtotal",
            "total",
        )
        read_only_fields = ("created_at", "completed_at", "subtotal", "total")

    # ---- STOCK CHECK (aggregate toàn đơn) ----
    def _check_stock_for_items(self, items_data):
        """
        Gom nhu cầu Ingredient từ tất cả món/quantity trong đơn,
        so với tồn kho hiện tại (Ingredient.current_stock).
        Raise ValidationError nếu thiếu.
        """
        # 1) Collect menu_item_ids & quantity
        menu_qty = defaultdict(int)
        for it in items_data:
            mi: MenuItem = it["menu_item"]
            qty = int(it.get("quantity") or 0)
            if qty <= 0:
                raise serializers.ValidationError({"items": "Mỗi món phải có số lượng > 0."})
            menu_qty[mi.id] += qty

        if not menu_qty:
            raise serializers.ValidationError({"items": "Đơn hàng phải có ít nhất 1 món."})

        # 2) Prefetch BOM (RecipeItem)
        recipe_qs = (
            RecipeItem.objects
            .select_related("ingredient")
            .filter(menu_item_id__in=menu_qty.keys())
        )

        # 3) Tính nhu cầu theo Ingredient
        needs = defaultdict(Decimal)  # ingredient_id -> Decimal needed
        for ri in recipe_qs:
            per_serving = Decimal(ri.quantity or 0)
            qty_servings = Decimal(menu_qty[ri.menu_item_id] or 0)
            if per_serving > 0 and qty_servings > 0:
                needs[ri.ingredient_id] += per_serving * qty_servings

        if not needs:
            # Món chưa có BOM coi như không tốn nguyên liệu -> cho qua
            return

        # 4) Khóa hàng tồn để kiểm tra an toàn (giảm race condition)
        #    Lưu ý: chỉ LOCK rows Ingredient, không lock Lots; vẫn đủ "best effort".
        with transaction.atomic():
            ing_ids = list(needs.keys())
            locked_ings = (
                Ingredient.objects
                .select_for_update()
                .filter(id__in=ing_ids)
            )
            ing_map = {ing.id: ing for ing in locked_ings}

            lack_msgs = []
            for ing_id, need in needs.items():
                ing = ing_map.get(ing_id)
                if not ing:
                    lack_msgs.append(f"Nguyên liệu #{ing_id} không tồn tại.")
                    continue
                have = Decimal(ing.current_stock or 0)
                if need > have:
                    # Format gọn gàng
                    lack_msgs.append(f"{ing.name}: cần {need}, còn {have}")

            if lack_msgs:
                raise serializers.ValidationError({
                    "items": "Thiếu nguyên liệu cho đơn hàng: " + "; ".join(lack_msgs)
                })

    def validate(self, attrs):
        """
        Validate field-level; việc check stock làm ở create/update vì cần items.
        """
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        items_data = validated_data.pop("items", [])

        # Check tồn kho toàn đơn
        # (Gọi trước khi ghi DB; có select_for_update bên trong)
        self._check_stock_for_items(items_data)

        # Tạo Order
        order: Order = Order.objects.create(**validated_data)

        # Tạo từng OrderItem với snapshot giá/tên
        for it in items_data:
            menu_item: MenuItem = it["menu_item"]
            qty = int(it.get("quantity") or 0)

            # snapshot name & price
            unit_price = it.get("unit_price")
            if not unit_price or Decimal(unit_price) == 0:
                unit_price = menu_item.price

            name = it.get("name") or menu_item.name

            OrderItem.objects.create(
                order=order,
                menu_item=menu_item,
                name=name,
                unit_price=unit_price,
                quantity=qty,
                total=Decimal(unit_price) * Decimal(qty),
            )

        return order

    @transaction.atomic
    def update(self, instance: Order, validated_data):
        """
        Nếu muốn cho phép update items: tương tự create – gom nhu cầu và check lại.
        Ở đây demo update các trường đơn, không sửa items (tránh rắc rối).
        Nếu cần chỉnh items, nên implement endpoint chuyên dụng (PUT/PATCH items) + check stock.
        """
        for field in [
            "customer_name", "customer_phone", "order_type", "table",
            "order_status", "payment_status", "notes"
        ]:
            if field in validated_data:
                setattr(instance, field, validated_data[field])

        # auto set completed_at nếu chuyển trạng thái hoàn tất
        if instance.order_status == Order.OrderStatus.COMPLETED and not instance.completed_at:
            instance.completed_at = timezone.now()

        instance.save()
        return instance
