from django_filters import (
    CharFilter,
    FilterSet,
    MultipleChoiceFilter,
)

from rest_framework import serializers
from rest_framework.filters import SearchFilter

from recipe.models import Recipe, Tag


class RecipeFilter(FilterSet):
    queryset = Tag.objects.all()
    choices = [(tag.slug, tag.name) for tag in Tag.objects.all()]
    tags = MultipleChoiceFilter(field_name='tags__slug', choices=choices)
    is_favorited = CharFilter(
        method='filter_is_favorited', label='В избранных'
    )
    is_in_shopping_cart = CharFilter(
        method='filter_is_in_shopping_cart', label='В списке покупок'
    )

    def filter_is_favorited(self, queryset, name, value):
        is_favorited = int(value)
        cur_user = self.request.user
        if cur_user.is_anonymous:
            raise serializers.ValidationError(
                {
                    'Авторизуйтесь': 'чтобы выполнить фильтрацию по избранным рецептам'
                }
            )

        recipes_list = cur_user.favorites.all().values_list(
            'recipe_id', flat=True
        )
        if is_favorited:
            return queryset.filter(id__in=recipes_list)
        return queryset.exclude(id__in=recipes_list)

    def filter_is_in_shopping_cart(self, queryset, name, value):
        is_in_shopping_cart = int(value)
        cur_user = self.request.user
        if cur_user.is_anonymous:
            raise serializers.ValidationError(
                {
                    'Авторизуйтесь': 'чтобы выполнить фильтрацию по избранным рецептам'
                }
            )

        recipes_list = cur_user.cart.all().values_list('recipe_id', flat=True)
        if is_in_shopping_cart:
            return queryset.filter(id__in=recipes_list)

        return queryset.exclude(id__in=recipes_list)

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')


class CustomSearchFilter(SearchFilter):
    search_param = 'name'
