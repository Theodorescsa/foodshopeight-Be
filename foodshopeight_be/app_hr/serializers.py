# app_hr/serializers.py
from rest_framework import serializers
from django.conf import settings
from django.contrib.auth import get_user_model

from app_home.models import Department, Position
from app_home.serializers import DepartmentSerializer, PositionSerializer  # tái dùng nested serializer đẹp sẵn có
from .models import StaffProfile, StaffStatus

User = get_user_model()

class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name")


class StaffProfileSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), allow_null=True, required=False
    )
    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(), allow_null=True, required=False
    )
    position = serializers.PrimaryKeyRelatedField(
        queryset=Position.objects.all(), allow_null=True, required=False
    )

    user_detail = SimpleUserSerializer(source="user", read_only=True)
    department_detail = DepartmentSerializer(source="department", read_only=True)
    position_detail = PositionSerializer(source="position", read_only=True)

    avatar_url = serializers.SerializerMethodField(read_only=True)

    status = serializers.ChoiceField(choices=StaffStatus.choices)

    class Meta:
        model = StaffProfile
        fields = [
            "id",
            # core
            "user", "user_detail",
            "full_name", "email", "phone",
            "department", "department_detail",
            "position", "position_detail",
            # work info
            "salary", "start_date",
            "status", "performance",
            "shifts_this_month", "total_hours",
            # media
            "avatar", "avatar_url",
        ]
        extra_kwargs = {
            "full_name": {"help_text": "Họ tên nhân sự"},
            "email": {"help_text": "Email liên hệ"},
            "phone": {"help_text": "Số điện thoại"},
            "salary": {"help_text": "Lương cơ bản (VND)"},
            "start_date": {"help_text": "Ngày bắt đầu làm việc (YYYY-MM-DD)"},
            "status": {"help_text": "Trạng thái làm việc"},
            "performance": {"help_text": "Điểm hiệu suất 0..100"},
            "shifts_this_month": {"help_text": "Số ca trong tháng"},
            "total_hours": {"help_text": "Tổng giờ làm tích lũy"},
            "avatar": {"help_text": "Ảnh đại diện (ImageField)"},
        }

    def get_avatar_url(self, obj):
        request = self.context.get("request")
        if obj.avatar and hasattr(obj.avatar, "url"):
            url = obj.avatar.url
            return request.build_absolute_uri(url) if request else url
        return None

    def validate_performance(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError("performance phải trong khoảng 0..100")
        return value
