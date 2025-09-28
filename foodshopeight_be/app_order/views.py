from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db import transaction

from app_order.models import Order, OrderItem
from .serializers import (
    OrderSerializer,
    OrderItemReadSerializer,
    OrderItemWriteSerializer,
)


class OrderViewSet(viewsets.ModelViewSet):
    """
    /api/orders/  – tạo đơn với items (nested)
    Validate tồn kho theo BOM trước khi tạo.
    """
    queryset = Order.objects.all().select_related("table").prefetch_related("items", "items__menu_item")
    serializer_class = OrderSerializer

    # Optional: endpoint kiểm tra nhanh tồn kho trước khi tạo (dry-run)
    @action(detail=False, methods=["post"], url_path="check-stock")
    def check_stock(self, request, *args, **kwargs):
        """
        POST /api/orders/check-stock
        Body:
        {
          "items": [
            {"menu_item": <id>, "quantity": <int>},
            ...
          ]
        }
        -> 200 OK nếu đủ, 400 nếu thiếu (kèm chi tiết).
        """
        serializer = OrderItemWriteSerializer(data=request.data.get("items", []), many=True)
        serializer.is_valid(raise_exception=True)

        # Tận dụng logic trong OrderSerializer mà không ghi DB:
        order_ser = OrderSerializer()
        try:
            with transaction.atomic():
                order_ser._check_stock_for_items(serializer.validated_data)
            return Response({"ok": True, "message": "Đủ nguyên liệu"}, status=status.HTTP_200_OK)
        except Exception as e:
            # DRF ValidationError sẽ tự có detail; còn lại thì wrap message
            if hasattr(e, "detail"):
                return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class OrderItemViewSet(viewsets.ModelViewSet):
    """
    Cho phép xem danh sách items hoặc thêm từng item vào đơn (nếu bạn muốn).
    Khi tạo lẻ 1 item, cũng validate tồn kho (dựa trên BOM).
    """
    queryset = OrderItem.objects.all().select_related("order", "menu_item")
    # Auto chọn serializer theo action: write vs read
    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return OrderItemWriteSerializer
        return OrderItemReadSerializer

    def perform_create(self, serializer):
        """
        Nếu cho phép tạo OrderItem rời rạc: cần check tồn kho cho item đó.
        """
        item_data = serializer.validated_data
        fake_order_serializer = OrderSerializer()
        fake_order_serializer._check_stock_for_items([item_data])
        serializer.save(
            total=(item_data.get("unit_price") or item_data["menu_item"].price) * item_data["quantity"],
            name=item_data.get("name") or item_data["menu_item"].name,
        )
