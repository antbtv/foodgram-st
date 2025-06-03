import os

from django.shortcuts import get_object_or_404
from django.http import FileResponse
from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum

from recipes.models import (
    Recipe, Ingredient,
    RecipeIngredient, Cart, Favorite
)
from users.models import User, Subscription
from .serializers import (
    UserSerializer, UserCreateSerializer, AvatarSerializer,
    IngredientSerializer, RecipeReadSerializer, ShortRecipeSerializer,
    RecipeWriteSerializer, SubscriptionSerializer
)
from .permissions import (
    RecipePermission,
    AdminOrReadOnly,
    CartFavoritePermission
)
from .filters import IngredientFilter, RecipeFilter
from .pagination import Paginator


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = IngredientFilter
    search_fields = ['^name']


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = Paginator
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    permission_classes = [RecipePermission]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return RecipeWriteSerializer
        return RecipeReadSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_link(self, request, pk=None):
        recipe = self.get_object()
        short_link = f'({os.getenv("LINK_DOMAIN")}{recipe.pk})'
        return Response({'short-link': short_link})

    def _toggle(self, request, pk, model, serializer_class, exists_msg):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user
        exists = model.objects.filter(user=user, recipe=recipe).exists()
        if request.method == 'POST':
            if exists:
                return Response(
                    {'error': exists_msg},
                    status=status.HTTP_400_BAD_REQUEST
                )
            model.objects.create(user=user, recipe=recipe)
            data = serializer_class(
                recipe, context={'request': request}
            ).data
            return Response(data, status=status.HTTP_201_CREATED)
        if not exists:
            return Response(
                {'error': exists_msg},
                status=status.HTTP_400_BAD_REQUEST
            )
        model.objects.filter(user=user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[CartFavoritePermission]
    )
    def favorite(self, request, pk=None):
        return self._toggle(
            request, pk, Favorite, ShortRecipeSerializer,
            'Рецепт уже в избранном'
        )

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[CartFavoritePermission]
    )
    def shopping_cart(self, request, pk=None):
        return self._toggle(
            request, pk, Cart, ShortRecipeSerializer,
            'Рецепт уже в корзине'
        )

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        items = Cart.objects.filter(user=request.user)
        if not items.exists():
            return Response(
                {'error': 'Корзина пуста'},
                status=status.HTTP_404_NOT_FOUND
            )

        ingredients = RecipeIngredient.objects.filter(
            recipe__cart__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(
            total_amount=Sum('amount')
        ).order_by('ingredient__name')

        lines = [
            f"{item['ingredient__name']}: {item['total_amount']} "
            f"{item['ingredient__measurement_unit']}"
            for item in ingredients
        ]
        content = "\n".join(lines)
        return FileResponse(
            content,
            as_attachment=True,
            filename='shopping_list.txt',
            content_type='text/plain; charset=utf-8'
        )


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    pagination_class = Paginator
    http_method_names = [
        'get', 'post', 'delete', 'put', 'patch', 'head', 'options'
    ]

    def get_permissions(self):
        if self.action in ['create']:
            return []
        if self.action in ['retrieve']:
            return [AllowAny()]
        if self.action == 'list':
            return [AdminOrReadOnly()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        if self.action == 'avatar':
            return AvatarSerializer
        return UserSerializer

    def get_object(self):
        return get_object_or_404(User, pk=self.kwargs.get("pk"))

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        serializer = UserSerializer(request.user, context={'request': request})
        return Response(serializer.data)

    @action(
        detail=False,
        methods=['put', 'delete'],
        url_path='me/avatar',
        permission_classes=[IsAuthenticated],
    )
    def avatar(self, request):
        user = request.user

        if request.method == 'DELETE':
            user.avatar.delete(save=False)
            user.avatar = None
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

        if 'avatar' not in request.data:
            return Response(
                {'avatar': ['Это поле обязательно.']},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = AvatarSerializer(
            user,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {'avatar': request.build_absolute_uri(user.avatar.url)},
            status=status.HTTP_200_OK
        )

    @action(
        detail=False,
        methods=['post'],
        url_path='set_password',
        permission_classes=[IsAuthenticated]
    )
    def set_password(self, request):
        user = request.user
        current = request.data.get('current_password')
        new = request.data.get('new_password')

        if not user.check_password(current):
            return Response(
                {'error': 'Неверный текущий пароль'},
                status=status.HTTP_400_BAD_REQUEST
            )
        user.set_password(new)
        user.save()
        return Response(
            {'status': 'Пароль изменен'},
            status=status.HTTP_204_NO_CONTENT
        )

    @action(
        detail=False,
        methods=['get'],
        url_path='subscriptions',
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        authors = User.objects.filter(subscribers__subscriber=request.user)
        page = self.paginate_queryset(authors)
        serializer = SubscriptionSerializer(
            page,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='subscribe',
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, pk=None):
        subscriber = request.user
        author = get_object_or_404(User, pk=pk)

        if author == subscriber:
            return Response(
                {'error': 'Нельзя подписаться на себя'},
                status=status.HTTP_400_BAD_REQUEST
            )

        subscription_exists = Subscription.objects.filter(
            subscriber=subscriber,
            author=author
        ).exists()

        if request.method == 'POST':
            if subscription_exists:
                return Response(
                    {'error': 'Вы уже подписаны'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Subscription.objects.create(subscriber=subscriber, author=author)
            data = SubscriptionSerializer(
                author,
                context={'request': request}
            ).data
            return Response(data, status=status.HTTP_201_CREATED)

        if not subscription_exists:
            return Response(
                {'error': 'Нельзя отписаться, подписка не найдена'},
                status=status.HTTP_400_BAD_REQUEST
            )
        Subscription.objects.filter(
            subscriber=subscriber,
            author=author
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
