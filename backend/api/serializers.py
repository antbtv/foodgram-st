from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField
from rest_framework.exceptions import ValidationError
from django.contrib.auth import get_user_model
from djoser.serializers import (
    UserCreateSerializer as DjoserUserCreateSerializer
)
from django.core.validators import MinValueValidator

from recipes.models import (
    Ingredient,
    RecipeIngredient,
    Recipe
)
from .constants import MIN_AMOUNT

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name',
            'last_name', 'is_subscribed', 'avatar'
        )
        read_only_fields = ('id', 'is_subscribed')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return (
            request.user.is_authenticated
            and obj.subscribers.filter(subscriber=request.user).exists()
        )


class UserCreateSerializer(DjoserUserCreateSerializer):
    class Meta(DjoserUserCreateSerializer.Meta):
        model = User
        fields = (
            'id', 'email', 'username', 'first_name',
            'last_name', 'password'
        )
        extra_kwargs = {
            'password': {'write_only': True}
        }


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=True)

    class Meta:
        model = User
        fields = ('avatar',)

    def validate_avatar(self, value):
        if not value:
            raise serializers.ValidationError(
                {"Поле аватара обязательно."}
            )
        return value


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientWriteSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField(
        validators=[MinValueValidator(MIN_AMOUNT)]
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeIngredientReadSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id', 'name', 'measurement_unit', 'amount'
        )


class RecipeReadSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientReadSerializer(
        many=True,
        source='recipe_ingredients'
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'image', 'ingredients', 'text',
            'cooking_time', 'author', 'is_favorited', 'is_in_shopping_cart'
        )

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image:
            url = obj.image.url
            if request:
                return request.build_absolute_uri(url)
            return url
        return None

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        user = request.user if request else None
        return (
            user
            and user.is_authenticated
            and obj.favorite.filter(user=user).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        user = request.user if request else None
        return (
            user
            and user.is_authenticated
            and obj.cart.filter(user=user).exists()
        )


class RecipeWriteSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientWriteSerializer(
        many=True,
        write_only=True,
        required=True
    )
    image = Base64ImageField(required=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'image', 'text',
            'cooking_time', 'ingredients'
        )

    def validate_image(self, value):
        if value == "" or value is None:
            raise serializers.ValidationError(
                "Поле 'image' не может быть пустым."
            )
        return value

    def validate_ingredients(self, value):
        if not value:
            raise ValidationError('Добавьте хотя бы один ингредиент')

        ingredients = [item['id'] for item in value]
        if len(ingredients) != len(set(ingredients)):
            raise ValidationError('Ингредиенты не должны повторяться')

        return value

    def create_ingredients(self, recipe, ingredients):
        RecipeIngredient.objects.bulk_create([
            RecipeIngredient(
                recipe=recipe,
                ingredient=item['id'],
                amount=item['amount']
            ) for item in ingredients
        ])

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        print(ingredients)
        recipe = Recipe.objects.create(**validated_data)
        self.create_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        instance.recipe_ingredients.all().delete()
        self.create_ingredients(instance, ingredients)
        return super().update(instance, validated_data)


class ShortRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
        read_only=True,
        source='recipes.count'
    )

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('recipes', 'recipes_count')
        read_only_fields = (
            UserSerializer.Meta.read_only_fields
            + ('recipes', 'recipes_count')
        )

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes = obj.recipes.all()
        try:
            if limit := request.query_params.get('recipes_limit'):
                recipes = recipes[:int(limit)]
        except ValueError:
            pass
        return ShortRecipeSerializer(recipes, many=True).data
