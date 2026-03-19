from django.urls import path
from . import views

app_name = 'comments' # Template'lerde URL çağırırken karışıklığı önler (örn: 'users:login')

urlpatterns = [
    path('<int:pk>/add/', views.add_comment, name='add_comment'),
]