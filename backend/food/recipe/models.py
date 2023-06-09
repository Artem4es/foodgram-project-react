from django.core import validators
from django.db import models

from recipe.validators import validate_time
from users.models import User


class Unit(models.Model):
    name = models.CharField(
        verbose_name='Единица измерения', max_length=50, unique=True
    )

    class Meta:
        verbose_name = 'Единица измерения'
        verbose_name_plural = 'Единицы измерения'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(verbose_name='Продукт', unique=True, max_length=50)

    class Meta:
        ordering = ('name',)
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='Продукт',
        max_length=200,
    )
    measurement_unit = models.ForeignKey(
        Unit,
        verbose_name='Единицы измерения',
        on_delete=models.CASCADE,
        max_length=200,
    )

    class Meta:
        ordering = ('product__name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.product} ({self.measurement_unit}) : '


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Название тега', max_length=200, unique=True
    )
    color = models.CharField(
        verbose_name='HEX-код цвета',
        max_length=7,
        unique=True,
    )
    slug = models.SlugField(
        verbose_name='Слаг',
        max_length=200,
        validators=[validators.validate_slug],
        unique=True,
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.slug


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
        db_index=True,
    )
    name = models.CharField(
        verbose_name='Название',
        help_text='Введите название рецепта',
        max_length=200,
        db_index=True,
    )
    image = models.FileField(
        verbose_name='Изображние',
        help_text='Добавьте изображение блюда',
        upload_to='images',
    )
    text = models.TextField(
        verbose_name='Описание', help_text='Опишите рецепт'
    )
    ingredients = models.ManyToManyField(
        Ingredient, through='RecipeIngredient', verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(
        Tag, through='RecipeTag', verbose_name='Тег рецепта'
    )
    cooking_time = models.IntegerField(
        verbose_name='Время приготовления',
        help_text='Введите время приготовления в минутах',
        validators=(validate_time,),
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeTag(models.Model):
    recipe = models.ForeignKey(
        Recipe, verbose_name='Рецепт', on_delete=models.CASCADE
    )
    tag = models.ForeignKey(
        Tag, verbose_name='Тег рецепта', on_delete=models.CASCADE
    )

    class Meta:
        ordering = ('recipe__name',)
        verbose_name = 'Теги рецептов'
        verbose_name_plural = 'Теги рецептов'

    def __str__(self):
        return f'{self.recipe} помечен тегом {self.tag}'


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        related_name='ingreds',
        on_delete=models.CASCADE,
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        related_name='recipes',
        on_delete=models.CASCADE,
    )
    amount = models.IntegerField(
        verbose_name='Количество',
    )

    class Meta:
        ordering = ('recipe__name',)
        verbose_name = 'Ингредиенты рецептов'
        verbose_name_plural = 'Ингредиенты рецептов'

    def __str__(self):
        return f'Для {self.recipe} нужны: {self.ingredient} {self.amount}'


class Favorites(models.Model):  # here to avoid circular import
    """Liked recipes"""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='favorites'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='favorites'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата добавления в избранное',
        auto_now_add=True,
    )

    class Meta:
        ordering = ('user', 'pub_date')
        verbose_name = 'Избранные рецепты'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_favorite'
            )
        ]

    def __str__(self):
        return f'{self.user} нравится {self.recipe}'


class Cart(models.Model):  # here to avoid circular import
    """Recipes to buy"""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='cart'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='cart'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата добавления в корзину',
        auto_now_add=True,
    )

    class Meta:
        ordering = ('user', 'pub_date')
        verbose_name = 'Покупка'
        verbose_name_plural = 'Покупки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_cart'
            )
        ]

    def __str__(self):
        return f'{self.user} покупает {self.recipe}'
