from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from app_home.models import Unit, IngredientCategory

class Supplier(models.Model):
    name = models.CharField("Tên nhà cung cấp", max_length=255, unique=True)  # "Công ty Thịt Sạch ABC"
    contact_name = models.CharField("Người liên hệ", max_length=255, blank=True, default="")
    phone = models.CharField("Số điện thoại", max_length=50, blank=True, default="")
    email = models.EmailField("Email", blank=True, default="")
    address = models.CharField("Địa chỉ", max_length=255, blank=True, default="")
    note = models.TextField("Ghi chú", blank=True, default="")

    class Meta:
        verbose_name = "Nhà cung cấp"
        verbose_name_plural = "Nhà cung cấp"

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """
    Nguyên liệu master (ví dụ: Thịt bò, Gạo tẻ, Rau xanh, Nước mắm, Cà phê).
    current_stock sẽ được tính từ các lô (InventoryLot) hoặc có thể lưu cached.
    """
    name = models.CharField("Tên nguyên liệu", max_length=255, unique=True)
    category = models.ForeignKey(
        IngredientCategory,
        on_delete=models.PROTECT,
        related_name="ingredients",
        verbose_name="Danh mục"
    )
    unit = models.ForeignKey(
        Unit,
        on_delete=models.PROTECT,
        related_name="ingredients",
        verbose_name="Đơn vị tính"
    )
    min_stock = models.DecimalField("Tồn tối thiểu", max_digits=12, decimal_places=3, default=0,
                                    validators=[MinValueValidator(0)])
    max_stock = models.DecimalField("Tồn tối đa", max_digits=12, decimal_places=3, default=0,
                                    validators=[MinValueValidator(0)])
    # Giá tham chiếu (không bắt buộc). Giá thực tế theo từng lô.
    reference_unit_price = models.DecimalField("Giá tham chiếu/đơn vị", max_digits=14, decimal_places=2,
                                               null=True, blank=True)
    is_active = models.BooleanField("Đang sử dụng", default=True)

    class Status(models.TextChoices):
        IN_STOCK = "in_stock", "Đủ hàng"
        LOW_STOCK = "low_stock", "Gần hết"
        OUT_OF_STOCK = "out_of_stock", "Hết hàng"

    status = models.CharField("Tình trạng", max_length=20, choices=Status.choices, default=Status.IN_STOCK)
    last_updated = models.DateField("Cập nhật lần cuối", default=timezone.now)

    class Meta:
        verbose_name = "Nguyên liệu"
        verbose_name_plural = "Nguyên liệu"

    def __str__(self):
        return self.name

    @property
    def current_stock(self):
        # Tổng tồn = tổng (quantity_remaining) của các lô
        agg = self.lots.aggregate(total=models.Sum("quantity_remaining"))
        return agg["total"] or 0


class InventoryLot(models.Model):
    """
    Lô nhập – để quản lý hạn dùng & giá theo lô (phù hợp mẫu có expiryDate).
    Nếu bạn muốn đơn giản, có thể bỏ Lot và giữ số lượng ngay trên Ingredient.
    """
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, related_name="lots", verbose_name="Nguyên liệu"
    )
    supplier = models.ForeignKey(
        Supplier, on_delete=models.SET_NULL, null=True, blank=True, related_name="lots", verbose_name="Nhà cung cấp"
    )
    quantity_received = models.DecimalField("Số lượng nhập", max_digits=12, decimal_places=3,
                                            validators=[MinValueValidator(0)])
    quantity_remaining = models.DecimalField(
        "Số lượng còn lại",
        max_digits=12,
        decimal_places=3,
        validators=[MinValueValidator(0)],
        null=True, blank=True   # 👈 thêm vào
    )
    unit_price = models.DecimalField("Đơn giá", max_digits=14, decimal_places=2)  # giá/đơn vị
    received_date = models.DateField("Ngày nhập", default=timezone.now)
    expiry_date = models.DateField("Hạn dùng", null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["expiry_date"]),
            models.Index(fields=["received_date"]),
        ]
        verbose_name = "Lô nhập kho"
        verbose_name_plural = "Lô nhập kho"

    def __str__(self):
        return f"{self.ingredient.name} - {self.received_date} ({self.quantity_remaining}/{self.quantity_received})"

    def save(self, *args, **kwargs):
        # Nếu là bản ghi mới và chưa nhập remaining, gán bằng received
        if self._state.adding and not self.quantity_remaining:
            self.quantity_remaining = self.quantity_received
        super().save(*args, **kwargs)
