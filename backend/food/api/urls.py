from django.urls import include, path
from rest_framework.routers import DefaultRouter

app_name = 'api'

from .views import (
    CustomTokenCreateView,
    CustomUserViewSet,
    SubscriptionsUserViewSet,
    IngredientViewSet,
    RecipeViewSet,
    TagViewSet,
)

app_name = 'api'

router = DefaultRouter()
# router.register(r'users', UsersViewSet, basename='users')


router.register(r'tags', TagViewSet)  # добавить basename
router.register(r'users/subscriptions', SubscriptionsUserViewSet)
router.register(r'users', CustomUserViewSet),
router.register(r'recipes', RecipeViewSet)
router.register(r'ingredients', IngredientViewSet)
# router.register(r'users/subscriptions', SubscribeUserViewSet)


urlpatterns = [
    path('', include(router.urls)),
    # Djoser создаст набор необходимых эндпоинтов.
    path('', include('djoser.urls')),  # внутри обрабатывает users/
    path('auth/', include('djoser.urls.authtoken')),
    path('auth/token/login/', CustomTokenCreateView.as_view()),
]
