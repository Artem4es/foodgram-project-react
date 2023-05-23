from django.urls import include, path
from rest_framework.routers import DefaultRouter

from recipe.views import (
    IngredientViewSet,
    RecipeViewSet,
    TagViewSet,
)

router_v1 = DefaultRouter()

app_name = 'recipe'

router_v1.register(r'tags', TagViewSet, basename='tags')
router_v1.register(r'recipes', RecipeViewSet, basename='recipes')
router_v1.register(r'ingredients', IngredientViewSet, basename='ingredients')

recipe_urlpatterns = [
    path('', include(router_v1.urls)),
]
