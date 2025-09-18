from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from rest_framework.routers import DefaultRouter
from app_hr.views import StaffProfileViewSet
from app_inventory.views import SupplierViewSet, IngredientViewSet, InventoryLotViewSet
from app_menu.views import MenuItemViewSet, RecipeItemViewSet

router = DefaultRouter()
app_name = 'api_gateway'

# ---- HR ----
router.register(r"hr/staff-profiles", StaffProfileViewSet, basename="hr-staff-profiles")

# ---- INVENTORY ----
router.register(r"inventory/suppliers", SupplierViewSet, basename="inventory-suppliers")
router.register(r"inventory/ingredients", IngredientViewSet, basename="inventory-ingredients")
router.register(r"inventory/lots", InventoryLotViewSet, basename="inventory-lots")

# ---- MENU ----
router.register(r"menu/items", MenuItemViewSet, basename="menu-items")
router.register(r"menu/recipes", RecipeItemViewSet, basename="menu-recipes")

urlpatterns = [
    path('', include(router.urls)),  # Include the router URLs
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='api-gateway:schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='api_gateway:schema'), name='redoc'),
]
