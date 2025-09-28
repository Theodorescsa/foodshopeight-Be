from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import (
    Unit, IngredientCategory, MenuCategory,
    Department, Position, DiningTable, AppSetting
)
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token["username"] = user.username
        return token

class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = ["id", "code", "name"]
        extra_kwargs = {
            "code": {"help_text": "Mã đơn vị: ví dụ 'kg', 'chai'"},
            "name": {"help_text": "Tên hiển thị: 'Kilogram', 'Chai'"},
        }


class IngredientCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = IngredientCategory
        fields = ["id", "name"]
        extra_kwargs = {"name": {"help_text": "Tên danh mục nguyên liệu"}}


class MenuCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuCategory
        fields = ["id", "name", "sort_order"]
        extra_kwargs = {
            "name": {"help_text": "Tên danh mục menu"},
            "sort_order": {"help_text": "Thứ tự sắp xếp tăng dần"},
        }


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ["id", "name"]


class PositionSerializer(serializers.ModelSerializer):
    # Trả về cả id department và thông tin chi tiết để tiện UI
    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(), allow_null=True, required=False
    )
    department_detail = DepartmentSerializer(source="department", read_only=True)

    class Meta:
        model = Position
        fields = ["id", "name", "department", "department_detail"]


class DiningTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiningTable
        fields = ["id", "name"]


class AppSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppSetting
        fields = ["id", "vat_percent", "currency"]
        extra_kwargs = {
            "vat_percent": {"help_text": "VAT mặc định (%)"},
            "currency": {"help_text": "Mã tiền tệ, ví dụ: VND"},
        }