from django.urls import include, path
from rest_framework.routers import DefaultRouter

# from users.views import SignUpView, TokenView, UsersViewSet

app_name = 'api'

from .views import RecipeViewSet, TagViewSet

# from .views import (
#     CategoryViewSet,
#     CommentViewSet,
#     GenreViewSet,
#     ReviewViewSet,
#     TitleViewSet,
# )

app_name = 'api'

router = DefaultRouter()
# router.register(r'users', UsersViewSet, basename='users')
router.register(r'tags', TagViewSet)
router.register(r'recipes', RecipeViewSet)
# router.register(r'genres', GenreViewSet)
# router.register(r'titles', TitleViewSet)
# router.register(
#     r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet, basename='reviews'
# )
# router.register(
#     r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
#     CommentViewSet,
#     basename='comments',
# )

# auth_patterns = [
#     path('signup/', SignUpView.as_view()),
#     path('token/', TokenView.as_view()),
# ]
# api/auth/token/login/
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
