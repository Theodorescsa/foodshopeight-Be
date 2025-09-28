# app_order/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from app_order.views import OrderViewSet, OrderItemViewSet

app_name = "app_order"

router = DefaultRouter()
router.register(r"orders", OrderViewSet, basename="orders")
router.register(r"order-items", OrderItemViewSet, basename="order-items")

urlpatterns = [
    path("", include(router.urls)),
]
