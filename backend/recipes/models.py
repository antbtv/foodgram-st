from django.db import models
from users.models import User
from django.core.validators import MinValueValidator

!!!Привести в единый стиль
class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="автор ",
    )
    name = models.CharField("название", max_length=100)
    text = models.TextField(verbose_name="описание приготовления")
    ingredients = models.ManyToManyField(
        "ingredient",
        through="RecipeIngredient",
        related_name="recipes",
        verbose_name="ингредиенты",
    )
    cooking_time = models.PositiveIntegerField(
        "время приготовления",
        validators=[MinValueValidator(1)],
    )
    image = models.ImageField("изображение", upload_to="recipes/")

    class Meta:
        ordering = ("name",)
        verbose_name = "рецепт"
        verbose_name_plural = "рецепты"

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        "название",
        max_length=100,
    )
    measurement_unit = models.CharField(
        "единица измерения",
        max_length=100,
    )

    class Meta:
        ordering = ("name",)
        verbose_name = "ингредиент"
        verbose_name_plural = "ингредиенты"
        constraints = [
            models.UniqueConstraint(
                fields=["name", "measurement_unit"],
                name="unique_ingredient",
            )
        ]

    def __str__(self):
        return f"{self.name} в {self.measurement_unit}"


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
        validators=[MinValueValidator(1)],
    )

    class Meta:
        ordering = ("recipe", "ingredient")
        verbose_name = "ингредиент"
        verbose_name_plural = "ингредиенты"

    def __str__(self):
        return (
            f"{self.ingredient} : {self.amount}"
            f" ({self.ingredient.measurement_unit})"
        )


class Cart(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='cart',
                             verbose_name='Пользователь')
    
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name='cart',
                               verbose_name='Рецепт')

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'КОрзины'
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='unique_cart_user')
        ]
    
    def __str__(self):
        return f'В корзине у {self.user} лежит {self.recipe}'


class Favorite(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='favorite',
                             verbose_name='Пользователь')

    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name='favorite',
                               verbose_name='Рецепт')

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='unique_favorite_user_recipe')
        ]

    def __str__(self):
        return f'У {self.user} в избранном лежит {self.recipe}'