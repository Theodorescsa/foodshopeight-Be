# app_menu/admin.py
from django.contrib import admin
from .models import MenuItem, RecipeItem


class RecipeItemInline(admin.TabularInline):
    model = RecipeItem
    extra = 1
    autocomplete_fields = ("ingredient",)


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "available")
    list_filter = ("category", "available")
    search_fields = ("name", "description")
    ordering = ("category", "name")
    list_editable = ("price", "available")
    inlines = [RecipeItemInline]


@admin.register(RecipeItem)
class RecipeItemAdmin(admin.ModelAdmin):
    list_display = ("menu_item", "ingredient", "quantity")
    search_fields = ("menu_item__name", "ingredient__name")
    list_filter = ("menu_item", "ingredient")
