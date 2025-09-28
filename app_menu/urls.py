from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MenuItemViewSet, RecipeItemViewSet

router = DefaultRouter()
app_name = "app_menu"

router.register(r"menu-items", MenuItemViewSet, basename="menu-items")
router.register(r"menu-recipes", RecipeItemViewSet, basename="menu-recipes")

urlpatterns = [
    path("", include(router.urls)),
]
