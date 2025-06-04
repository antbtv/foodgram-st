from django.urls import path, include
from django.contrib import admin

from api.views import redirect_to_recipe


urlpatterns = [
    path('api/', include('api.urls')),
    path('admin/', admin.site.urls),
    path('s/<int:pk>', redirect_to_recipe),
]
