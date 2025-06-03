from django.contrib import admin
from django import forms

from .models import (
    Recipe,
    Ingredient,
    Cart,
    Favorite,
    RecipeIngredient
)
from .constants import ADMIN_LIST_PER_PAGE


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    min_num = 1
    fields = ('ingredient', 'amount')
    autocomplete_fields = ('ingredient',)


class RecipeAdminForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        if not self.instance.pk and not self.data.get(
            'recipeingredient_set-TOTAL_FORMS',
            0
        ):
            raise forms.ValidationError(
                "Рецепт должен содержать хотя бы один ингредиент"
            )
        return cleaned_data


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    form = RecipeAdminForm
    list_display = ('name', 'author', 'cooking_time', 'favorites_count',)
    search_fields = ('name', 'author__username', 'author__email')
    list_filter = ('author',)
    readonly_fields = ('favorites_count',)
    inlines = (RecipeIngredientInline,)
    fieldsets = (
        (None, {
            'fields': ('author', 'name', 'image', 'text')
        }),
        ('Детали', {
            'fields': ('cooking_time', 'favorites_count')
        }),
    )

    def favorites_count(self, obj):
        return obj.favorites.count()
    favorites_count.short_description = 'В избранном'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit', 'recipes_count')
    search_fields = ('name', 'measurement_unit')
    list_filter = ('measurement_unit',)
    list_per_page = ADMIN_LIST_PER_PAGE

    def recipes_count(self, obj):
        return obj.recipes.count()
    recipes_count.short_description = 'Используется в рецептах'


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user__username', 'recipe__name')
    autocomplete_fields = ('user', 'recipe')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user__username', 'recipe__name')
    autocomplete_fields = ('user', 'recipe')


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount')
    search_fields = ('recipe__name', 'ingredient__name')
    list_filter = ('recipe', 'ingredient')
    autocomplete_fields = ('recipe', 'ingredient')
    list_select_related = ('recipe', 'ingredient')
