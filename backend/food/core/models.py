# from django.db import models  # пока лишнее

# from recipe.models import Recipe
# from users.models import User


# class AbstactFavoriteCart(models.Model):
#     """Abstract class for Favotite and Cart models"""

#     user = models.ForeignKey(
#         User, on_delete=models.CASCADE, related_name='recipes'
#     )
#     recipe = models.ForeignKey(
#         Recipe, on_delete=models.CASCADE, related_name='users'
#     )
#     pub_date = models.DateTimeField(
#         verbose_name='Дата подписки или добавления в покупки',
#         auto_now_add=True,
#     )

#     class Meta:
#         abstract = True
