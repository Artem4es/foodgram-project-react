from django.contrib.auth.validators import UnicodeUsernameValidator
from djoser.serializers import UserSerializer, UserCreateSerializer
from rest_framework import serializers

from .models import User


class UserSignUpSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )


class UserSerializer(UserSerializer):
    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',  # добавить пагинацию и is_subscribed
        )
