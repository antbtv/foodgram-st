from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    username = models.CharField('Логин', max_length=100, unique=True)
    first_name = models.CharField('Имя', max_length=100, unique=True)
    last_name = models.CharField('Фамилия', max_length=100)
    avatar = models.ImageField('Аватар', upload_to='avatars/', blank=True, null=True)
    email = models.EmailField('Email', max_length=100, unique=True)

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
            models.UniqueConstraint(fields=['subscriber', 'author'], name='unique_follow')
        ]

    def __str__(self):
        return f'{self.subscriber} оформил подписку на {self.author}'
