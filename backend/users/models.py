from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

from .constants import (
    USERNAME_REGEX,
    USERNAME_MAX_LENGTH,
    FIRST_NAME_MAX_LENGTH,
    LAST_NAME_MAX_LENGTH,
    EMAIL_MAX_LENGTH
)


class User(AbstractUser):
    username_validator = RegexValidator(
        regex=USERNAME_REGEX,
        message=(
            'Введите корректный логин. '
            'Разрешены только буквы, цифры и символы @/./+/-/_'
        )
    )
    username = models.CharField(
        'Логин',
        max_length=USERNAME_MAX_LENGTH,
        unique=True,
        validators=[username_validator]
    )
    first_name = models.CharField(
        'Имя',
        max_length=FIRST_NAME_MAX_LENGTH
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=LAST_NAME_MAX_LENGTH
    )
    avatar = models.ImageField(
        'Аватар',
        upload_to='avatars/',
        blank=True,
        null=True
    )
    email = models.EmailField(
        'Email',
        max_length=EMAIL_MAX_LENGTH,
        unique=True
    )

    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscription(models.Model):
    subscriber = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribers',
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['subscriber', 'author'],
                name='unique_follow'
            ),
            models.CheckConstraint(
                check=~models.Q(subscriber=models.F('author')),
                name='prevent_self_follow'
            )
        ]

    def clean(self):
        if self.subscriber == self.author:
            raise ValidationError('Нельзя подписаться на самого себя')

    def save(self, *args, **kwargs):
        if self.subscriber == self.author:
            raise ValidationError('Нельзя подписаться на самого себя')
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.subscriber} оформил подписку на {self.author}'
