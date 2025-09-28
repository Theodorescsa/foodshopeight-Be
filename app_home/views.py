# app_home/views.py
from django.http import JsonResponse
from rest_framework import viewsets, permissions
from drf_spectacular.utils import (
    extend_schema, OpenApiParameter, OpenApiTypes, extend_schema_view
)
from django.db.models import Q

from .pagination import CustomPagination
from .models import (
    Unit, IngredientCategory, MenuCategory,
    Department, Position, DiningTable, AppSetting
)
from .serializers import (
    CustomTokenObtainPairSerializer, UnitSerializer, IngredientCategorySerializer, MenuCategorySerializer,
    DepartmentSerializer, PositionSerializer, DiningTableSerializer, AppSettingSerializer
)
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiTypes
from rest_framework import viewsets
from django.contrib.auth.models import User
from django.db.models import Q

from .serializers import CustomTokenObtainPairSerializer
from .pagination import CustomPagination
from .docs import *

# Create your views here.
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    @extend_schema(tags=["app_home"])
    @custom_token_obtain_pair_view_schema()
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            return Response(
                {"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )
        user = User.objects.get(username=request.data['username'])
        user_serializer = UserRegistrationSerializer(user, fields=('id', 'username', 'email', 'first_name', 'last_name'))
        # Lấy userProfile từ user
        user_profile = UserProfile.objects.get(user=user)
        positions = user_profile.positions.all()
        positions = PositionSerializer(positions, many=True, fields=( 'title',))

        response_data = {
            "refresh": serializer.validated_data["refresh"],
            "access": serializer.validated_data["access"],
            "user": user_serializer.data,
            "positions": positions.data
        }

        return Response(response_data, status=status.HTTP_200_OK)

# ---- Base ViewSet: chỉ định quyền + phân trang tuỳ biến ----
class CommonViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]   # đổi IsAdminUser nếu cần
    pagination_class = CustomPagination                   # <-- dùng CustomPagination của bạn


# -------------------- UNIT --------------------
@extend_schema(tags=["app_home"])
@extend_schema_view(
    list=extend_schema(summary="Danh sách đơn vị", description="Liệt kê + tìm kiếm theo code/name."),
    retrieve=extend_schema(summary="Chi tiết đơn vị"),
    create=extend_schema(summary="Tạo đơn vị"),
    update=extend_schema(summary="Cập nhật đơn vị (PUT)"),
    partial_update=extend_schema(summary="Cập nhật đơn vị (PATCH)"),
    destroy=extend_schema(summary="Xoá đơn vị"),
)
class UnitViewSet(CommonViewSet):
    serializer_class = UnitSerializer

    def get_queryset(self):
        qs = Unit.objects.all()
        search = self.request.query_params.get("search")
        ordering = self.request.query_params.get("ordering", "code")
        if search:
            qs = qs.filter(Q(code__icontains=search) | Q(name__icontains=search))
        return qs.order_by(ordering)


# -------------------- INGREDIENT CATEGORY --------------------
@extend_schema(tags=["app_home"])
@extend_schema_view(
    list=extend_schema(summary="Danh sách danh mục nguyên liệu"),
    retrieve=extend_schema(summary="Chi tiết danh mục nguyên liệu"),
    create=extend_schema(summary="Tạo danh mục nguyên liệu"),
    update=extend_schema(summary="Cập nhật danh mục nguyên liệu (PUT)"),
    partial_update=extend_schema(summary="Cập nhật danh mục nguyên liệu (PATCH)"),
    destroy=extend_schema(summary="Xoá danh mục nguyên liệu"),
)
class IngredientCategoryViewSet(CommonViewSet):
    serializer_class = IngredientCategorySerializer

    def get_queryset(self):
        qs = IngredientCategory.objects.all()
        search = self.request.query_params.get("search")
        ordering = self.request.query_params.get("ordering", "name")
        if search:
            qs = qs.filter(name__icontains=search)
        return qs.order_by(ordering)


# -------------------- MENU CATEGORY --------------------
@extend_schema(tags=["app_home"])
@extend_schema_view(
    list=extend_schema(
        summary="Danh sách danh mục menu",
        parameters=[
            OpenApiParameter("ordering", OpenApiTypes.STR, OpenApiParameter.QUERY,
                             description="Sắp xếp: 'sort_order', '-sort_order', 'name', ..."),
            OpenApiParameter("search", OpenApiTypes.STR, OpenApiParameter.QUERY,
                             description="Tìm theo tên danh mục"),
        ],
    ),
    retrieve=extend_schema(summary="Chi tiết danh mục menu"),
    create=extend_schema(summary="Tạo danh mục menu"),
    update=extend_schema(summary="Cập nhật danh mục menu (PUT)"),
    partial_update=extend_schema(summary="Cập nhật danh mục menu (PATCH)"),
    destroy=extend_schema(summary="Xoá danh mục menu"),
)
class MenuCategoryViewSet(CommonViewSet):
    serializer_class = MenuCategorySerializer

    def get_queryset(self):
        qs = MenuCategory.objects.all()
        search = self.request.query_params.get("search")
        ordering = self.request.query_params.get("ordering", "sort_order,name")
        if search:
            qs = qs.filter(name__icontains=search)
        # Hỗ trợ chuỗi nhiều trường "a,b"
        if "," in ordering:
            fields = [f.strip() for f in ordering.split(",") if f.strip()]
            return qs.order_by(*fields)
        return qs.order_by(ordering)


# -------------------- DEPARTMENT --------------------
@extend_schema(tags=["app_home"])
@extend_schema_view(
    list=extend_schema(summary="Danh sách phòng ban"),
    retrieve=extend_schema(summary="Chi tiết phòng ban"),
    create=extend_schema(summary="Tạo phòng ban"),
    update=extend_schema(summary="Cập nhật phòng ban (PUT)"),
    partial_update=extend_schema(summary="Cập nhật phòng ban (PATCH)"),
    destroy=extend_schema(summary="Xoá phòng ban"),
)
class DepartmentViewSet(CommonViewSet):
    serializer_class = DepartmentSerializer

    def get_queryset(self):
        qs = Department.objects.all()
        search = self.request.query_params.get("search")
        ordering = self.request.query_params.get("ordering", "name")
        if search:
            qs = qs.filter(name__icontains=search)
        return qs.order_by(ordering)


# -------------------- POSITION --------------------
@extend_schema(tags=["app_home"])
@extend_schema_view(
    list=extend_schema(
        summary="Danh sách chức danh / vị trí",
        parameters=[
            OpenApiParameter("department", OpenApiTypes.INT, OpenApiParameter.QUERY,
                             description="Lọc theo id phòng ban"),
            OpenApiParameter("search", OpenApiTypes.STR, OpenApiParameter.QUERY,
                             description="Tìm theo tên vị trí hoặc tên phòng ban"),
            OpenApiParameter("ordering", OpenApiTypes.STR, OpenApiParameter.QUERY,
                             description="Sắp xếp: 'name', 'department__name', ..."),
        ],
    ),
    retrieve=extend_schema(summary="Chi tiết vị trí"),
    create=extend_schema(summary="Tạo vị trí"),
    update=extend_schema(summary="Cập nhật vị trí (PUT)"),
    partial_update=extend_schema(summary="Cập nhật vị trí (PATCH)"),
    destroy=extend_schema(summary="Xoá vị trí"),
)
class PositionViewSet(CommonViewSet):
    serializer_class = PositionSerializer

    def get_queryset(self):
        qs = Position.objects.select_related("department")
        search = self.request.query_params.get("search")
        department_id = self.request.query_params.get("department")
        ordering = self.request.query_params.get("ordering", "name")
        if department_id:
            qs = qs.filter(department_id=department_id)
        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(department__name__icontains=search))
        return qs.order_by(ordering)


# -------------------- DINING TABLE --------------------
@extend_schema(tags=["app_home"])
@extend_schema_view(
    list=extend_schema(summary="Danh sách bàn ăn"),
    retrieve=extend_schema(summary="Chi tiết bàn ăn"),
    create=extend_schema(summary="Tạo bàn ăn"),
    update=extend_schema(summary="Cập nhật bàn ăn (PUT)"),
    partial_update=extend_schema(summary="Cập nhật bàn ăn (PATCH)"),
    destroy=extend_schema(summary="Xoá bàn ăn"),
)
class DiningTableViewSet(CommonViewSet):
    serializer_class = DiningTableSerializer

    def get_queryset(self):
        qs = DiningTable.objects.all()
        search = self.request.query_params.get("search")
        ordering = self.request.query_params.get("ordering", "name")
        if search:
            qs = qs.filter(name__icontains=search)
        return qs.order_by(ordering)


# -------------------- APP SETTING --------------------
@extend_schema(tags=["app_home"])
@extend_schema_view(
    list=extend_schema(
        summary="Danh sách App Settings",
        description="Thông thường chỉ có 1 bản ghi.",
        parameters=[
            OpenApiParameter("currency", OpenApiTypes.STR, OpenApiParameter.QUERY,
                             description="Lọc theo mã tiền tệ, vd: VND"),
            OpenApiParameter("ordering", OpenApiTypes.STR, OpenApiParameter.QUERY,
                             description="Sắp xếp: 'vat_percent', '-vat_percent', 'currency', ..."),
        ],
    ),
    retrieve=extend_schema(summary="Chi tiết App Setting"),
    create=extend_schema(summary="Tạo App Setting"),
    update=extend_schema(summary="Cập nhật App Setting (PUT)"),
    partial_update=extend_schema(summary="Cập nhật App Setting (PATCH)"),
    destroy=extend_schema(summary="Xoá App Setting"),
)
class AppSettingViewSet(CommonViewSet):
    serializer_class = AppSettingSerializer

    def get_queryset(self):
        qs = AppSetting.objects.all()
        currency = self.request.query_params.get("currency")
        ordering = self.request.query_params.get("ordering", "id")
        if currency:
            qs = qs.filter(currency__iexact=currency)
        return qs.order_by(ordering)
