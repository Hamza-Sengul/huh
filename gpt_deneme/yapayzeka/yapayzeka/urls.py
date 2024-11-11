# gpt_chatbot/urls.py
from django.contrib import admin
from django.urls import path
from menu import views as chat_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/chatbot_pdf_text/', chat_views.chatbot_pdf_text_response, name="chatbot_pdf_text_response"),
    path('api/chatbot/', chat_views.chatbot_response, name="chatbot_response"),
    path('api/chatbot_pdf/', chat_views.chatbot_pdf_response, name="chatbot_pdf_response"),
    path('', chat_views.chatbot_page, name="chatbot_page"),
]
