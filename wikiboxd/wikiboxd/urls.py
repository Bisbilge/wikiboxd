from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('ratings/', include('ratings.urls')),
    path('', include('articles.urls')),
    path('comments/', include('comments.urls')),
]