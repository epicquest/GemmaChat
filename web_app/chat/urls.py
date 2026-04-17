from django.urls import path

from . import views

app_name = "chat"

urlpatterns = [
    path("", views.chat_page, name="index"),
    path("stream/", views.stream_chat, name="stream"),
    path("clear/", views.clear_history, name="clear"),
]
