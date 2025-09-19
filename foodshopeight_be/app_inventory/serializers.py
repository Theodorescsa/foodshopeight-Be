# app_inventory/serializers.py
from rest_framework import serializers
from .models import Supplier, Ingredient, InventoryLot
from app_home.models import Unit, IngredientCategory
from app_home.serializers import UnitSerializer, IngredientCategorySerializer


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = [
            "id",
            "name",
            "contact_name",
            "phone",
            "email",
            "address",
            "note",
        ]
        extra_kwargs = {
            "name": {"help_text": "Tên nhà cung cấp (duy nhất)"},
            "contact_name": {"help_text": "Tên người liên hệ"},
            "phone": {"help_text": "SĐT liên hệ"},
            "email": {"help_text": "Email liên hệ"},
            "address": {"help_text": "Địa chỉ NCC"},
            "note": {"help_text": "Ghi chú thêm"},
        }


class IngredientSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(
        queryset=IngredientCategory.objects.all()
    )
    unit = serializers.PrimaryKeyRelatedField(
        queryset=Unit.objects.all()
    )

    category_detail = IngredientCategorySerializer(source="category", read_only=True)
    unit_detail = UnitSerializer(source="unit", read_only=True)

    current_stock = serializers.DecimalField(
        max_digits=12, decimal_places=3, read_only=True
    )

    class Meta:
        model = Ingredient
        fields = [
            "id",
            "name",
            "category", "category_detail",
            "unit", "unit_detail",
            "min_stock", "max_stock",
            "reference_unit_price",
            "is_active",
            "status",
            "last_updated",
            "current_stock",
        ]
        extra_kwargs = {
            "name": {"help_text": "Tên nguyên liệu (duy nhất)"},
            "min_stock": {"help_text": "Mức tồn tối thiểu (đề xuất)"},
            "max_stock": {"help_text": "Mức tồn tối đa (đề xuất)"},
            "reference_unit_price": {"help_text": "Giá tham chiếu/đơn vị (tuỳ chọn)"},
            "is_active": {"help_text": "Còn sử dụng nguyên liệu hay không"},
            "status": {"help_text": "Tình trạng tồn kho (in_stock/low_stock/out_of_stock)"},
            "last_updated": {"help_text": "Ngày cập nhật gần nhất"},
        }


class InventoryLotSerializer(serializers.ModelSerializer):
    ingredient = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    supplier = serializers.PrimaryKeyRelatedField(
        queryset=Supplier.objects.all(), allow_null=True, required=False
    )

    ingredient_detail = IngredientSerializer(source="ingredient", read_only=True)
    supplier_detail = SupplierSerializer(source="supplier", read_only=True)

    class Meta:
        model = InventoryLot
        fields = [
            "id",
            "ingredient", "ingredient_detail",
            "supplier", "supplier_detail",
            "quantity_received",
            "quantity_remaining",
            "unit_price",
            "received_date",
            "expiry_date",
        ]
        extra_kwargs = {
            "quantity_received": {"help_text": "Số lượng nhập vào (đơn vị theo Ingredient.unit)"},
            "quantity_remaining": {"help_text": "Số lượng còn lại (mặc định = quantity_received nếu để trống khi tạo mới)", "required": False},
            "unit_price": {"help_text": "Giá / 1 đơn vị"},
            "received_date": {"help_text": "Ngày nhận lô hàng (YYYY-MM-DD)"},
            "expiry_date": {"help_text": "Hạn dùng (nếu có)"},
        }

    def validate(self, attrs):
        qty_recv = attrs.get("quantity_received", getattr(self.instance, "quantity_received", None))
        qty_rem = attrs.get("quantity_remaining", getattr(self.instance, "quantity_remaining", None))
        if qty_recv is not None and qty_rem is not None and qty_rem > qty_recv:
            raise serializers.ValidationError({"quantity_remaining": "Không được lớn hơn quantity_received"})
        return attrs
