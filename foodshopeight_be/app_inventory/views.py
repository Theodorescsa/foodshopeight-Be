# app_inventory/views.py
from django.db.models import Q
from rest_framework import viewsets, permissions
from drf_spectacular.utils import (
    extend_schema, extend_schema_view, OpenApiParameter, OpenApiTypes
)

from app_home.pagination import CustomPagination
from .models import Supplier, Ingredient, InventoryLot
from .serializers import SupplierSerializer, IngredientSerializer, InventoryLotSerializer

class CommonViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomPagination


# -------------------- SUPPLIER --------------------
@extend_schema(tags=["app_inventory"])
@extend_schema_view(
    list=extend_schema(
        summary="Danh sách nhà cung cấp",
        parameters=[
            OpenApiParameter("search", OpenApiTypes.STR, OpenApiParameter.QUERY,
                             description="Tìm theo tên NCC / người liên hệ / SĐT / email"),
            OpenApiParameter("ordering", OpenApiTypes.STR, OpenApiParameter.QUERY,
                             description="Ví dụ: 'name', '-name'"),
        ],
    ),
    retrieve=extend_schema(summary="Chi tiết nhà cung cấp"),
    create=extend_schema(summary="Tạo nhà cung cấp"),
    update=extend_schema(summary="Cập nhật nhà cung cấp (PUT)"),
    partial_update=extend_schema(summary="Cập nhật nhà cung cấp (PATCH)"),
    destroy=extend_schema(summary="Xoá nhà cung cấp"),
)
class SupplierViewSet(CommonViewSet):
    serializer_class = SupplierSerializer

    def get_queryset(self):
        qs = Supplier.objects.all()
        params = self.request.query_params
        search = params.get("search")
        ordering = params.get("ordering", "name")
        if search:
            qs = qs.filter(
                Q(name__icontains=search) |
                Q(contact_name__icontains=search) |
                Q(phone__icontains=search) |
                Q(email__icontains=search)
            )
        return qs.order_by(ordering)


# -------------------- INGREDIENT --------------------
@extend_schema(tags=["app_inventory"])
@extend_schema_view(
    list=extend_schema(
        summary="Danh sách nguyên liệu",
        parameters=[
            OpenApiParameter("category", OpenApiTypes.INT, OpenApiParameter.QUERY,
                             description="Lọc theo id danh mục nguyên liệu"),
            OpenApiParameter("unit", OpenApiTypes.INT, OpenApiParameter.QUERY,
                             description="Lọc theo id đơn vị"),
            OpenApiParameter("status", OpenApiTypes.STR, OpenApiParameter.QUERY,
                             description="in_stock/low_stock/out_of_stock"),
            OpenApiParameter("is_active", OpenApiTypes.BOOL, OpenApiParameter.QUERY,
                             description="true/false"),
            OpenApiParameter("search", OpenApiTypes.STR, OpenApiParameter.QUERY,
                             description="Tìm theo tên/ tên danh mục"),
            OpenApiParameter("ordering", OpenApiTypes.STR, OpenApiParameter.QUERY,
                             description="Ví dụ: 'name', 'last_updated', '-status'"),
        ],
    ),
    retrieve=extend_schema(summary="Chi tiết nguyên liệu"),
    create=extend_schema(summary="Tạo nguyên liệu"),
    update=extend_schema(summary="Cập nhật nguyên liệu (PUT)"),
    partial_update=extend_schema(summary="Cập nhật nguyên liệu (PATCH)"),
    destroy=extend_schema(summary="Xoá nguyên liệu"),
)
class IngredientViewSet(CommonViewSet):
    serializer_class = IngredientSerializer

    def get_queryset(self):
        qs = Ingredient.objects.select_related("category", "unit")
        params = self.request.query_params
        category_id = params.get("category")
        unit_id = params.get("unit")
        status_val = params.get("status")
        is_active = params.get("is_active")
        search = params.get("search")
        ordering = params.get("ordering", "name")

        if category_id:
            qs = qs.filter(category_id=category_id)
        if unit_id:
            qs = qs.filter(unit_id=unit_id)
        if status_val:
            qs = qs.filter(status=status_val)
        if is_active is not None:
            val = str(is_active).lower() in ("1", "true", "t", "yes", "y")
            qs = qs.filter(is_active=val)
        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(category__name__icontains=search))

        if "," in ordering:
            fields = [f.strip() for f in ordering.split(",") if f.strip()]
            return qs.order_by(*fields)
        return qs.order_by(ordering)


# -------------------- INVENTORY LOT --------------------
@extend_schema(tags=["app_inventory"])
@extend_schema_view(
    list=extend_schema(
        summary="Danh sách lô hàng (InventoryLot)",
        parameters=[
            OpenApiParameter("ingredient", OpenApiTypes.INT, OpenApiParameter.QUERY,
                             description="Lọc theo id nguyên liệu"),
            OpenApiParameter("supplier", OpenApiTypes.INT, OpenApiParameter.QUERY,
                             description="Lọc theo id nhà cung cấp"),
            OpenApiParameter("received_from", OpenApiTypes.DATE, OpenApiParameter.QUERY,
                             description="Lọc received_date >= ngày (YYYY-MM-DD)"),
            OpenApiParameter("received_to", OpenApiTypes.DATE, OpenApiParameter.QUERY,
                             description="Lọc received_date <= ngày (YYYY-MM-DD)"),
            OpenApiParameter("expiry_from", OpenApiTypes.DATE, OpenApiParameter.QUERY,
                             description="Lọc expiry_date >= ngày"),
            OpenApiParameter("expiry_to", OpenApiTypes.DATE, OpenApiParameter.QUERY,
                             description="Lọc expiry_date <= ngày"),
            OpenApiParameter("ordering", OpenApiTypes.STR, OpenApiParameter.QUERY,
                             description="Ví dụ: 'expiry_date', 'received_date', '-quantity_remaining'"),
        ],
    ),
    retrieve=extend_schema(summary="Chi tiết lô hàng"),
    create=extend_schema(summary="Tạo lô hàng"),
    update=extend_schema(summary="Cập nhật lô hàng (PUT)"),
    partial_update=extend_schema(summary="Cập nhật lô hàng (PATCH)"),
    destroy=extend_schema(summary="Xoá lô hàng"),
)
class InventoryLotViewSet(CommonViewSet):
    serializer_class = InventoryLotSerializer

    def get_queryset(self):
        qs = InventoryLot.objects.select_related("ingredient", "supplier")
        params = self.request.query_params
        ingredient_id = params.get("ingredient")
        supplier_id = params.get("supplier")
        received_from = params.get("received_from")
        received_to = params.get("received_to")
        expiry_from = params.get("expiry_from")
        expiry_to = params.get("expiry_to")
        ordering = params.get("ordering", "expiry_date,received_date")

        if ingredient_id:
            qs = qs.filter(ingredient_id=ingredient_id)
        if supplier_id:
            qs = qs.filter(supplier_id=supplier_id)
        if received_from:
            qs = qs.filter(received_date__gte=received_from)
        if received_to:
            qs = qs.filter(received_date__lte=received_to)
        if expiry_from:
            qs = qs.filter(expiry_date__gte=expiry_from)
        if expiry_to:
            qs = qs.filter(expiry_date__lte=expiry_to)

        if "," in ordering:
            fields = [f.strip() for f in ordering.split(",") if f.strip()]
            return qs.order_by(*fields)
        return qs.order_by(ordering)
