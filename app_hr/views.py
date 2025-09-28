# app_hr/views.py
from django.db.models import Q
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from drf_spectacular.utils import (
    extend_schema, extend_schema_view, OpenApiParameter, OpenApiTypes
)

from app_home.pagination import CustomPagination
from app_home.models import Department, Position
from .models import StaffProfile, StaffStatus
from .serializers import StaffProfileSerializer

class CommonViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomPagination


# -------------------- STAFF PROFILE --------------------
@extend_schema(tags=["app_hr"])
@extend_schema_view(
    list=extend_schema(
        summary="Danh sách hồ sơ nhân sự",
        description="Liệt kê + lọc + tìm kiếm hồ sơ nhân sự.",
        parameters=[
            OpenApiParameter("search", OpenApiTypes.STR, OpenApiParameter.QUERY,
                             description="Tìm theo họ tên / email / phone"),
            OpenApiParameter("status", OpenApiTypes.STR, OpenApiParameter.QUERY,
                             description=f"Lọc theo trạng thái: {', '.join([s for s, _ in StaffStatus.choices])}"),
            OpenApiParameter("department", OpenApiTypes.INT, OpenApiParameter.QUERY,
                             description="Lọc theo id phòng ban"),
            OpenApiParameter("position", OpenApiTypes.INT, OpenApiParameter.QUERY,
                             description="Lọc theo id chức vụ"),
            OpenApiParameter("date_from", OpenApiTypes.DATE, OpenApiParameter.QUERY,
                             description="Lọc start_date >= date_from (YYYY-MM-DD)"),
            OpenApiParameter("date_to", OpenApiTypes.DATE, OpenApiParameter.QUERY,
                             description="Lọc start_date <= date_to (YYYY-MM-DD)"),
            OpenApiParameter("ordering", OpenApiTypes.STR, OpenApiParameter.QUERY,
                             description="Ví dụ: 'full_name', '-salary', 'department__name', 'position__name'"),
        ],
    ),
    retrieve=extend_schema(summary="Chi tiết hồ sơ nhân sự"),
    create=extend_schema(summary="Tạo hồ sơ nhân sự"),
    update=extend_schema(summary="Cập nhật hồ sơ nhân sự (PUT)"),
    partial_update=extend_schema(summary="Cập nhật hồ sơ nhân sự (PATCH)"),
    destroy=extend_schema(summary="Xoá hồ sơ nhân sự"),
)
class StaffProfileViewSet(CommonViewSet):
    serializer_class = StaffProfileSerializer

    def get_queryset(self):
        qs = (
            StaffProfile.objects
            .select_related("user", "department", "position")
        )

        # --- filters ---
        params = self.request.query_params
        search = params.get("search")
        status_val = params.get("status")
        department_id = params.get("department")
        position_id = params.get("position")
        date_from = params.get("date_from")
        date_to = params.get("date_to")
        ordering = params.get("ordering", "full_name")

        if search:
            qs = qs.filter(
                Q(full_name__icontains=search) |
                Q(email__icontains=search) |
                Q(phone__icontains=search)
            )
        if status_val:
            qs = qs.filter(status=status_val)
        if department_id:
            qs = qs.filter(department_id=department_id)
        if position_id:
            qs = qs.filter(position_id=position_id)
        if date_from:
            qs = qs.filter(start_date__gte=date_from)
        if date_to:
            qs = qs.filter(start_date__lte=date_to)

        if "," in ordering:
            fields = [f.strip() for f in ordering.split(",") if f.strip()]
            return qs.order_by(*fields)

        return qs.order_by(ordering)
