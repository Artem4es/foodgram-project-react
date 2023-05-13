import base64  # Модуль с функциями кодирования и декодирования base64

from rest_framework import serializers

from recipe.models import (
    Favorites,
    Ingredient,
    Product,
    Recipe,
    RecipeTag,
    Tag,
)
from users.models import User


from django.core.files.base import ContentFile
from django.db import IntegrityError


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return data


# class AmountRelatedField(serializers.RelatedField):
#     def to_representation(self, value):  # нет при запросе ingredients
#         if self.context.get('request').get_full_path() == '/api/ingredients/':
#             return
#         return super().to_representation(value)


class IngredientSerializer(serializers.ModelSerializer):
    name = serializers.SlugRelatedField(slug_field='name', read_only=True)
    measurement_unit = serializers.SlugRelatedField(
        slug_field='name', read_only=True
    )

    def to_representation(self, instance):
        data = super(IngredientSerializer, self).to_representation(instance)
        if 'ingredients' in (
            self.context.get('request').get_full_path()
        ):  # не делать жёстко
            del data['amount']
        return data

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )  # amount только в Recipe


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')

    def validate(self, attrs):
        return super().validate(attrs)

    def to_internal_value(self, data):
        return super().to_internal_value(data)


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
        )  # добавить is_subscribed


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=True, allow_null=True)
    tags = TagSerializer(required=True, many=True)  # required не работает
    author = AuthorSerializer(required=False)
    ingredients = IngredientSerializer(
        required=False, many=True
    )  # тут закончил!!!
    # ingredients = serializers.SlugRelatedField(
    #     slug_field='name', queryset=Ingredient.objects.all(), many=True
    # )
    is_favorited = serializers.SerializerMethodField()

    def get_is_favorited(self, obj):  # тут закончил!
        """Избранные рецепты"""
        cur_user = self.context.get('request').user
        if cur_user.is_anonymous:
            return False
        if Favorites.objects.filter(user=cur_user, recipe=obj).exists():
            return True
        return False

    def validate(self, attrs):
        return super().validate(attrs)

    def to_internal_value(self, data):
        tags = data.pop('tags')
        tag_list = []
        for d in tags:
            if not isinstance(d, int):
                raise serializers.ValidationError(
                    {
                        'Значение Tag должно быть типом int. Введено': type(
                            d
                        ).__name__
                    }
                )
            tag_dict = {}
            try:
                tag = Tag.objects.get(id=d)
            except Tag.DoesNotExist:
                raise serializers.ValidationError(
                    {'Тег с id': f'{d} не существует'}
                )
            tag_dict['id'] = tag.id
            tag_dict['name'] = tag.name
            tag_dict['color'] = tag.color
            tag_dict['slug'] = tag.slug
            tag_list.append(tag_dict)
        data['tags'] = tag_list
        return super().to_internal_value(data)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',  # автоматически при создании
            'ingredients',
            'is_favorited',
            # 'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def validate_tags(self, value):  # по идее должно быть через required=True
        if not value:
            raise serializers.ValidationError(
                {'Поле Tag не должно быть пустым!'}
            )

        return value

    def create(self, validated_data):
        author = self.context.get('request').user
        tags = self.initial_data.get('tags', [])
        validated_data['author'] = author
        validated_data.pop('tags')
        try:
            recipe = Recipe.objects.create(**validated_data)
        except IntegrityError:
            raise serializers.ValidationError(
                'У вас уже есть рецепт с таким названием!'
            )

            # if User.objects.filter(username=username).exists():
            # raise serializers.ValidationError(
            #     'Другой пользователь с таким username уже существует.'
            # )
        for tag in tags:
            id = tag.get('id')
            tag = Tag.objects.get(id=id)
            RecipeTag.objects.get_or_create(recipe=recipe, tag=tag)
        return recipe

    # def validators(self):
    #     return super().validators

    # def is_valid(self, *, raise_exception=False):
    #     return super().is_valid(raise_exception=raise_exception)

    # def get_validators(self):
    #     return super().get_validators()

    # def validated_data(self):
    #     return super().validated_data


# class ReviewSerializer(serializers.ModelSerializer):
#     author = serializers.SlugRelatedField(
#         read_only=True, slug_field='username'
#     )

#     class Meta:
#         fields = ('id', 'text', 'author', 'score', 'pub_date')
#         model = Review

#     def validate(self, data):
#         user = self.context.get('request').user
#         title = self.context.get('view').kwargs.get('title_id')
#         if self.context.get('view').action == 'create':
#             if Review.objects.filter(title=title).filter(author=user).exists():
#                 raise serializers.ValidationError(
#                     'Второй раз отзыв отправлять нельзя!'
#                 )
#         return data


# class CommentSerializer(serializers.ModelSerializer):
#     author = serializers.SlugRelatedField(
#         read_only=True, slug_field='username'
#     )

#     class Meta:
#         fields = ('id', 'text', 'author', 'pub_date')
#         model = Comment


# class CategorySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Category
#         fields = ('name', 'slug')


# class GenreSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Genre
#         fields = ('name', 'slug')


# class TitleSerializer(serializers.ModelSerializer):
#     rating = serializers.SerializerMethodField()
#     genre = GenreSerializer(many=True)
#     category = CategorySerializer()

#     def get_rating(self, obj):
#         rating = Review.objects.filter(title=obj).aggregate(Avg('score'))
#         return rating['score__avg']

#     class Meta:
#         model = Title
#         fields = '__all__'


# class TitlePostSerializer(serializers.ModelSerializer):
#     rating = serializers.SerializerMethodField()
#     genre = serializers.SlugRelatedField(
#         slug_field='slug', queryset=Genre.objects.all(), many=True
#     )
#     category = serializers.SlugRelatedField(
#         slug_field='slug', queryset=Category.objects.all()
#     )

#     def get_rating(self, obj):
#         rating = Review.objects.filter(title=obj).aggregate(Avg('score'))
#         return rating['score__avg']

#     class Meta:
#         model = Title
#         fields = '__all__'
