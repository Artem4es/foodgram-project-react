import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, status


def validate_username(value):
    if value.lower() == "me":
        raise ValidationError(_(f"Имя {value} использовать нельзя."))
    if not re.match(r"[\w.@+-]+\Z", value):
        raise ValidationError(_(f"{value} содержит недопустимые символы!"))


def check_user(id, User):
    if not User.objects.filter(id=id).exists():
        error = serializers.ValidationError(
            {"detail": f"Не существует пользователя с таким id: {id}"}
        )
        error.status_code = status.HTTP_404_NOT_FOUND
        raise error


def check_user_is_author(author, cur_user, User):
    if author == cur_user:
        raise serializers.ValidationError(
            "К сожалению, нельзя подписаться на себя :("
        )


def check_already_subscribed(author, cur_user, Follow):
    if Follow.objects.filter(user=cur_user, author=author).exists():
        raise serializers.ValidationError(
            "Вы уже подписаны на этого пользователя!"
        )


def check_if_not_subscribed(user, author, Follow):
    if not Follow.objects.filter(user=user, author=author).exists():
        raise serializers.ValidationError(
            {"errors": "Вы не подписаны на этого пользователя!"}
        )
