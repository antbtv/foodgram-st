from django.db import models
from users.models import User
from django.core.validators import MinValueValidator

from .constants import (
    MIN_COOKING_TIME,
    MAX_RECIPE_NAME_LENGTH,
    MAX_INGREDIENT_NAME_LENGTH,
    MAX_MEASUREMENT_UNIT_LENGTH
)


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    name = models.CharField(
        'Название',
        max_length=MAX_RECIPE_NAME_LENGTH
    )
    text = models.TextField('Описание приготовления')
    ingredients = models.ManyToManyField(
        'Ingredient',
        through='RecipeIngredient',
        related_name='recipes',
        verbose_name='Ингредиенты'
    )
    cooking_time = models.PositiveIntegerField(
        'Время приготовления',
        validators=[MinValueValidator(MIN_COOKING_TIME)]
    )
    image = models.ImageField('Изображение', upload_to='recipes/')

    class Meta:
        ordering = ('name',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        'Название',
        max_length=MAX_INGREDIENT_NAME_LENGTH
    )

    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=MAX_MEASUREMENT_UNIT_LENGTH
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient'
            )
        ]

    def __str__(self):
        return f'{self.name} в {self.measurement_unit}'


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="recipe_ingredients",
        verbose_name="рецепт",
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name="recipe_ingredients",
        verbose_name="ингредиент",
    )
    amount = models.PositiveIntegerField(
        "количество",
        validators=[MinValueValidator(MIN_COOKING_TIME)],
    )

    class Meta:
        ordering = ("recipe", "ingredient")
        verbose_name = "ингредиент рецепта"
        verbose_name_plural = "ингредиенты рецепта"

    def __str__(self):
        return (
            f"{self.ingredient} : {self.amount}"
            f" ({self.ingredient.measurement_unit})"
        )


class Cart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_cart_user'
            )
        ]

    def __str__(self):
        return f'В корзине у {self.user} лежит {self.recipe}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite_user_recipe'
            )
        ]

    def __str__(self):
        return f'У {self.user} в избранном лежит {self.recipe}'
