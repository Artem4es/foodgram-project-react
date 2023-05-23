from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import (
    serializers,
    status,
    viewsets,
)

from api.v1.filters import RecipeFilter
from api.v1.services import create_pdf, get_ingredients
from api.v1.permissions import AuthorAdminPermission
from recipe.serializers import (
    IngredientSerializer,
    RecipeSerializer,
    RecipeSubscribeSerializer,
    TagSerializer,
)
from recipe.models import Cart, Favorites, Ingredient, Recipe, Tag
from recipe.validators import (
    check_if_not_favorited,
    check_if_owner,
    check_if_subscribed,
    check_recipe_id,
    is_in_cart,
    is_not_in_cart,
)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.select_related('product', 'measurement_unit')
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (SearchFilter,)
    search_fields = ('^name__name',)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.select_related('author')
    http_method_names = ('get', 'post', 'patch', 'delete')
    serializer_class = RecipeSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (AuthorAdminPermission,)

    def update(self, request, partial=False, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @action(
        detail=True,
        url_path=r'favorite',
        methods=('post', 'delete'),
    )
    def subscription(self, request, pk):
        recipe = check_recipe_id(pk, Recipe)
        cur_user = request.user
        if request.method == 'DELETE':
            check_if_not_favorited(cur_user, recipe, Favorites)
            Favorites.objects.get(user=cur_user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        elif request.method == 'POST':
            check_if_owner(recipe, cur_user)
            check_if_subscribed(cur_user, recipe, Favorites)
            Favorites.objects.get_or_create(user=cur_user, recipe=recipe)
            serializer = RecipeSubscribeSerializer(instance=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        methods=('get',),
        detail=False,
        url_path=r'download_shopping_cart',
        permission_classes=(IsAuthenticated,),
    )
    def download_file(self, *args, **kwargs):
        cur_user = self.request.user
        recipes_id = cur_user.cart.all().values_list('recipe_id', flat=True)
        if not recipes_id:
            raise serializers.ValidationError('У вас нет рецептов в корзине!')
        ingredients = get_ingredients(recipes_id)
        file_path, file_name = create_pdf(ingredients)
        document = open(file_path, 'rb')
        response = HttpResponse(document, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename={file_name}'
        return response

    @action(methods=('post', 'delete'), detail=True, url_path=r'shopping_cart')
    def change_cart(self, request, pk):
        recipe = check_recipe_id(pk, Recipe)
        cur_user = request.user
        if request.method == 'POST':
            is_in_cart(cur_user, recipe, Cart)
            Cart.objects.create(user=cur_user, recipe=recipe)
            serializer = RecipeSubscribeSerializer(instance=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            is_not_in_cart(cur_user, recipe, Cart)
            Cart.objects.get(user=cur_user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
