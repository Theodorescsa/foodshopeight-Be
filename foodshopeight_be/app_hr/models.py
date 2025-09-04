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
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="staff_profile", null=True, blank=True)
    full_name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, default="")
    phone = models.CharField(max_length=50, blank=True, default="")
    position = models.ForeignKey(Position, on_delete=models.SET_NULL, null=True, blank=True, related_name="staffs")
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name="staffs")

    salary = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(0)], default=0)
    start_date = models.DateField(null=True, blank=True)

    status = models.CharField(max_length=20, choices=StaffStatus.choices, default=StaffStatus.ACTIVE)
    performance = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])  # 0..100
    shifts_this_month = models.PositiveIntegerField(default=0)
    total_hours = models.PositiveIntegerField(default=0)  # tổng giờ (tuỳ bạn chuyển sang timesheet chi tiết sau)

    avatar = models.ImageField(upload_to="staff/", null=True, blank=True)

    def __str__(self):
        return self.full_name
