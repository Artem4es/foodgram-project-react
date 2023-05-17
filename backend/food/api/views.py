from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import (
    serializers,
    status,
    viewsets,
    pagination,
)

from .filters import RecipeFilter
from .permissions import AuthorAdminPermission
from .serializers import (
    IngredientSerializer,
    RecipeSerializer,
    RecipeSubscribeSerializer,
    TagSerializer,
)
from recipe.models import Favorites, Ingredient, Recipe, Tag


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    http_method_names = ('get', 'post', 'patch', 'delete')
    queryset = Recipe.objects.all()
    pagination_class = pagination.LimitOffsetPagination
    serializer_class = RecipeSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (AuthorAdminPermission,)
    lookup_field = 'recipe_id'

    @action(
        detail=True,
        url_path=r'favorite',
        methods=('post', 'delete'),
    )
    def subscribtion(self, request, recipe_id):
        if not Recipe.objects.filter(id=recipe_id).exists():
            raise serializers.ValidationError(
                {"errors": f"Не существует рецепта с таким id: {recipe_id}"}
            )
        recipe = Recipe.objects.get(id=recipe_id)
        cur_user = request.user
        if recipe.author == cur_user:
            raise serializers.ValidationError(
                {
                    "errors": "К сожалению, нельзя подписаться или отписаться от себя:)"
                }
            )
        cur_user = request.user
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
            Favorites.objects.get_or_create(user=cur_user, recipe=recipe)
            serializer = RecipeSubscribeSerializer(instance=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)


# class CategoryViewSet(CreateReadDeleteModelViewSet):
#     queryset = Category.objects.all()
#     serializer_class = CategorySerializer
#     filter_backends = (filters.SearchFilter,)
#     search_fields = ('name',)
#     lookup_field = 'slug'
#     permission_classes = (AdminOrReadOnly,)


# class GenreViewSet(CreateReadDeleteModelViewSet):
#     queryset = Genre.objects.all()
#     serializer_class = GenreSerializer
#     filter_backends = (filters.SearchFilter,)
#     search_fields = ('name',)
#     lookup_field = 'slug'
#     permission_classes = (AdminOrReadOnly,)


# class TitleViewSet(CreateReadUpdateDeleteModelViewset):
#     http_method_names = (
#         "get",
#         "post",
#         "patch",
#         "delete",
#     )
#     queryset = Title.objects.all()
#     serializer_class = TitleSerializer
#     filter_backends = (DjangoFilterBackend,)
#     filterset_class = TitleFilter
#     permission_classes = (AdminOrReadOnly,)

#     def get_serializer_class(self):
#         if self.action in ('create', 'partial_update'):
#             return TitlePostSerializer
#         return TitleSerializer


# class ReviewViewSet(viewsets.ModelViewSet):
#     serializer_class = ReviewSerializer
#     permission_classes = (
#         AuthorAdminModeratorPermission,
#         IsAuthenticatedOrReadOnly,
#     )

#     def get_queryset(self):
#         title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
#         return title.reviews.all()

#     def perform_create(self, serializer):
#         user = self.request.user
#         title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
#         if serializer.is_valid():
#             serializer.save(author=user, title=title)


# class CommentViewSet(viewsets.ModelViewSet):
#     serializer_class = CommentSerializer
#     permission_classes = (
#         AuthorAdminModeratorPermission,
#         IsAuthenticatedOrReadOnly,
#     )

#     def get_queryset(self):
#         review = get_object_or_404(Review, pk=self.kwargs.get('review_id'))
#         return review.comments.all()

#     def perform_create(self, serializer):
#         review = get_object_or_404(Review, pk=self.kwargs.get('review_id'))
#         serializer.save(author=self.request.user, review=review)
