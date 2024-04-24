from django.urls import path

from . import views

app_name = "chat_demo"

urlpatterns = [
    path("", views.index, name="index"),
    path("chat/", views.chat, name="chat"),
    path("<str:room_name>/", views.room, name="room"),
]
