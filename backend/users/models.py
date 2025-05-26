from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    username = models.CharField('Логин',
                                max_length=100, 
                                unique=True)
    first_name = models.CharField("Имя", 
                                  unique=True,
                                  max_length=100)
    last_name = models.CharField("Фамилия", 
                                 max_length=100)
    !!!!!!!!!!!!!!upload_to
    avatar = models.ImageField("Аватар", 
                               upload_to="", 
                               blank=True, 
                               null=True)
    email = models.EmailField("Email",
                              unique=True, 
                              max_length=150)
    

    REQUIRED_FIELDS = ['username',
                       'first_name',
                       'last_name',
                       'avatar']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username
    

class Subscription(models.Model):
    subscriber = models.ForeignKey(User, 
                                   on_delete=models.CASCADE,
                                   related_name='subscriber',
                                   verbose_name='Подписчик')
    
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='author',
                               verbose_name='Автор')

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['subscriber', 'author'],
                name='unique_follow'
            )
        ]

    def __str__(self):
        return f'{self.subscriber} оформил подписку на {self.author}'