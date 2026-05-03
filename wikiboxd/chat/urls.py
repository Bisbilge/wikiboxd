from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.inbox, name='inbox'),
    path('<int:conversation_id>/', views.conversation_detail, name='conversation'),
    path('start/<str:username>/', views.start_conversation, name='start_conversation'),
]
