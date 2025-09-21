from decimal import Decimal
from collections import defaultdict

from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet
from django.utils import timezone
from django.urls import path
from django.http import JsonResponse
from datetime import timedelta
from django.db.models import Sum, Count, Avg
from django.db.models.functions import TruncDay

# Models trong app_order
from .models import Order, OrderItem, Payment

# Models tham chiếu bên ngoài
from app_menu.models import MenuItem           # để đọc BOM và lấy price
from app_inventory.models import Ingredient    # hoặc đổi sang app bạn đang dùng cho Ingredient

from django.shortcuts import get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def admin_menu_price(request):
    menu_id = request.GET.get("id")
    price = 0
    if menu_id:
        price = MenuItem.objects.filter(pk=menu_id).values_list("price", flat=True).first() or 0
    return JsonResponse({"price": str(price)})
class OrderItemInlineFormSet(BaseInlineFormSet):
    """Cộng dồn nhu cầu nguyên liệu theo tất cả OrderItem rồi so với tồn kho."""
    def clean(self):
        super().clean()
        needs = defaultdict(Decimal)

        for form in self.forms:
            if not hasattr(form, "cleaned_data"):
                continue
            cd = form.cleaned_data
            if not cd or cd.get("DELETE"):
                continue

            mi: MenuItem = cd.get("menu_item")
            qty = Decimal(cd.get("quantity") or 0)
            if not mi or qty <= 0:
                continue

            # Cộng dồn nhu cầu theo BOM của từng món
            for ri in mi.recipe_items.select_related("ingredient").all():
                needs[ri.ingredient_id] += Decimal(ri.quantity or 0) * qty

        if not needs:
            return

        # So với tồn kho
        lack = []
        for ing_id, need in needs.items():
            ing = Ingredient.objects.get(pk=ing_id)
            have = Decimal(ing.current_stock or 0)
            if need > have:
                lack.append(f"{ing.name}: cần {need}, còn {have}")

        if lack:
            raise ValidationError("Thiếu nguyên liệu: " + "; ".join(lack))


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    formset = OrderItemInlineFormSet
    fields = ("menu_item", "quantity", "total")
    readonly_fields = ("total",)

    class Media:
        js = ("admin/orderitem_inline.js",)


    # Tính total theo MenuItem.price vì không còn unit_price snapshot
    def save_new_objects(self, formset, commit=True):
        objs = super().save_new_objects(formset, commit=False)
        for obj in objs:
            if obj.menu_item:
                price = Decimal(obj.menu_item.price or 0)
                obj.total = price * Decimal(obj.quantity or 0)
        if commit:
            for obj in objs:
                obj.save()
        return objs

    def save_existing_objects(self, formset, commit=True):
        objs, _ = super().save_existing_objects(formset, commit=False)
        for obj in objs:
            if obj.menu_item:
                price = Decimal(obj.menu_item.price or 0)
                obj.total = price * Decimal(obj.quantity or 0)
        if commit:
            for obj in objs:
                obj.save()
        return objs, []


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    class Media:
        js = ("admin/order_payment_inline.js",)


# =================
# Admin đăng ký model
# =================
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_number",
        "customer_name",
        "order_type",
        "order_status",
        "payment_status",
        "created_at",
        "completed_at",
    )
    list_filter = ("order_status", "payment_status", "order_type", "created_at")
    search_fields = ("order_number", "customer_name", "customer_phone")  # bỏ staff_name vì model không còn
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

    # Không còn subtotal/total trên Order → không gọi recalc_totals()
    def save_formset(self, request, form, formset, change):
        # Nếu là OrderItem, bạn đã xử lý ở Inline -> cứ save
        if formset.model is OrderItem:
            return super().save_formset(request, form, formset, change)

        if formset.model is Payment:
            instances = formset.save(commit=False)

            # tổng tiền các mặt hàng
            total_items = form.instance.items.aggregate(s=Sum("total"))["s"] or Decimal("0")

            # tổng các payment đã có trong DB (không tính mấy cái đang save tạm)
            paid_existing = form.instance.payments.exclude(pk__in=[obj.pk for obj in instances if obj.pk]).aggregate(
                s=Sum("amount")
            )["s"] or Decimal("0")

            # tổng các payment đang nhập (đã có value)
            paid_inputs = sum([Decimal(obj.amount or 0) for obj in instances])

            remaining = total_items - paid_existing - paid_inputs
            # fill cho những obj có amount rỗng/0
            for obj in instances:
                if not obj.amount or Decimal(obj.amount) == 0:
                    fill = max(remaining, Decimal("0"))
                    obj.amount = fill
                    remaining = Decimal("0")
                obj.save()

            formset.save_m2m()
            return

        # mặc định
        return super().save_formset(request, form, formset, change)
    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path("menu-price/", self.admin_site.admin_view(admin_menu_price), name="order_menu_price"),
        ]
        return custom + urls
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "menu_item", "quantity", "total")
    search_fields = ("order__order_number", "menu_item__name")
    list_filter = ("order",)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("order", "method", "amount", "paid_at", "note")
    list_filter = ("method", "paid_at")
    search_fields = ("order__order_number", "note")
    ordering = ("-paid_at",)


# ========================
# Dashboard JSON cho charts
# ========================
from datetime import timedelta
from django.utils import timezone
from django.db.models.functions import TruncDay, Coalesce, NullIf
from django.db.models import Sum, Avg, Count, F, Value, CharField, Case, When
from django.db.models.functions import TruncDay, Coalesce
@staff_member_required
def dashboard_data(request):
    now = timezone.now()
    start_14d = now - timedelta(days=14)
    start_30d = now - timedelta(days=30)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    # Doanh thu theo ngày (14 ngày)
    rev_qs = (
        Payment.objects.filter(paid_at__gte=start_14d)
        .annotate(d=TruncDay("paid_at"))
        .values("d")
        .annotate(revenue=Sum("amount"))
        .order_by("d")
    )
    rev_labels = [x["d"].strftime("%d/%m") for x in rev_qs]
    rev_values = [float(x["revenue"] or 0) for x in rev_qs]

    # KPI
    revenue_today = Payment.objects.filter(paid_at__gte=today_start).aggregate(s=Sum("amount"))["s"] or 0
    revenue_7d = Payment.objects.filter(paid_at__gte=now - timedelta(days=7)).aggregate(s=Sum("amount"))["s"] or 0
    orders_today = Order.objects.filter(created_at__gte=today_start).count()

    # AOV 30 ngày
    aov_30d = (
        Order.objects.filter(created_at__gte=start_30d)
        .annotate(sum_total=Sum("items__total"))
        .aggregate(avg=Avg("sum_total"))["avg"] or 0
    )

    # Phương thức thanh toán (30 ngày)
    pm_qs = (
        Payment.objects.filter(paid_at__gte=start_30d)
        .values("method")
        .annotate(total=Sum("amount"))
        .order_by("-total")
    )
    method_map = dict(Payment.Method.choices)
    pm_labels = [method_map.get(x["method"], x["method"]) for x in pm_qs]
    pm_values = [float(x["total"] or 0) for x in pm_qs]

    # Top món (30 ngày) — ưu tiên snapshot name, fallback sang tên món hiện tại
    ti_qs = (
        OrderItem.objects.filter(order__created_at__gte=start_30d)
        .annotate(
            name_nonempty=Case(
                When(name__exact="", then=Value(None)),
                default=F("name"),
                output_field=CharField(),
            )
        )
        .annotate(item_name=Coalesce(F("name_nonempty"), F("menu_item__name")))
        .values("item_name")
        .annotate(qty=Sum("quantity"))
        .order_by("-qty")[:10]
    )

    ti_labels = [i["item_name"] or "(N/A)" for i in ti_qs]
    ti_values = [int(i["qty"] or 0) for i in ti_qs]

    # Trạng thái đơn hôm nay
    st_qs = (
        Order.objects.filter(created_at__gte=today_start)
        .values("order_status")
        .annotate(c=Count("id"))
        .order_by("-c")
    )
    st_map = dict(Order.OrderStatus.choices)
    st_labels = [st_map.get(x["order_status"], x["order_status"]) for x in st_qs]
    st_values = [int(x["c"]) for x in st_qs]

    return JsonResponse({
        "revenue_by_day": {"labels": rev_labels, "values": rev_values},
        "kpi": {
            "revenue_today": float(revenue_today),
            "revenue_7d": float(revenue_7d),
            "orders_today": orders_today,
            "aov_30d": float(aov_30d),
        },
        "pay_methods": {"labels": pm_labels, "values": pm_values},
        "top_items": {"labels": ti_labels, "values": ti_values},
        "order_status_today": {"labels": st_labels, "values": st_values},
    })
def menu_item_price_view(request, pk: int):
    mi = get_object_or_404(MenuItem, pk=pk)
    # trả string để khỏi lỗi serialize Decimal
    return JsonResponse({"price": str(mi.price)})


# Đưa endpoint vào namespace admin (yêu cầu login)
def _wrap_urls(get_urls):
    def wrapper():
        my = [
            path("dashboard-data/", admin.site.admin_view(dashboard_data), name="dashboard-data"),
            path("menu-item-price/<int:pk>/", admin.site.admin_view(menu_item_price_view), name="menu-item-price"),
        ]
        return my + get_urls()
    return wrapper

admin.site.get_urls = _wrap_urls(admin.site.get_urls)