import base64

from django.core.files.base import ContentFile
from rest_framework import serializers

from recipe.models import (
    Cart,
    Favorites,
    Ingredient,
    Recipe,
    RecipeIngredient,
    RecipeTag,
    Tag,
)
from recipe.validators import (
    validate_ingredients,
    validate_ingredient_id,
    validate_recipe_name,
    validate_tags,
)
from users.models import Follow, User


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return data


class IngredientSerializer(serializers.ModelSerializer):
    id = serializers.CharField(required=True)
    name = serializers.SlugRelatedField(slug_field='name', read_only=True)
    measurement_unit = serializers.SlugRelatedField(
        slug_field='name', read_only=True
    )
    amount = serializers.IntegerField(required=True, min_value=1)

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def validate_id(self, value):
        validate_ingredient_id(value, Ingredient)
        return value

    def to_representation(self, instance):
        if self.context.get('view').basename == 'ingredients':
            if self.fields.get('amount'):
                del self.fields['amount']
            return super().to_representation(instance)

        recipe = self.context.get('instance')
        amount = RecipeIngredient.objects.filter(
            ingredient=instance, recipe=recipe
        )[0].amount
        instance.amount = amount
        return super().to_representation(instance)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')

    def to_internal_value(self, data):
        if not isinstance(data, dict):
            cur_tag = validate_tags(data, Tag)
            tag = {}
            tag['id'] = cur_tag.id
            tag['name'] = cur_tag.name
            tag['color'] = cur_tag.color
            tag['slug'] = cur_tag.slug
            data = tag

        return data


class AuthorSerializer(
    serializers.ModelSerializer
):  # here to avoid circular import error
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        """Существует ли подписка на этого автора"""
        cur_user = self.context.get('request').user
        if cur_user.is_anonymous:
            return False
        if Follow.objects.filter(user=cur_user, author=obj).exists():
            return True
        return False

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


class RecipeSubscribeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=True)
    tags = TagSerializer(required=True, many=True)
    author = AuthorSerializer(required=False)
    ingredients = IngredientSerializer(required=True, many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_is_favorited(self, obj):
        """Избранные рецепты"""
        cur_user = self.context.get('request').user
        if cur_user.is_anonymous:
            return False
        if Favorites.objects.filter(user=cur_user, recipe=obj).exists():
            return True
        return False

    def get_is_in_shopping_cart(self, obj):
        """Список рецептов для покупки"""
        cur_user = self.context.get('request').user
        if cur_user.is_anonymous:
            return False
        if Cart.objects.filter(
            user=cur_user,
            recipe=obj,
        ).exists():
            return True
        return False

    def to_internal_value(self, data):
        tags = data.get('tags')
        if tags is None:
            return super().to_internal_value(data)
        tag_list = []
        if tags == []:
            tags = ['empty']
        for tag in tags:
            tags = TagSerializer(Tag, data=tag)
            tags.is_valid(raise_exception=True)
            tag_list.append(tags.validated_data)
        data['tags'] = tag_list
        return super().to_internal_value(data)

    def to_representation(self, instance):
        self.context['instance'] = instance  # for Ingr. ser-zer amount field
        return super().to_representation(instance)

    def validate_name(self, value):
        cur_user = self.context.get('request').user
        return validate_recipe_name(value, cur_user, Recipe)

    def validate_ingredients(self, value):
        """Responsible for internal part of ingredients"""
        return validate_ingredients(value)

    def create(self, validated_data):
        author = self.context.get('request').user
        tags = self.initial_data.get('tags', [])
        ingredients = self.initial_data.get('ingredients', [])
        validated_data['author'] = author
        validated_data.pop('tags')
        validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)

        for tag in tags:
            tag_id = tag.get('id')
            tag = Tag.objects.get(id=tag_id)
            RecipeTag.objects.get_or_create(recipe=recipe, tag=tag)

        for ingredient in ingredients:
            ing_id = ingredient.get('id')
            ing_inst = Ingredient.objects.get(id=ing_id)
            amount = ingredient.get('amount')
            RecipeIngredient.objects.get_or_create(
                recipe=recipe, ingredient=ing_inst, amount=amount
            )
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.get('tags')
        ingredients = validated_data.get('ingredients')
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        instance.save()

        RecipeTag.objects.filter(recipe_id=instance.id).delete()
        for tag in tags:
            tag = Tag.objects.filter(**tag)[0]
            RecipeTag.objects.create(recipe=instance, tag=tag)
        RecipeIngredient.objects.filter(recipe_id=instance.id).delete()
        for ingredient in ingredients:
            ing_id = ingredient.get('id')
            ing_inst = Ingredient.objects.get(id=ing_id)
            amount = ingredient.get('amount')
            RecipeIngredient.objects.get_or_create(
                recipe=instance, ingredient=ing_inst, amount=amount
            )

        return instance