from django.db import models
from django.core.validators import MinValueValidator

class Unit(models.Model):
    """Đơn vị đo: kg, chai, ly, ..."""
    code = models.CharField(max_length=50, unique=True)  # 'kg', 'chai'
    name = models.CharField(max_length=100)              # 'Kilogram', 'Chai'

    def __str__(self):
        return self.code

class IngredientCategory(models.Model):
    """Danh mục nguyên liệu: Thịt, Ngũ cốc, Rau củ, Gia vị, Đồ uống..."""
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class MenuCategory(models.Model):
    """Danh mục menu: Món chính, Món phụ, Đồ uống, Tráng miệng"""
    name = models.CharField(max_length=100, unique=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "name"]

    def __str__(self):
        return self.name

class Department(models.Model):
    """Phòng ban: Bếp, Phục vụ, Thu ngân, Quản lý, Bảo vệ, Tạp vụ"""
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Position(models.Model):
    """Chức danh/Vị trí: Đầu bếp, Phục vụ, Thu ngân, Quản lý ca..."""
    name = models.CharField(max_length=100, unique=True)
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name="positions", null=True, blank=True)

    def __str__(self):
        return self.name

class DiningTable(models.Model):
    """Bàn ăn trong nhà hàng (dùng cho dine-in)"""
    name = models.CharField(max_length=50, unique=True)  # Ví dụ: "Bàn 5"

    def __str__(self):
        return self.name

class AppSetting(models.Model):
    """Một vài tham số chung (VAT mặc định, tiền tệ, ...)"""
    vat_percent = models.DecimalField(max_digits=5, decimal_places=2, default=10.00, validators=[MinValueValidator(0)])
    currency = models.CharField(max_length=10, default="VND")

    class Meta:
        verbose_name = "App Setting"
        verbose_name_plural = "App Settings"
