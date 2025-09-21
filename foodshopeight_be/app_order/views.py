from django.db.models import Q, Sum
from rest_framework import viewsets, permissions
from drf_spectacular.utils import (
    extend_schema, extend_schema_view, OpenApiParameter, OpenApiTypes
)

from app_home.pagination import CustomPagination
from .models import Order, OrderItem, Payment
from .serializers import OrderSerializer, OrderItemSerializer, PaymentSerializer


class CommonViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomPagination


# -------------------- ORDER --------------------
@extend_schema(tags=["app_order"])
@extend_schema_view(
    list=extend_schema(
        summary="Danh sách đơn hàng",
        parameters=[
            OpenApiParameter("search", OpenApiTypes.STR, OpenApiParameter.QUERY,
                             description="Tìm theo mã đơn / tên KH / SĐT"),
            OpenApiParameter("order_status", OpenApiTypes.STR, OpenApiParameter.QUERY,
                             description="Trạng thái đơn"),
            OpenApiParameter("payment_status", OpenApiTypes.STR, OpenApiParameter.QUERY,
                             description="Trạng thái thanh toán"),
            OpenApiParameter("order_type", OpenApiTypes.STR, OpenApiParameter.QUERY,
                             description="Hình thức (dine_in/takeaway/delivery)"),
            OpenApiParameter("date_from", OpenApiTypes.DATETIME, OpenApiParameter.QUERY,
                             description="created_at >= (YYYY-MM-DD)"),
            OpenApiParameter("date_to", OpenApiTypes.DATETIME, OpenApiParameter.QUERY,
                             description="created_at <= (YYYY-MM-DD)"),
            OpenApiParameter("min_total", OpenApiTypes.NUMBER, OpenApiParameter.QUERY,
                             description="Lọc total >= min_total"),
            OpenApiParameter("max_total", OpenApiTypes.NUMBER, OpenApiParameter.QUERY,
                             description="Lọc total <= max_total"),
            OpenApiParameter("ordering", OpenApiTypes.STR, OpenApiParameter.QUERY,
                             description="VD: '-created_at', 'customer_name', 'sum_total' (total)"),
        ],
    ),
    retrieve=extend_schema(summary="Chi tiết đơn hàng"),
    create=extend_schema(summary="Tạo đơn hàng"),
    update=extend_schema(summary="Cập nhật đơn hàng (PUT)"),
    partial_update=extend_schema(summary="Cập nhật đơn hàng (PATCH)"),
    destroy=extend_schema(summary="Xoá đơn hàng"),
)
class OrderViewSet(CommonViewSet):
    serializer_class = OrderSerializer

    def get_queryset(self):
        # annotate sum_total để filter/order theo tổng tiền (vì total là property)
        qs = (
            Order.objects
            .select_related("table")
            .prefetch_related("items", "payments")
            .annotate(sum_total=Sum("items__total"))
        )

        p = self.request.query_params
        search = p.get("search")
        order_status = p.get("order_status")
        payment_status = p.get("payment_status")
        order_type = p.get("order_type")
        date_from = p.get("date_from")
        date_to = p.get("date_to")
        min_total = p.get("min_total")
        max_total = p.get("max_total")
        ordering = p.get("ordering", "-created_at")

        if search:
            qs = qs.filter(
                Q(order_number__icontains=search) |
                Q(customer_name__icontains=search) |
                Q(customer_phone__icontains=search)
            )
        if order_status:
            qs = qs.filter(order_status=order_status)
        if payment_status:
            qs = qs.filter(payment_status=payment_status)
        if order_type:
            qs = qs.filter(order_type=order_type)
        if date_from:
            qs = qs.filter(created_at__gte=date_from)
        if date_to:
            qs = qs.filter(created_at__lte=date_to)
        if min_total:
            qs = qs.filter(sum_total__gte=min_total)
        if max_total:
            qs = qs.filter(sum_total__lte=max_total)

        # hỗ trợ nhiều field ordering
        if "," in ordering:
            fields = [f.strip() for f in ordering.split(",") if f.strip()]
            return qs.order_by(*fields)

        # cho phép order theo 'sum_total' như 'total'
        if ordering in ("total", "-total"):
            ordering = ordering.replace("total", "sum_total")

        return qs.order_by(ordering)


# -------------------- ORDER ITEM --------------------
@extend_schema(tags=["app_order"])
@extend_schema_view(
    list=extend_schema(summary="Danh sách dòng hàng"),
    retrieve=extend_schema(summary="Chi tiết dòng hàng"),
    create=extend_schema(summary="Thêm dòng hàng"),
    update=extend_schema(summary="Cập nhật dòng hàng (PUT)"),
    partial_update=extend_schema(summary="Cập nhật dòng hàng (PATCH)"),
    destroy=extend_schema(summary="Xoá dòng hàng"),
)
class OrderItemViewSet(CommonViewSet):
    serializer_class = OrderItemSerializer

    def get_queryset(self):
        qs = OrderItem.objects.select_related("order", "menu_item")
        order_id = self.request.query_params.get("order")
        if order_id:
            qs = qs.filter(order_id=order_id)
        ordering = self.request.query_params.get("ordering", "-id")
        if "," in ordering:
            fields = [f.strip() for f in ordering.split(",") if f.strip()]
            return qs.order_by(*fields)
        return qs.order_by(ordering)


# -------------------- PAYMENT --------------------
@extend_schema(tags=["app_order"])
@extend_schema_view(
    list=extend_schema(summary="Danh sách thanh toán"),
    retrieve=extend_schema(summary="Chi tiết thanh toán"),
    create=extend_schema(summary="Tạo thanh toán"),
    update=extend_schema(summary="Cập nhật thanh toán (PUT)"),
    partial_update=extend_schema(summary="Cập nhật thanh toán (PATCH)"),
    destroy=extend_schema(summary="Xoá thanh toán"),
)
class PaymentViewSet(CommonViewSet):
    serializer_class = PaymentSerializer

    def get_queryset(self):
        qs = Payment.objects.select_related("order")
        order_id = self.request.query_params.get("order")
        if order_id:
            qs = qs.filter(order_id=order_id)
        method = self.request.query_params.get("method")
        if method:
            qs = qs.filter(method=method)
        date_from = self.request.query_params.get("date_from")
        date_to = self.request.query_params.get("date_to")
        if date_from:
            qs = qs.filter(paid_at__gte=date_from)
        if date_to:
            qs = qs.filter(paid_at__lte=date_to)
        ordering = self.request.query_params.get("ordering", "-paid_at")
        if "," in ordering:
            fields = [f.strip() for f in ordering.split(",") if f.strip()]
            return qs.order_by(*fields)
        return qs.order_by(ordering)
