# app_home/admin.py
from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin
from .models import (
    Unit, IngredientCategory, MenuCategory,
    Department, Position, DiningTable, AppSetting, UserProxy
)


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ("code", "name")
    search_fields = ("code", "name")
    ordering = ("code",)


@admin.register(IngredientCategory)
class IngredientCategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(MenuCategory)
class MenuCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "sort_order")
    search_fields = ("name",)
    ordering = ("sort_order", "name")
    list_editable = ("sort_order",)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ("name", "department")
    search_fields = ("name", "department__name")
    list_filter = ("department",)
    ordering = ("name",)


@admin.register(DiningTable)
class DiningTableAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(AppSetting)
class AppSettingAdmin(admin.ModelAdmin):
    list_display = ("vat_percent", "currency")
    search_fields = ("currency",)
    ordering = ("currency",)

    def has_add_permission(self, request):
        """Giới hạn chỉ cho phép 1 bản ghi AppSetting."""
        if AppSetting.objects.exists():
            return False
        return super().has_add_permission(request)


# Gỡ model gốc khỏi admin
admin.site.unregister(Group)

