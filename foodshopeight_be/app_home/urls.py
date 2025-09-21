# user_home/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views
from rest_framework_simplejwt.views import TokenRefreshView,TokenObtainPairView

router = DefaultRouter()
app_name = 'app_home'

router.register(r'units-admin', views.UnitViewSet, basename='unit')
router.register(r'ingredient-categories', views.IngredientCategoryViewSet, basename='ingredient-category')
router.register(r'menu-categories', views.MenuCategoryViewSet, basename='menu-category')
router.register(r'departments', views.DepartmentViewSet, basename='department')
router.register(r'positions', views.PositionViewSet, basename='position')
router.register(r'dining-tables', views.DiningTableViewSet, basename='dining-table')
router.register(r'app-settings', views.AppSettingViewSet, basename='app-setting')

urlpatterns = [
    path("v1/", include(router.urls)),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    ]
