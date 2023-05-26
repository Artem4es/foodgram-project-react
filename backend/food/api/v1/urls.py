from django.urls import include, path

from recipe.urls import recipe_urlpatterns
from users.urls import users_urlpatterns


app_name = 'v1'

urlpatterns = [
    path(r'', include(users_urlpatterns)),
    path(r'', include(recipe_urlpatterns)),
    path(r'', include('djoser.urls')),
]
