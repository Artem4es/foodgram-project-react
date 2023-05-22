from django.http import JsonResponse
from rest_framework import status


def custom404(request, exception=None):
    data = {'detail': 'Упc, такой странички нет...'}
    return JsonResponse(data, status=status.HTTP_404_NOT_FOUND)


def custom_server_error(request, *args, **kwargs):
    data = {'error': 'Вы придумали что-то такое, что сервер упал в обморок...'}
    return JsonResponse(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
