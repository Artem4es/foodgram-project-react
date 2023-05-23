from rest_framework.pagination import PageNumberPagination
from rest_framework.serializers import ValidationError
from rest_framework.settings import api_settings

DEFAULT_PAGE_SIZE = api_settings.PAGE_SIZE


class PageLimitPagination(PageNumberPagination):
    """Only page and limit parameters"""

    if not isinstance(DEFAULT_PAGE_SIZE, int):
        raise Exception(
            '"PAGE_SIZE" in settings.py should be a valid integer and > 0'
        )
    if DEFAULT_PAGE_SIZE < 1:
        raise Exception('"PAGE_SIZE" in settings.py can\'t be less than 1')

    def get_page_size(self, request):
        page_size = request.query_params.get('limit', DEFAULT_PAGE_SIZE)
        try:
            page_size = int(page_size)
        except ValueError:
            raise ValidationError('"limit" должен быть числом!')
        if page_size < 1:
            raise ValidationError('"limit" не может быть меньше 1')
        return page_size
