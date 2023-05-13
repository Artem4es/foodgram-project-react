from django.contrib import admin

from recipe.models import (
    Favorites,
    Unit,
    Product,
    Ingredient,
    Recipe,
    RecipeIngredient,
    Tag,
)


class FavoritesAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user', 'recipe')


class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient')
    search_fields = ('recipe', 'ingredient')


class UnitAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('id', 'name')


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'amount', 'measurement_unit')
    search_fields = ('id', 'name', 'amount', 'measurement_unit')


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')
    search_fields = ('name', 'color', 'slug')
    prepopulated_fields = {"slug": ("name",)}


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        # 'tags',
        'author',
        # 'ingredients',
        # 'is_favorited',
        # 'is_in_shopping_cart',
        'name',
        'image',
        'text',
        'cooking_time',
    )
    search_fields = (
        'id',
        # 'tags',
        'author',
        # 'ingredients',
        # 'is_favorited',
        # 'is_in_shopping_cart',
        'name',
        'image',
        'text',
        'cooking_time',
    )


admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Unit, UnitAdmin)
admin.site.register(RecipeIngredient, RecipeIngredientAdmin)
admin.site.register(Favorites, FavoritesAdmin)
