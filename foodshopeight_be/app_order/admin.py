# app_order/admin.py
from django.contrib import admin
from .models import Order, OrderItem, Payment


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    autocomplete_fields = ("menu_item",)


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_number",
        "customer_name",
        "order_type",
        "order_status",
        "payment_status",
        "subtotal",
        "total",
        "created_at",
        "completed_at",
    )
    list_filter = ("order_status", "payment_status", "order_type", "created_at")
    search_fields = ("order_number", "customer_name", "customer_phone", "staff_name")
    ordering = ("-created_at",)
    inlines = [OrderItemInline, PaymentInline]
    readonly_fields = ("created_at", "completed_at")

    fieldsets = (
        (None, {
            "fields": (
                "order_number",
                ("customer_name", "customer_phone"),
                ("order_type", "table"),
                "notes",
                "staff_name",
            )
        }),
        ("Tài chính", {
            "fields": (
                "subtotal",
                "tax",
                "discount",
                "total",
            )
        }),
        ("Trạng thái", {
            "fields": (
                "order_status",
                "payment_status",
                ("created_at", "completed_at"),
            )
        }),
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "menu_item", "name", "unit_price", "quantity", "total")
    search_fields = ("order__order_number", "menu_item__name", "name")
    list_filter = ("order",)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("order", "method", "amount", "paid_at", "note")
    list_filter = ("method", "paid_at")
    search_fields = ("order__order_number", "note")
    ordering = ("-paid_at",)
