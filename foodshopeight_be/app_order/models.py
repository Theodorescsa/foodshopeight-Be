from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.conf import settings
from app_home.models import DiningTable
from app_menu.models import MenuItem

class Order(models.Model):
    class OrderType(models.TextChoices):
        DINE_IN = "dine_in", "Ăn tại chỗ"
        TAKEAWAY = "takeaway", "Mang đi"
        DELIVERY = "delivery", "Giao hàng"  # dự phòng

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

    order_number = models.CharField("Mã đơn hàng", max_length=50, unique=True)  # "ORD-001"
    customer_name = models.CharField("Tên khách", max_length=255, blank=True, default="")
    customer_phone = models.CharField("SĐT khách", max_length=50, blank=True, default="")
    order_type = models.CharField("Hình thức", max_length=20, choices=OrderType.choices, default=OrderType.DINE_IN)

    table = models.ForeignKey(DiningTable, on_delete=models.SET_NULL, null=True, blank=True, related_name="orders", verbose_name="Bàn")

    subtotal = models.DecimalField("Tạm tính", max_digits=14, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    tax = models.DecimalField("Thuế", max_digits=14, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    discount = models.DecimalField("Giảm giá", max_digits=14, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    total = models.DecimalField("Thành tiền", max_digits=14, decimal_places=2, default=0, validators=[MinValueValidator(0)])

    order_status = models.CharField("Trạng thái đơn", max_length=20, choices=OrderStatus.choices, default=OrderStatus.PENDING)
    payment_status = models.CharField("Trạng thái thanh toán", max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.UNPAID)

    created_at = models.DateTimeField("Ngày tạo", default=timezone.now)
    completed_at = models.DateTimeField("Ngày hoàn tất", null=True, blank=True)

    staff_name = models.CharField("Nhân viên phụ trách", max_length=255, blank=True, default="")
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

    def recalc_totals(self):
        agg = self.items.aggregate(
            subtotal=models.Sum(models.F("unit_price") * models.F("quantity")),
        )
        self.subtotal = agg["subtotal"] or 0
        self.total = self.subtotal + self.tax - self.discount
        return self

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items", verbose_name="Đơn hàng")
    menu_item = models.ForeignKey(MenuItem, on_delete=models.SET_NULL, null=True, blank=True, related_name="order_items", verbose_name="Món")
    name = models.CharField("Tên món (snapshot)", max_length=255)
    unit_price = models.DecimalField("Đơn giá (snapshot)", max_digits=14, decimal_places=2, validators=[MinValueValidator(0)])
    quantity = models.PositiveIntegerField("Số lượng", default=1)
    total = models.DecimalField("Thành tiền (dòng)", max_digits=14, decimal_places=2, default=0, validators=[MinValueValidator(0)])

    class Meta:
        verbose_name = "Mặt hàng trong đơn"
        verbose_name_plural = "Mặt hàng trong đơn"

    def save(self, *args, **kwargs):
        self.total = (self.unit_price or 0) * (self.quantity or 0)
        super().save(*args, **kwargs)

class Payment(models.Model):
    class Method(models.TextChoices):
        CASH = "cash", "Tiền mặt"
        CARD = "card", "Thẻ"
        TRANSFER = "transfer", "Chuyển khoản"
        E_WALLET = "ewallet", "Ví điện tử"

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="payments", verbose_name="Đơn hàng")
    method = models.CharField("Phương thức", max_length=20, choices=Method.choices)
    amount = models.DecimalField("Số tiền", max_digits=14, decimal_places=2, validators=[MinValueValidator(0)])
    paid_at = models.DateTimeField("Thời điểm thanh toán", default=timezone.now)
    note = models.CharField("Ghi chú", max_length=255, blank=True, default="")

    class Meta:
        indexes = [models.Index(fields=["paid_at"])]
        verbose_name = "Thanh toán"
        verbose_name_plural = "Thanh toán"

    def __str__(self):
        return f"{self.get_method_display()} - {self.amount}"
