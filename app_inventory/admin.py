# app_inventory/admin.py
from django.contrib import admin
from .models import Supplier, Ingredient, InventoryLot
from django import forms


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("name", "contact_name", "phone", "email")
    search_fields = ("name", "contact_name", "phone", "email")
    ordering = ("name",)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "unit",
        "min_stock",
        "max_stock",
        "current_stock_display",
        "status",
        "last_updated",
    )
    list_filter = ("category", "status", "unit")
    search_fields = ("name", "category__name")
    ordering = ("name",)
    list_editable = ("min_stock", "max_stock", "status")
    readonly_fields = ("current_stock_display",)

    fieldsets = (
        (None, {
            "fields": (
                "name",
                ("category", "unit"),
                ("min_stock", "max_stock"),
                ("reference_unit_price", "status"),
                "last_updated",
            )
        }),
    )

    def current_stock_display(self, obj):
        return obj.current_stock
    current_stock_display.short_description = "Tồn kho hiện tại"


class InventoryLotForm(forms.ModelForm):
    class Meta:
        model = InventoryLot
        fields = "__all__"
        widgets = {
            "quantity_received": forms.NumberInput(attrs={"step": "1"}),   # 👉 tăng theo 0.1
            "quantity_remaining": forms.NumberInput(attrs={"step": "1"}),
            "unit_price": forms.NumberInput(attrs={"step": "1000"}),         # ví dụ: nhảy 1000/đơn
        }

@admin.register(InventoryLot)
class InventoryLotAdmin(admin.ModelAdmin):
    form = InventoryLotForm
    list_display = ("ingredient","supplier","quantity_received","quantity_remaining",
                    "unit_price","received_date","expiry_date")