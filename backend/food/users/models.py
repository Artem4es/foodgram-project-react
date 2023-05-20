from django.contrib.auth.models import AbstractUser
from django.db import models


from .validators import validate_username

# from recipe.models import Recipe

# User = get_user_model()


class User(AbstractUser):
    USER = 'user'
    ADMIN = 'admin'

    USER_ROLES = [
        (USER, USER),
        (ADMIN, ADMIN),
    ]

    username = models.CharField(
        validators=(validate_username,),
        max_length=150,
        unique=True,
        verbose_name='Логин',
    )
    first_name = models.CharField(verbose_name='Имя', max_length=150)
    last_name = models.CharField(verbose_name='Фамилия', max_length=150)
    email = models.EmailField(
        max_length=254,
        unique=True,
        verbose_name='Email',
    )
    password = models.CharField(
        max_length=150, blank=False, verbose_name='Пароль'
    )
    role = models.CharField(
        max_length=20,
        choices=USER_ROLES,
        default=USER,
        verbose_name="Роль",
    )

    class Meta:
        ordering = ('id',)
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        constraints = [
            models.UniqueConstraint(
                fields=['username', 'email'], name='unique_username_email'
            )
        ]

    @property
    def is_user(self):
        return self.role == self.USER

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_superuser or self.is_staff

    def __str__(self):
        return self.username


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Подписчик',
        related_name='following',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='followers',
    )

    pub_date = models.DateTimeField(
        verbose_name='Дата подписки', auto_now_add=True
    )

    def __str__(self):
        return f'{self.user} подписан на {self.author}'

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'], name='unique_subscription'
            )
        ]
