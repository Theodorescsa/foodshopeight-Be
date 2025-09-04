# app_hr/admin.py
from django.contrib import admin
from .models import StaffProfile, StaffStatus


@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "email",
        "phone",
        "position",
        "department",
        "status",
        "salary",
        "start_date",
        "performance",
        "shifts_this_month",
        "total_hours",
    )
    list_filter = ("status", "department", "position")
    search_fields = ("full_name", "email", "phone", "position__name", "department__name")
    ordering = ("full_name",)
    list_editable = ("status", "salary", "performance")
    readonly_fields = ("avatar_preview",)

    fieldsets = (
        (None, {
            "fields": (
                "user",
                "full_name",
                ("email", "phone"),
                ("department", "position"),
                "status",
                "avatar",
                "avatar_preview",
            )
        }),
        ("Thông tin công việc", {
            "fields": (
                "salary",
                "start_date",
                ("performance", "shifts_this_month", "total_hours"),
            )
        }),
    )

    def avatar_preview(self, obj):
        if obj.avatar:
            return f'<img src="{obj.avatar.url}" style="max-height: 100px;"/>'
        return "(No image)"
    avatar_preview.allow_tags = True
    avatar_preview.short_description = "Ảnh đại diện"
