from django.urls import path
from . import views

app_name = 'articles'

urlpatterns = [
    path('', views.home, name='home'),
    path('ara/', views.wiki_search, name='wiki_search'),
    path('ara/ekle/<path:wiki_title>/', views.wiki_import, name='wiki_import'),
    path('<int:pk>/', views.detail, name='detail'),
]