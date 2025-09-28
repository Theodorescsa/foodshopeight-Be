from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from app_home.models import Department, Position

class StaffStatus(models.TextChoices):
    ACTIVE = "active", "Đang làm"
    INACTIVE = "inactive", "Nghỉ việc"
    ON_LEAVE = "on_leave", "Đang nghỉ phép"

class StaffProfile(models.Model):
    """
    Hồ sơ nhân sự. 
    Có thể dùng OneToOneField với auth.User nếu bạn đã có sẵn user đăng nhập.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="staff_profile",
        null=True,
        blank=True,
        verbose_name="Tài khoản người dùng"
    )
    full_name = models.CharField("Họ và tên", max_length=255)
    email = models.EmailField("Email", blank=True, default="")
    phone = models.CharField("Số điện thoại", max_length=50, blank=True, default="")
    position = models.ForeignKey(
        Position,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="staffs",
        verbose_name="Chức danh"
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="staffs",
        verbose_name="Phòng ban"
    )

    salary = models.DecimalField("Lương cơ bản", max_digits=14, decimal_places=2, validators=[MinValueValidator(0)], default=0)
    start_date = models.DateField("Ngày bắt đầu", null=True, blank=True)

    status = models.CharField("Trạng thái", max_length=20, choices=StaffStatus.choices, default=StaffStatus.ACTIVE)
    performance = models.PositiveIntegerField(
        "Hiệu suất (0–100)",
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    shifts_this_month = models.PositiveIntegerField("Số ca trong tháng", default=0)
    total_hours = models.PositiveIntegerField("Tổng giờ làm", default=0)

    avatar = models.ImageField("Ảnh đại diện", upload_to="staff/", null=True, blank=True)

    class Meta:
        verbose_name = "Hồ sơ nhân sự"
        verbose_name_plural = "Hồ sơ nhân sự"

    def __str__(self):
        return self.full_name
