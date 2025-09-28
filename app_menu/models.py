from django.db import models
from django.core.validators import MinValueValidator
from app_home.models import MenuCategory
# Giữ nguyên import Ingredient từ app_inventory nếu dự án bạn đang để Ingredient trong app_inventory.
# Nếu Ingredient nằm ở app_inventory như phía trên, RecipeItem bên dưới không cần import Ingredient trực tiếp.

class MenuItem(models.Model):
    """Món ăn/đồ uống trên menu"""
    name = models.CharField("Tên món", max_length=255, unique=True)  # "Phở bò", "Cơm gà", ...
    category = models.ForeignKey(MenuCategory, on_delete=models.PROTECT, related_name="menu_items", verbose_name="Danh mục")
    price = models.DecimalField("Đơn giá", max_digits=14, decimal_places=2, validators=[MinValueValidator(0)])
    description = models.TextField("Mô tả", blank=True, default="")
    available = models.BooleanField("Còn bán", default=True)
    image = models.ImageField("Ảnh minh họa", upload_to="menu/", null=True, blank=True)

    class Meta:
        verbose_name = "Món trên menu"
        verbose_name_plural = "Món trên menu"

    def __str__(self):
        return self.name

class RecipeItem(models.Model):
    """
    Định lượng nguyên liệu cho 1 phần menu item (BOM).
    Ví dụ: 'Phở bò' dùng 0.2 kg Thịt bò + 0.1 kg Bánh phở + ...
    """
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name="recipe_items", verbose_name="Món")
    # Nếu Ingredient ở app_inventory: from app_inventory.models import Ingredient
    # Nếu Ingredient ở app_hr: from app_hr.models import Ingredient
    from app_inventory.models import Ingredient as _Ingredient  # tránh xung đột tên local
    ingredient = models.ForeignKey(_Ingredient, on_delete=models.PROTECT, related_name="recipe_usages", verbose_name="Nguyên liệu")
    quantity = models.DecimalField("Định lượng/1 phần", max_digits=12, decimal_places=3, validators=[MinValueValidator(0)])

    class Meta:
        unique_together = ("menu_item", "ingredient")
        verbose_name = "Định lượng nguyên liệu"
        verbose_name_plural = "Định lượng nguyên liệu"

    def __str__(self):
        return f"{self.menu_item} - {self.ingredient} ({self.quantity})"
