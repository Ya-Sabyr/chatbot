from django.template.response import TemplateResponse
from django.shortcuts import render


def index(request):
    return render(request, "chat/index.html")

def chat(request):
    return TemplateResponse(request, "pegasus_chat_demo/single_chat.html")

def room(request, room_name):
    return render(request, "chat/room.html", {"room_name": room_name})