from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('', views.chat_view, name='chat'),
    path('send-message/', views.send_message, name='send_message'),
    path('conversation/<int:conversation_id>/', views.conversation_history, name='conversation_history'),
    path('conversation/create/', views.create_conversation, name='create_conversation'),
    path('conversation/<int:conversation_id>/delete/', views.delete_conversation, name='delete_conversation'),
]