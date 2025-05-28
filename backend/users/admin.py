from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (User, Subscription)


class AdminUser(UserAdmin):
    list_display = ('username',
                    'first_name',
                    'email',
                    'is_staff')
    
    ordering = ('email',)

    list_filter = ('is_staff',
                   'is_active')
    
    search_fields = ('username',
                     'email')


class AdminSubscribe(admin.ModelAdmin):
    list_display = ('id', 'subscriber', 'author')


admin.site.register(Subscription, AdminSubscribe)
admin.site.register(User, AdminUser)