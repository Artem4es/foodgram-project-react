from django.core.exceptions import ValidationError
from rest_framework import serializers


def validate_time(value):
    if value < 1:
        raise ValidationError('Время приготовления не может быть меньше 1')


def validate_ingredient_id(value, ingredient):
    if not ingredient.objects.filter(id=value).exists():
        raise serializers.ValidationError(
            f'Не существует ингредиент с таким id: {value}'
        )


def validate_recipes_limit(value):
    try:
        recipes_limit = int(value)
    except ValueError:
        raise serializers.ValidationError(
            '"recipes_limit" должен быть целым числом!'
        )
    if recipes_limit < 0:
        raise serializers.ValidationError(
            '"recipes_limit" не может быть меньше 0!'
        )
    return int(value)


def validate_tags(value, Tag):
    if value == 'empty':
        raise serializers.ValidationError(
            {'tags': 'Содержимое поля "tags" не должно быть пустым!'}
        )
    if not isinstance(value, int):
        raise serializers.ValidationError(
            {
                'tags': f'Значения в поле "tags" должны иметь тип int. Введено: {type(value).__name__}'
            }
        )
    try:
        cur_tag = Tag.objects.get(id=value)
    except Tag.DoesNotExist:
        raise serializers.ValidationError(
            {'tags': f'Тег с id {value} не существует'}
        )
    return cur_tag


def is_unique(el_id, el_set, field):
    if el_id in el_set:
        raise serializers.ValidationError(
            f'Элементы в поле "{field}" не должны повторяться'
        )
    el_set.add(el_id)


def validate_recipe_name(name, cur_user, Recipe):
    if Recipe.objects.filter(author=cur_user, name=name).exists():
        raise serializers.ValidationError(
            'У вас уже есть рецепт с таким названием!'
        )
    return name


def validate_ingredients(value):
    """Responsible for internal part of ingredients"""
    if not value:
        raise serializers.ValidationError(
            'Поле ingredients не должно быть пустым!'
        )
    return value


def check_recipe_id(pk, Recipe):
    if not Recipe.objects.filter(id=pk).exists():
        raise serializers.ValidationError(
            {"errors": f"Не существует рецепта с таким id: {pk}"}
        )
    return Recipe.objects.get(id=pk)


def check_if_owner(recipe, cur_user):
    if recipe.author == cur_user:
        raise serializers.ValidationError(
            {"errors": "К сожалению, нельзя подписываться на свои рецепты:)"}
        )


def check_if_not_favorited(cur_user, recipe, Favorites):
    if not Favorites.objects.filter(user=cur_user, recipe=recipe).exists():
        raise serializers.ValidationError(
            {"errors": "Вы не подписаны на этот рецепт"}
        )


def check_if_subscribed(cur_user, recipe, Favorites):
    if Favorites.objects.filter(user=cur_user, recipe=recipe).exists():
        raise serializers.ValidationError(
            {"errors": "Вы уже подписаны на этот рецепт"}
        )


def is_in_cart(cur_user, recipe, Cart):
    if Cart.objects.filter(user=cur_user, recipe=recipe).exists():
        raise serializers.ValidationError(
            {"errors": "У вас в корзине уже есть этот рецепт"}
        )


def is_not_in_cart(cur_user, recipe, Cart):
    if not Cart.objects.filter(user=cur_user, recipe=recipe).exists():
        raise serializers.ValidationError(
            {"errors": "У вас нет этого рецепта в корзине"}
        )
