from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiExample, OpenApiParameter, OpenApiTypes
from rest_framework import viewsets
from rest_framework.decorators import action, api_view
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from django.db.models import Q
from rest_framework.views import APIView

from .serializers import CustomTokenObtainPairSerializer
from .pagination import CustomPagination
from .docs import *
from datetime import date
    
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
    