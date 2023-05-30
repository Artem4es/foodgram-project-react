from rest_framework.pagination import PageNumberPagination
from rest_framework.serializers import ValidationError
from rest_framework.settings import api_settings

DEFAULT_PAGE_SIZE = api_settings.PAGE_SIZE


class PageLimitPagination(PageNumberPagination):
    """Only page and limit parameters"""

    page_size_query_param = 'limit'
