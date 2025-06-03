import json
from django.db import transaction
from recipes.models import Ingredient


def load_ingredients():
    path = 'test_media/ingredients.json'

    with open(path, encoding='utf-8') as f:
        data = json.load(f)

        with transaction.atomic():
            existing = set(Ingredient.objects.values_list(
                'name',
                'measurement_unit'
            ))
            new_ingredients = [
                Ingredient(
                    name=item['name'],
                    measurement_unit=item['measurement_unit']
                )
                for item in data
                if (item['name'], item['measurement_unit']) not in existing
            ]
            Ingredient.objects.bulk_create(new_ingredients)
