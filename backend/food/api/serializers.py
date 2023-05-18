import base64  # Модуль с функциями кодирования и декодирования base64

from rest_framework import serializers

from recipe.models import (
    Cart,
    Favorites,
    Ingredient,
    Product,
    Recipe,
    RecipeIngredient,
    RecipeTag,
    Tag,
)
from users.models import Follow, User


from django.core.files.base import ContentFile


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
    amount = serializers.IntegerField(required=True)  # в спецификации не req.

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def validate(self, attrs):
        return super().validate(attrs)

    def validate_amount(self, value):
        if value < 1:
            raise serializers.ValidationError(
                'Количество не может быть меньше 1'
            )
        return value

    def validate_id(self, value):
        if not Ingredient.objects.filter(id=value).exists():
            raise serializers.ValidationError(
                f'Не существует ингредиент с таким id: {value}'
            )
        return value

    def to_representation(self, instance):
        if 'ingredients' in (
            self.context.get('request').get_full_path()
        ):  # не делать жёстко
            if self.fields.get('amount'):
                del self.fields['amount']
            return super().to_representation(instance)
        else:
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

    def validate(self, attrs):
        return super().validate(attrs)

    def to_internal_value(self, data):
        return super().to_internal_value(data)


class AuthorSerializer(serializers.ModelSerializer):
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

    def validate(self, attrs):
        return super().validate(attrs)

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

    def to_internal_value(self, data):  # более изящная валидация!
        tags = data.get('tags')  # нельзя перенсти в tags этот метод?
        if not tags:
            return super().to_internal_value(data)
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

    def to_representation(self, instance):
        self.context['instance'] = instance  # for Ingr. ser-zer amount field
        return super().to_representation(instance)

    def validate_name(self, value):
        cur_user = self.context.get('request').user
        if Recipe.objects.filter(author=cur_user, name=value).exists():
            raise serializers.ValidationError(
                'У вас уже есть рецепт с таким названием!'
            )

        return value

    def validate_ingredients(self, value):
        """Responsible for internal part of ingredients"""
        if not value:
            raise serializers.ValidationError(
                'Поле ingredients не должно быть пустым!'
            )

        return value

    def validate_tags(self, value):
        """Responsible for internal part of tags"""
        if not value:
            raise serializers.ValidationError(
                'Поле Tag не должно быть пустым!'
            )

        return value

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

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)


# class AddDeleteRecipeSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Favorites
#         field

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
