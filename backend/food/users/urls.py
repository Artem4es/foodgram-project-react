from django.urls import include, path
from rest_framework.routers import DefaultRouter

from users.views import (
    CustomTokenCreateView,
    CustomUserViewSet,
)

app_name = 'users'

router_v1 = DefaultRouter()
router_v1.register(r'users', CustomUserViewSet, basename='users'),


users_urlpatterns = [
    path('', include(router_v1.urls)),
    path(
        'auth/token/login/',
        CustomTokenCreateView.as_view(),
        name='token_create',
    ),
]
