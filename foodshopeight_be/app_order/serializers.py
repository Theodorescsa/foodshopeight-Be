from rest_framework import serializers
from django.utils import timezone

from app_menu.models import MenuItem
from .models import Order, OrderItem, Payment


# ---------- ORDER ITEM ----------
class OrderItemSerializer(serializers.ModelSerializer):
    menu_item = serializers.PrimaryKeyRelatedField(
        queryset=MenuItem.objects.all(), allow_null=True, required=False
    )
    menu_item_name = serializers.CharField(source="menu_item.name", read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "order",
            "menu_item",
            "menu_item_name",
            "name",        # snapshot name (allow override)
            "unit_price",  # snapshot price (allow override)
            "quantity",
            "total",       # computed in model.save()
        ]
        read_only_fields = ["total"]

    def validate_quantity(self, value):
        if value is None or value < 1:
            raise serializers.ValidationError("Số lượng phải >= 1")
        return value

    def create(self, validated_data):
        # Model.save() đã tự snapshot name/unit_price nếu thiếu, và tính total + clean tồn kho
        obj = OrderItem(**validated_data)
        obj.save()
        return obj

    def update(self, instance, validated_data):
        # Cho phép cập nhật snapshot nếu cần (đặc biệt khi chỉnh giá tay)
        for f, v in validated_data.items():
            setattr(instance, f, v)
        instance.save()
        return instance


# ---------- PAYMENT ----------
class PaymentSerializer(serializers.ModelSerializer):
    order_number = serializers.CharField(source="order.order_number", read_only=True)

    class Meta:
        model = Payment
        fields = ["id", "order", "order_number", "method", "amount", "paid_at", "note"]

    def validate_amount(self, value):
        if value is None or value < 0:
            raise serializers.ValidationError("Số tiền phải >= 0")
        return value


# ---------- ORDER ----------
class OrderSerializer(serializers.ModelSerializer):
    table_name = serializers.CharField(source="table.name", read_only=True)
    # computed money
    subtotal = serializers.SerializerMethodField(read_only=True)
    total = serializers.SerializerMethodField(read_only=True)
    # nested read-only for detail view
    items = OrderItemSerializer(many=True, read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "order_number",
            "customer_name",
            "customer_phone",
            "order_type",
            "table",
            "table_name",
            # status
            "order_status",
            "payment_status",
            # time
            "created_at",
            "completed_at",
            # note
            "notes",
            # computed money
            "subtotal",
            "total",
            # nested
            "items",
            "payments",
        ]
        read_only_fields = ["created_at", "subtotal", "total"]

    def get_subtotal(self, obj):
        # dùng property trong model
        return float(obj.subtotal)

    def get_total(self, obj):
        return float(obj.total)

    def update(self, instance, validated_data):
        # cập nhật cơ bản
        for f, v in validated_data.items():
            setattr(instance, f, v)
        # nếu chuyển sang COMPLETED mà chưa có completed_at -> set
        if (
            instance.order_status == Order.OrderStatus.COMPLETED
            and not instance.completed_at
        ):
            instance.completed_at = timezone.now()
        instance.save()
        return instance
