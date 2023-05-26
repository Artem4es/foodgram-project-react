import os
import uuid

from reportlab.pdfbase import pdfmetrics, ttfonts
from reportlab.pdfgen import canvas

from food.settings import MEDIA_ROOT
from recipe.models import Ingredient, Recipe, RecipeIngredient


def get_ingredients(recipes_id):
    """Gets all ingredients for recipes and returns ingredients dictionary"""
    ingredients_dict = {}
    for rec_id in recipes_id:
        recipe = Recipe.objects.get(id=rec_id)
        ingredients = recipe.ingreds.all().values_list('ingredient', flat=True)
        for ing_id in ingredients:
            ingredient = Ingredient.objects.get(id=ing_id)
            amount = RecipeIngredient.objects.get(
                recipe=recipe, ingredient=ingredient
            ).amount
            ingredients_dict[str(ingredient)] = amount + ingredients_dict.get(
                str(ingredient), 0
            )
    return ingredients_dict


def create_pdf(ingredients):
    """Returns pdf with recipes"""
    filename = f'{str(uuid.uuid4())}.pdf'
    file_path = os.path.join(MEDIA_ROOT, 'pdf', filename)
    logo_path = os.path.join(MEDIA_ROOT, 'logo.jpg')
    p = canvas.Canvas(filename=file_path)
    p.drawImage(image=logo_path, x=195, y=500)
    pdfmetrics.registerFont(ttfonts.TTFont('Dejavu', 'DejaVuSans.ttf'))
    p.setFont('Dejavu', 14)
    p.drawCentredString(300, 478, 'Что нужно купить: ')
    p.setFont('Dejavu', 12)
    y = 450
    for ingredient, amount in ingredients.items():
        p.drawCentredString(
            x=300, y=y, text=f'{ingredient} {amount}'
        )  # что если не хватает страницы?
        y -= 15
    p.showPage()
    p.save()
    return file_path, filename
