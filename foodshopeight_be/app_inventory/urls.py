from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SupplierViewSet, IngredientViewSet, InventoryLotViewSet

router = DefaultRouter()
app_name = "app_inventory"

router.register(r"suppliers", SupplierViewSet, basename="inventory-suppliers")
router.register(r"ingredients", IngredientViewSet, basename="inventory-ingredients")
router.register(r"lots", InventoryLotViewSet, basename="inventory-lots")

urlpatterns = [
    path("", include(router.urls)),
]
