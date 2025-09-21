"""
URL configuration for foodshopeight_be project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.views.static import serve
from django.views.generic import TemplateView

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
urlpatterns = [
    path('media/<path:path>/', serve, {'document_root': settings.MEDIA_ROOT}),
    path('static/<path:path>/', serve, {'document_root': settings.STATIC_ROOT}),
    path('admin/', admin.site.urls),
    
    path('api-gateway/', include(('api_gateway.urls', 'api-gateway'), namespace='api-gateway')),
    path('api/app-home/', include("app_home.urls", namespace='app_home')),
    path("api/app-hr/", include("app_hr.urls", namespace="app_hr")),
    path("api/app-inventory/", include("app_inventory.urls", namespace="app_inventory")),
    path("api/app-menu/", include("app_menu.urls", namespace="app_menu")),
    path("api/app-order/", include("app_order.urls", namespace="app_order")),
    
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    
]
