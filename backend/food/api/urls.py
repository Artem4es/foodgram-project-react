from django.urls import include, path
from rest_framework.routers import DefaultRouter

app_name = 'api'

from .views import (
    IngredientViewSet,
    RecipeViewSet,
    TagViewSet,
)

app_name = 'api'

router = DefaultRouter()
# router.register(r'users', UsersViewSet, basename='users')
router.register(r'tags', TagViewSet)
router.register(r'recipes', RecipeViewSet)
router.register(r'ingredients', IngredientViewSet)


urlpatterns = [
    # path('auth/', include(auth_patterns)),
    path('', include(router.urls)),
    # Djoser создаст набор необходимых эндпоинтов.
    # базовые, для управления пользователями в Django:
    path('', include('djoser.urls')),  # внутри обрабатывает users/
    path(
        'auth/', include('djoser.urls.authtoken')
    ),  # внутри обрабатывает users/
    # JWT-эндпоинты, для управления JWT-токенами:
    path('auth/', include('djoser.urls.jwt')),
]
