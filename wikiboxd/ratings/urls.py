from django.urls import path
from . import views

app_name = 'ratings' # Template'lerde URL çağırırken karışıklığı önler (örn: 'users:login')

urlpatterns = [
    path('<int:pk>/rate/', views.rate_article, name='rate_article'),
]