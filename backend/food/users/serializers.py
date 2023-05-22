from djoser.serializers import (
    UserCreateSerializer,
)
from rest_framework import serializers

from recipe.validators import validate_recipes_limit
from recipe.serializers import AuthorSerializer, RecipeSubscribeSerializer
from .models import User


class CustomUserCreateSerializer(UserCreateSerializer):
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


class CustomUserSerializer(AuthorSerializer):
    """
    Responsible for "users" basename. Basically it's DRF UserSerializer
    """


class SubscribeUserSerializer(AuthorSerializer):
    recipes = RecipeSubscribeSerializer(many=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        new_fields = ('recipes', 'recipes_count')
        fields = AuthorSerializer.Meta.fields + new_fields

    def to_representation(self, instance):
        response = super().to_representation(instance)
        query_params = self.context.get('request').query_params
        recipes = response.get('recipes')
        recipes_limit = query_params.get('recipes_limit')
        if recipes_limit:
            recipes_limit = validate_recipes_limit(recipes_limit)
            if len(recipes) >= recipes_limit:
                recipes = recipes[:recipes_limit]
            response['recipes'] = recipes
        return response

    def get_recipes_count(self, obj):
        user = obj
        return user.recipes.count()
