# app_inventory/admin.py
from django.contrib import admin
from .models import Supplier, Ingredient, InventoryLot


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


@admin.register(InventoryLot)
class InventoryLotAdmin(admin.ModelAdmin):
    list_display = (
        "ingredient",
        "supplier",
        "quantity_received",
        "quantity_remaining",
        "unit_price",
        "received_date",
        "expiry_date",
    )
    list_filter = ("ingredient", "supplier", "expiry_date", "received_date")
    search_fields = ("ingredient__name", "supplier__name")
    ordering = ("-received_date",)
