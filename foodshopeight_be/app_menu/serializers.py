# app_menu/serializers.py
from rest_framework import serializers
from .models import MenuItem, RecipeItem
from app_home.models import MenuCategory
from app_home.serializers import MenuCategorySerializer
from app_inventory.models import Ingredient
from app_inventory.serializers import IngredientSerializer


class RecipeItemSerializer(serializers.ModelSerializer):
    menu_item = serializers.PrimaryKeyRelatedField(
        queryset=MenuItem.objects.all()
    )
    ingredient = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )

    # read-only: thông tin chi tiết ingredient
    ingredient_detail = IngredientSerializer(source="ingredient", read_only=True)

    class Meta:
        model = RecipeItem
        fields = [
            "id",
            "menu_item",
            "ingredient", "ingredient_detail",
            "quantity",
        ]
        extra_kwargs = {
            "quantity": {"help_text": "Định lượng nguyên liệu cho 1 phần (theo đơn vị của Ingredient)"},
        }

    def validate_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError("quantity phải >= 0")
        return value


class MenuItemSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=MenuCategory.objects.all())

    category_detail = MenuCategorySerializer(source="category", read_only=True)
    image_url = serializers.SerializerMethodField(read_only=True)

    recipe_items = RecipeItemSerializer(many=True, read_only=True)

    class Meta:
        model = MenuItem
        fields = [
            "id",
            "name",
            "category", "category_detail",
            "price",
            "description",
            "available",
            "image", "image_url",
            "recipe_items",
        ]
        extra_kwargs = {
            "name": {"help_text": "Tên món (duy nhất)"},
            "price": {"help_text": "Giá bán / phần"},
            "description": {"help_text": "Mô tả ngắn"},
            "available": {"help_text": "Còn bán / tạm ẩn trên menu"},
            "image": {"help_text": "Ảnh món (ImageField)"},
        }

    def get_image_url(self, obj):
        request = self.context.get("request")
        if obj.image and hasattr(obj.image, "url"):
            url = obj.image.url
            return request.build_absolute_uri(url) if request else url
        return None
