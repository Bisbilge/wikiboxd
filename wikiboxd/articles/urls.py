from django.urls import path
from . import views

app_name = 'articles'

urlpatterns = [
    path('', views.home, name='home'),
    path('makaleler/', views.article_list, name='article_list'),
    path('kategoriler/', views.category_list, name='category_list'),
    path('kategoriler/<slug:slug>/', views.category_detail, name='category_detail'),
    path('kategoriler/<slug:slug>/takip/', views.toggle_category_follow, name='category_follow'),
    path('ara/', views.wiki_search, name='wiki_search'),
    path('ara/ekle/<path:wiki_title>/', views.wiki_import, name='wiki_import'),
    path('<int:pk>/', views.detail, name='detail'),
    path('<int:pk>/embed/', views.wiki_embed_proxy, name='wiki_embed'),
    path('<int:pk>/favori/', views.toggle_favorite, name='toggle_favorite'),
]