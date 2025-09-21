# app_order/models.py
from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.core.exceptions import ValidationError

from app_home.models import DiningTable
from app_menu.models import MenuItem  # RecipeItem nằm trong app_menu

class Order(models.Model):
    class OrderType(models.TextChoices):
        DINE_IN = "dine_in", "Ăn tại chỗ"
        TAKEAWAY = "takeaway", "Mang đi"
        DELIVERY = "delivery", "Giao hàng"

    class OrderStatus(models.TextChoices):
        PENDING = "pending", "Chờ xác nhận"
        PREPARING = "preparing", "Đang làm"
        READY = "ready", "Sẵn sàng"
        COMPLETED = "completed", "Hoàn tất"
        CANCELLED = "cancelled", "Hủy"

    class PaymentStatus(models.TextChoices):
        UNPAID = "unpaid", "Chưa thanh toán"
        PENDING = "pending", "Chờ thanh toán"
        PAID = "paid", "Đã thanh toán"
        REFUNDED = "refunded", "Hoàn tiền"

    order_number = models.CharField("Mã đơn hàng", max_length=50, unique=True)
    customer_name = models.CharField("Tên khách", max_length=255, blank=True, default="")
    customer_phone = models.CharField("SĐT khách", max_length=50, blank=True, default="")
    order_type = models.CharField("Hình thức", max_length=20, choices=OrderType.choices, default=OrderType.DINE_IN)
    table = models.ForeignKey(DiningTable, on_delete=models.SET_NULL, null=True, blank=True,
                              related_name="orders", verbose_name="Bàn")
    order_status = models.CharField("Trạng thái đơn", max_length=20, choices=OrderStatus.choices,
                                    default=OrderStatus.PENDING)
    payment_status = models.CharField("Trạng thái thanh toán", max_length=20, choices=PaymentStatus.choices,
                                      default=PaymentStatus.UNPAID)
    created_at = models.DateTimeField("Ngày tạo", default=timezone.now)
    completed_at = models.DateTimeField("Ngày hoàn tất", null=True, blank=True)
    notes = models.TextField("Ghi chú", blank=True, default="")

    class Meta:
        indexes = [
            models.Index(fields=["created_at"]),
            models.Index(fields=["order_number"]),
            models.Index(fields=["order_status"]),
            models.Index(fields=["payment_status"]),
        ]
        verbose_name = "Đơn hàng"
        verbose_name_plural = "Đơn hàng"

    def __str__(self):
        return self.order_number

    @property
    def subtotal(self) -> Decimal:
        # cộng theo snapshot item.total (an toàn)
        agg = self.items.aggregate(s=models.Sum("total"))
        return Decimal(agg["s"] or 0)

    @property
    def total(self) -> Decimal:
        # nếu không dùng thuế/giảm giá, total == subtotal
        return self.subtotal


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE,
                              related_name="items", verbose_name="Đơn hàng")
    menu_item = models.ForeignKey(MenuItem, on_delete=models.SET_NULL,
                                  null=True, blank=True, related_name="order_items", verbose_name="Món")
    # ✅ snapshot để giữ giá/tên tại thời điểm đặt
    name = models.CharField("Tên món (snapshot)", max_length=255, blank=True, default="")
    unit_price = models.DecimalField("Đơn giá (snapshot)", max_digits=14, decimal_places=2,
                                     validators=[MinValueValidator(0)], default=0)
    quantity = models.PositiveIntegerField("Số lượng", default=1)
    total = models.DecimalField("Thành tiền (dòng)", max_digits=14, decimal_places=2,
                                default=0, validators=[MinValueValidator(0)])

    class Meta:
        verbose_name = "Mặt hàng trong đơn"
        verbose_name_plural = "Mặt hàng trong đơn"

    def clean(self):
        """Check tồn kho theo BOM của món."""
        if self.menu_item and self.quantity:
            from collections import defaultdict
            needs = defaultdict(Decimal)
            # lấy BOM
            for ri in self.menu_item.recipe_items.select_related("ingredient").all():
                needs[ri.ingredient_id] += Decimal(ri.quantity or 0) * Decimal(self.quantity)

            # so với tồn hiện có
            # Ingredient của bạn nằm ở app nào thì import ở đó
            from app_inventory.models import Ingredient  # đổi nếu bạn để Ingredient ở app khác
            lack = []
            for ing_id, need in needs.items():
                ing = Ingredient.objects.get(pk=ing_id)
                have = Decimal(ing.current_stock or 0)
                if need > have:
                    lack.append(f"{ing.name}: cần {need}, còn {have}")
            if lack:
                raise ValidationError({"menu_item": "Thiếu nguyên liệu: " + "; ".join(lack)})

    def save(self, *args, **kwargs):
        if self.menu_item:
            if not self.name:
                self.name = self.menu_item.name
            # snapshot giá tại thời điểm đặt
            if not self.unit_price or self.unit_price == 0:
                self.unit_price = self.menu_item.price

        self.total = Decimal(self.unit_price or 0) * Decimal(self.quantity or 0)
        self.full_clean(exclude=None)  # check tồn kho như bạn đã viết
        super().save(*args, **kwargs)
class Payment(models.Model):
    class Method(models.TextChoices):
        CASH = "cash", "Tiền mặt"
        CARD = "card", "Thẻ"
        TRANSFER = "transfer", "Chuyển khoản"
        E_WALLET = "ewallet", "Ví điện tử"

    order = models.ForeignKey(Order, on_delete=models.CASCADE,
                              related_name="payments", verbose_name="Đơn hàng")
    method = models.CharField("Phương thức", max_length=20, choices=Method.choices)
    amount = models.DecimalField("Số tiền", max_digits=14, decimal_places=2,
                                 validators=[MinValueValidator(0)])
    paid_at = models.DateTimeField("Thời điểm thanh toán", default=timezone.now)
    note = models.CharField("Ghi chú", max_length=255, blank=True, default="")

    class Meta:
        indexes = [models.Index(fields=["paid_at"])]
        verbose_name = "Thanh toán"
        verbose_name_plural = "Thanh toán"

    def __str__(self):
        return f"{self.get_method_display()} - {self.amount}"
