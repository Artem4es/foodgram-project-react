from django.db import models
from django.utils.text import slugify

from users.models import User


class Unit(models.Model):
    name = models.CharField(
        verbose_name='Единица измерения', max_length=50, unique=True
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Единица измерения'
        verbose_name_plural = 'Единицы измерения'


class Product(models.Model):
    name = models.CharField(verbose_name='Продукт', unique=True, max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'


class Ingredient(models.Model):
    name = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='Продукт',
        max_length=50,
    )
    qty = models.IntegerField(verbose_name='Количество')
    units = models.ForeignKey(
        Unit, verbose_name='Единицы измерения', on_delete=models.CASCADE
    )

    def __str__(self):
        return f'{self.name}, {self.qty}, {self.units}'

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'


class Tag(models.Model):
    name = models.CharField(verbose_name='Название тега', max_length=50)
    color = models.CharField(verbose_name='HEX-код цвета', max_length=7)
    slug = models.SlugField(verbose_name='Слаг')

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name, allow_unicode=True)
        super(Tag, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipies',
        verbose_name='Автор',
        db_index=True,
    )
    name = models.CharField(
        verbose_name='Название',
        help_text='Введите название рецепта',
        max_length=255,
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
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации', auto_now_add=True
    )

    def __str__(self):
        return self.name

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'name'], name='unique_recipe'
            )
        ]
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


class RecipeTag(models.Model):
    recipe = models.ForeignKey(
        Recipe, verbose_name='Рецепт', on_delete=models.CASCADE
    )
    tag = models.ForeignKey(
        Tag, verbose_name='Тег рецепта', on_delete=models.CASCADE
    )

    def __str__(self):
        return f'{self.recipe} помечен тегом {self.tag}'


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe, verbose_name='Рецепт', on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(
        Ingredient, verbose_name='Ингредиент', on_delete=models.CASCADE
    )

    def __str__(self):
        return f'Для {self.recipe} нужны: {self.ingredient}'


class Favorites(models.Model):  # here to avoid circular import
    """Liked recipes"""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='recipes'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='users'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата добавления в избранное', auto_now_add=True
    )

    def __str__(self):
        return f'{self.user} нравится {self.recipe}'

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_favorite'
            )
        ]


class Cart(Favorites):  # here to avoid circular import
    """Recipes to buy"""

    buy_date = models.DateTimeField(
        verbose_name='Дата добавления в покупки', auto_now_add=True
    )

    def __str__(self):
        return f'{self.user} покупает {self.recipe}'

    class Meta:
        verbose_name = 'Покупка'
        verbose_name_plural = 'Покупки'
