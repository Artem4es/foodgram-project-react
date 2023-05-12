from django.contrib import admin

from recipe.models import Recipe, Tag


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')
    search_fields = ('name', 'color', 'slug')
    prepopulated_fields = {"slug": ("name",)}


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
