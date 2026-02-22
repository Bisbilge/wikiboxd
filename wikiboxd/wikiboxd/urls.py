from django.contrib import admin
from django.urls import path, include # include eklendi

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')), # Boş bırakılan ana dizini core.urls'e yönlendiriyoruz
]