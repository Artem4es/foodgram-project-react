from djoser.views import UserViewSet, TokenCreateView
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import (
    serializers,
    status,
    viewsets,
)

from .custom_pagination import PageLimitPagination
from .filters import RecipeFilter
from .functions import create_pdf, get_ingredients
from .permissions import AuthorAdminPermission, UnregisteredUserPermission
from .serializers import (
    IngredientSerializer,
    RecipeSerializer,
    RecipeSubscribeSerializer,
    TagSerializer,
)
from recipe.models import Cart, Favorites, Ingredient, Recipe, Tag
from users.models import Follow, User
from users.serializers import (
    CustomUserSerializer,
    SubscribeUserSerializer,
)


class CustomTokenCreateView(TokenCreateView):
    """Status code change from 200 to 201"""

    def _action(self, serializer):
        response = super()._action(serializer)
        response.status_code = status.HTTP_201_CREATED
        return response


class CustomUserViewSet(UserViewSet):  # можно в settings.py настроить?
    serializer_class = CustomUserSerializer
    permission_classes = (UnregisteredUserPermission,)  # для users/

    @action(detail=True, methods=('post', 'delete'), url_path=r'subscribe')
    def subscribe(self, request, id):
        self.check_permissions(request)
        if not User.objects.filter(id=id).exists():
            error = serializers.ValidationError(
                {'detail': f'Не существует пользователя с таким id: {id}'}
            )
            error.status_code = status.HTTP_404_NOT_FOUND
            raise error
        author = User.objects.get(id=id)
        cur_user = request.user
        if request.method == 'POST':
            if author == cur_user:
                raise serializers.ValidationError(
                    'К сожалению, нельзя подписаться на себя :('
                )
            if Follow.objects.filter(user=cur_user, author=author).exists():
                raise serializers.ValidationError(
                    'Вы уже подписаны на этого пользователя!'
                )
            Follow.objects.create(user=cur_user, author=author)
            serializer = SubscribeUserSerializer(
                instance=author, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            if not Follow.objects.filter(
                user=cur_user, author=author
            ).exists():
                raise serializers.ValidationError(
                    {'errors': 'Вы не подписаны на этого пользователя!'}
                )
            Follow.objects.filter(user=cur_user, author=author).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class SubscriptionsUserViewSet(
    viewsets.ModelViewSet  # объединить с users/ нельзя?
):  # наследовать от CustomUserViewSet?
    queryset = User.objects.all()
    http_method_names = ('get',)
    pagination_class = PageLimitPagination
    serializer_class = SubscribeUserSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        subscriptions = user.following.all().values_list('author', flat=True)
        return self.queryset.filter(id__in=subscriptions)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (SearchFilter,)
    search_fields = ('^name__name',)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    http_method_names = ('get', 'post', 'patch', 'delete')
    pagination_class = PageLimitPagination
    serializer_class = RecipeSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (AuthorAdminPermission,)

    @action(
        detail=True,
        url_path=r'favorite',
        methods=('post', 'delete'),
    )
    def subscription(self, request, pk):  # опечатка
        if not Recipe.objects.filter(id=pk).exists():
            raise serializers.ValidationError(
                {"errors": f"Не существует рецепта с таким id: {pk}"}
            )
        recipe = Recipe.objects.get(id=pk)
        cur_user = request.user
        if recipe.author == cur_user:
            raise serializers.ValidationError(
                {
                    "errors": "К сожалению, нельзя подписаться или отписаться от своих рецептов:)"
                }
            )
        if request.method == 'DELETE':
            if not Favorites.objects.filter(
                user=cur_user, recipe=recipe
            ).exists():
                raise serializers.ValidationError(
                    {"errors": "Вы не подписаны на этот рецепт"}
                )
            Favorites.objects.get(user=cur_user, recipe=recipe).delete()

            return Response(status=status.HTTP_204_NO_CONTENT)
        elif request.method == 'POST':
            if Favorites.objects.filter(user=cur_user, recipe=recipe).exists():
                raise serializers.ValidationError(
                    {"errors": "Вы уже подписаны на этот рецепт"}
                )
            Favorites.objects.get_or_create(user=cur_user, recipe=recipe)
            serializer = RecipeSubscribeSerializer(instance=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(methods=('get',), detail=False, url_path=r'download_shopping_cart')
    def download_file(self, *args, **kwargs):
        self.permission_classes = (IsAuthenticated,)
        self.check_permissions(self.request)
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
        if not Recipe.objects.filter(id=pk).exists():
            raise serializers.ValidationError(
                {"errors": f"Не существует рецепта с таким id: {pk}"}
            )
        cur_user = request.user
        recipe = Recipe.objects.get(id=pk)
        if request.method == 'POST':
            if Cart.objects.filter(user=cur_user, recipe=recipe).exists():
                raise serializers.ValidationError(
                    {"errors": "У вас в корзине уже есть этот рецепт"}
                )
            Cart.objects.create(user=cur_user, recipe=recipe)
            serializer = RecipeSubscribeSerializer(instance=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            if not Cart.objects.filter(user=cur_user, recipe=recipe).exists():
                raise serializers.ValidationError(
                    {"errors": "У вас нет этого рецепта в корзине"}
                )
            Cart.objects.get(user=cur_user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
