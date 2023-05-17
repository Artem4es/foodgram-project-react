from rest_framework.mixins import CreateModelMixin, DestroyModelMixin
from rest_framework.viewsets import GenericViewSet


class CreateDeleteViewSet(CreateModelMixin, DestroyModelMixin, GenericViewSet):
    """Only create and destroy actions"""
