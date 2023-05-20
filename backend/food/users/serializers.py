from djoser.serializers import (
    UserCreateSerializer,
)
from rest_framework import serializers

from api.serializers import AuthorSerializer, RecipeSubscribeSerializer
from .models import User


class CustomUserCreateSerializer(UserCreateSerializer):
    def to_internal_value(self, data):
        return super().to_internal_value(data)

    def to_representation(self, instance):
        return super().to_representation(instance)

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


class CustomUserSerializer(AuthorSerializer):  # UserSerializer
    """Responsible for /users/ endpoint"""

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )


class SubscribeUserSerializer(AuthorSerializer):  # можно унаследовать тоже
    recipes = RecipeSubscribeSerializer(many=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta:  # наследовать поля!
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def to_representation(self, instance):
        response = super().to_representation(instance)
        query_params = self.context.get('request').query_params
        recipes = response.get('recipes')
        if query_params:
            recipes_limit = query_params.get('recipes_limit')
            try:
                recipes_limit = int(recipes_limit)
            except ValueError:
                raise serializers.ValidationError(
                    '"recipes_limit" должен быть целым числом!'
                )
            if recipes_limit < 0:
                raise serializers.ValidationError(
                    '"recipes_limit" не может быть меньше 0!'
                )
            if len(recipes) >= recipes_limit:
                recipes = recipes[:recipes_limit]
            response['recipes'] = recipes
        return response

    def get_recipes_count(self, obj):
        user = obj
        return user.recipes.count()
