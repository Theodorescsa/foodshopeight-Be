from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from app_home.models import Unit, IngredientCategory

class Supplier(models.Model):
    name = models.CharField(max_length=255, unique=True)  # "Công ty Thịt Sạch ABC"
    contact_name = models.CharField(max_length=255, blank=True, default="")
    phone = models.CharField(max_length=50, blank=True, default="")
    email = models.EmailField(blank=True, default="")
    address = models.CharField(max_length=255, blank=True, default="")
    note = models.TextField(blank=True, default="")

    def __str__(self):
        return self.name

class Ingredient(models.Model):
    """
    Nguyên liệu master (ví dụ: Thịt bò, Gạo tẻ, Rau xanh, Nước mắm, Cà phê).
    current_stock sẽ được tính từ các lô (InventoryLot) hoặc có thể lưu cached.
    """
    name = models.CharField(max_length=255, unique=True)
    category = models.ForeignKey(IngredientCategory, on_delete=models.PROTECT, related_name="ingredients")
    unit = models.ForeignKey(Unit, on_delete=models.PROTECT, related_name="ingredients")
    min_stock = models.DecimalField(max_digits=12, decimal_places=3, default=0, validators=[MinValueValidator(0)])
    max_stock = models.DecimalField(max_digits=12, decimal_places=3, default=0, validators=[MinValueValidator(0)])
    # Giá tham chiếu (không bắt buộc). Giá thực tế theo từng lô.
    reference_unit_price = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Status(models.TextChoices):
        IN_STOCK = "in_stock", "Đủ hàng"
        LOW_STOCK = "low_stock", "Gần hết"
        OUT_OF_STOCK = "out_of_stock", "Hết hàng"

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.IN_STOCK)
    last_updated = models.DateField(default=timezone.now)

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
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name="lots")
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, related_name="lots")
    quantity_received = models.DecimalField(max_digits=12, decimal_places=3, validators=[MinValueValidator(0)])
    quantity_remaining = models.DecimalField(max_digits=12, decimal_places=3, validators=[MinValueValidator(0)])
    unit_price = models.DecimalField(max_digits=14, decimal_places=2)  # giá/đơn vị
    received_date = models.DateField(default=timezone.now)
    expiry_date = models.DateField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["expiry_date"]),
            models.Index(fields=["received_date"]),
        ]

    def __str__(self):
        return f"{self.ingredient.name} - {self.received_date} ({self.quantity_remaining}/{self.quantity_received})"
