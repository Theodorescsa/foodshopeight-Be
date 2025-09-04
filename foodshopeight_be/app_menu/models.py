from django.db import models
from django.core.validators import MinValueValidator
from app_home.models import MenuCategory
from app_inventory.models import Ingredient

class MenuItem(models.Model):
    """Món ăn/đồ uống trên menu"""
    name = models.CharField(max_length=255, unique=True)  # "Phở bò", "Cơm gà", ...
    category = models.ForeignKey(MenuCategory, on_delete=models.PROTECT, related_name="menu_items")
    price = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(0)])
    description = models.TextField(blank=True, default="")
    available = models.BooleanField(default=True)
    image = models.ImageField(upload_to="menu/", null=True, blank=True)

    def __str__(self):
        return self.name

class RecipeItem(models.Model):
    """
    Định lượng nguyên liệu cho 1 phần menu item (BOM).
    Ví dụ: 'Phở bò' dùng 0.2 kg Thịt bò + 0.1 kg Bánh phở + ...
    """
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name="recipe_items")
    ingredient = models.ForeignKey(Ingredient, on_delete=models.PROTECT, related_name="recipe_usages")
    quantity = models.DecimalField(max_digits=12, decimal_places=3, validators=[MinValueValidator(0)])

    class Meta:
        unique_together = ("menu_item", "ingredient")
