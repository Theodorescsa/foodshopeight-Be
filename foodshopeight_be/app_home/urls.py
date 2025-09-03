# user_home/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from rest_framework_simplejwt.views import TokenRefreshView

router = DefaultRouter()
app_name = 'app_home'



urlpatterns = [
    path("v1/", include(router.urls)),
    path("token/", views.CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    ]
