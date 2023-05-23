from django.contrib import admin
from django.urls import include, path

from api.v1.custom_exceptions import custom404, custom_server_error

handler404 = custom404
handler500 = custom_server_error

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls', namespace='api')),
]
