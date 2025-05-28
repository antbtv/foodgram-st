import json

from django.db import transaction

from recipes.models import Ingredient

path = ('test_media/ingredients.json')

with open(path, encoding='utf-8') as f:
    data = json.load(f)

    with transaction.atomic():
        for value in data:
            ingredient = Ingredient.objects.get_or_create(
                name=value['name'],
                measurement_unit=value['measurement_unit']
            )