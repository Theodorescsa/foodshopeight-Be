# app_menu/views.py
from django.db.models import Q
from rest_framework import viewsets, permissions
from drf_spectacular.utils import (
    extend_schema, extend_schema_view, OpenApiParameter, OpenApiTypes
)

from app_home.pagination import CustomPagination
from .models import MenuItem, RecipeItem
from .serializers import MenuItemSerializer, RecipeItemSerializer

class CommonViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomPagination


# -------------------- MENU ITEM --------------------
@extend_schema(tags=["app_menu"])
@extend_schema_view(
    list=extend_schema(
        summary="Danh sách món ăn/đồ uống",
        parameters=[
            OpenApiParameter("category", OpenApiTypes.INT, OpenApiParameter.QUERY,
                             description="Lọc theo id danh mục menu"),
            OpenApiParameter("available", OpenApiTypes.BOOL, OpenApiParameter.QUERY,
                             description="true/false"),
            OpenApiParameter("price_gte", OpenApiTypes.NUMBER, OpenApiParameter.QUERY,
                             description="Giá >= số này"),
            OpenApiParameter("price_lte", OpenApiTypes.NUMBER, OpenApiParameter.QUERY,
                             description="Giá <= số này"),
            OpenApiParameter("search", OpenApiTypes.STR, OpenApiParameter.QUERY,
                             description="Tìm theo tên/ mô tả"),
            OpenApiParameter("ordering", OpenApiTypes.STR, OpenApiParameter.QUERY,
                             description="Ví dụ: 'category__name', 'price', '-name' hoặc chuỗi 'a,b'"),
        ],
    ),
    retrieve=extend_schema(summary="Chi tiết món"),
    create=extend_schema(summary="Tạo món"),
    update=extend_schema(summary="Cập nhật món (PUT)"),
    partial_update=extend_schema(summary="Cập nhật món (PATCH)"),
    destroy=extend_schema(summary="Xoá món"),
)
class MenuItemViewSet(CommonViewSet):
    serializer_class = MenuItemSerializer

    def get_queryset(self):
        qs = (
            MenuItem.objects
            .select_related("category")
            .prefetch_related("recipe_items__ingredient")
        )

        params = self.request.query_params
        category_id = params.get("category")
        available = params.get("available")
        price_gte = params.get("price_gte")
        price_lte = params.get("price_lte")
        search = params.get("search")
        ordering = params.get("ordering", "category__name,name")

        if category_id:
            qs = qs.filter(category_id=category_id)
        if available is not None:
            val = str(available).lower() in ("1", "true", "t", "yes", "y")
            qs = qs.filter(available=val)
        if price_gte:
            qs = qs.filter(price__gte=price_gte)
        if price_lte:
            qs = qs.filter(price__lte=price_lte)
        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(description__icontains=search))

        if "," in ordering:
            fields = [f.strip() for f in ordering.split(",") if f.strip()]
            return qs.order_by(*fields)
        return qs.order_by(ordering)


# -------------------- RECIPE ITEM --------------------
@extend_schema(tags=["app_menu"])
@extend_schema_view(
    list=extend_schema(
        summary="Danh sách định lượng nguyên liệu (RecipeItem)",
        parameters=[
            OpenApiParameter("menu_item", OpenApiTypes.INT, OpenApiParameter.QUERY,
                             description="Lọc theo id món"),
            OpenApiParameter("ingredient", OpenApiTypes.INT, OpenApiParameter.QUERY,
                             description="Lọc theo id nguyên liệu"),
            OpenApiParameter("search", OpenApiTypes.STR, OpenApiParameter.QUERY,
                             description="Tìm theo tên món hoặc tên nguyên liệu"),
            OpenApiParameter("ordering", OpenApiTypes.STR, OpenApiParameter.QUERY,
                             description="Ví dụ: 'menu_item__name', 'ingredient__name', '-quantity'"),
        ],
    ),
    retrieve=extend_schema(summary="Chi tiết RecipeItem"),
    create=extend_schema(summary="Tạo RecipeItem"),
    update=extend_schema(summary="Cập nhật RecipeItem (PUT)"),
    partial_update=extend_schema(summary="Cập nhật RecipeItem (PATCH)"),
    destroy=extend_schema(summary="Xoá RecipeItem"),
)
class RecipeItemViewSet(CommonViewSet):
    serializer_class = RecipeItemSerializer

    def get_queryset(self):
        qs = RecipeItem.objects.select_related("menu_item", "ingredient")
        params = self.request.query_params
        menu_item_id = params.get("menu_item")
        ingredient_id = params.get("ingredient")
        search = params.get("search")
        ordering = params.get("ordering", "menu_item__name,ingredient__name")

        if menu_item_id:
            qs = qs.filter(menu_item_id=menu_item_id)
        if ingredient_id:
            qs = qs.filter(ingredient_id=ingredient_id)
        if search:
            qs = qs.filter(
                Q(menu_item__name__icontains=search) |
                Q(ingredient__name__icontains=search)
            )

        if "," in ordering:
            fields = [f.strip() for f in ordering.split(",") if f.strip()]
            return qs.order_by(*fields)
        return qs.order_by(ordering)
