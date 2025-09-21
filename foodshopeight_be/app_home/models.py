from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User

class UserProxy(User):
    class Meta:
        proxy = True
        verbose_name = "Danh sách nhân viên"
        verbose_name_plural = "Danh sách nhân viên"

class Unit(models.Model):
    """Đơn vị đo: kg, chai, ly, ..."""
    code = models.CharField("Mã đơn vị", max_length=50, unique=True)  # 'kg', 'chai'
    name = models.CharField("Tên đơn vị", max_length=100)             # 'Kilogram', 'Chai'

    class Meta:
        verbose_name = "Đơn vị đo"
        verbose_name_plural = "Đơn vị đo"

    def __str__(self):
        return self.code

class IngredientCategory(models.Model):
    """Danh mục nguyên liệu: Thịt, Ngũ cốc, Rau củ, Gia vị, Đồ uống..."""
    name = models.CharField("Tên danh mục", max_length=100, unique=True)

    class Meta:
        verbose_name = "Danh mục nguyên liệu"
        verbose_name_plural = "Danh mục nguyên liệu"

    def __str__(self):
        return self.name

class MenuCategory(models.Model):
    """Danh mục menu: Món chính, Món phụ, Đồ uống, Tráng miệng"""
    name = models.CharField("Tên danh mục", max_length=100, unique=True)
    sort_order = models.PositiveIntegerField("Thứ tự sắp xếp", default=0)

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name = "Danh mục menu"
        verbose_name_plural = "Danh mục menu"

    def __str__(self):
        return self.name

class Department(models.Model):
    """Phòng ban: Bếp, Phục vụ, Thu ngân, Quản lý, Bảo vệ, Tạp vụ"""
    name = models.CharField("Tên phòng ban", max_length=100, unique=True)

    class Meta:
        verbose_name = "Phòng ban"
        verbose_name_plural = "Phòng ban"

    def __str__(self):
        return self.name

class Position(models.Model):
    """Chức danh/Vị trí: Đầu bếp, Phục vụ, Thu ngân, Quản lý ca..."""
    name = models.CharField("Tên chức danh", max_length=100, unique=True)
    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name="positions",
        null=True,
        blank=True,
        verbose_name="Phòng ban"
    )

    class Meta:
        verbose_name = "Chức danh"
        verbose_name_plural = "Chức danh"

    def __str__(self):
        return self.name

class DiningTable(models.Model):
    """Bàn ăn trong nhà hàng (dùng cho dine-in)"""
    name = models.CharField("Tên bàn", max_length=50, unique=True)  # Ví dụ: "Bàn 5"

    class Meta:
        verbose_name = "Bàn ăn"
        verbose_name_plural = "Bàn ăn"

    def __str__(self):
        return self.name

class AppSetting(models.Model):
    """Một vài tham số chung (VAT mặc định, tiền tệ, ...)"""
    vat_percent = models.DecimalField(
        "VAT mặc định (%)",
        max_digits=5,
        decimal_places=2,
        default=10.00,
        validators=[MinValueValidator(0)]
    )
    currency = models.CharField("Tiền tệ", max_length=10, default="VND")

    class Meta:
        verbose_name = "Thiết lập ứng dụng"
        verbose_name_plural = "Thiết lập ứng dụng"

    def __str__(self):
        return f"VAT {self.vat_percent}% - {self.currency}"
