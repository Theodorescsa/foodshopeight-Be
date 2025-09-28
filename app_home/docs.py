from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, OpenApiResponse, extend_schema_view
from drf_spectacular.types import OpenApiTypes
from .serializers import *
def custom_token_obtain_pair_view_schema():
    return extend_schema(
        summary="Đăng nhập và nhận JWT token",
        description="API này cho phép người dùng đăng nhập và nhận JWT token.",
        responses={
            200: {
                "type": "object",
                "properties": {
                    "refresh": {
                        "type": "string",
                        "example": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                    },
                    "access": {
                        "type": "string",
                        "example": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                    },
                },
                "description": "Đăng nhập thành công",
            },
            401: {
                "type": "object",
                "properties": {
                    "detail": {"type": "string", "example": "Invalid credentials"}
                },
                "description": "Thông tin đăng nhập không hợp lệ",
            },
        },
        tags=["app_home"],
    )