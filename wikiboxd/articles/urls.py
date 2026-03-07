from django.urls import path
from . import views

app_name = 'articles'

urlpatterns = [
    # Boş bırakılan URL anasayfayı temsil eder ve views.home fonksiyonunu çalıştırır.
    path('', views.home, name='home'),
]