import json
import uuid

from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer
from django.conf import settings
from django.template.loader import render_to_string
from openai import OpenAI, AsyncOpenAI
"""
class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {"type": "chat.message", "message": message}
        )

    # Receive message from room group
    def chat_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        self.send(text_data=json.dumps({"message": message}))

"""
class ChatConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        self.messages = []
        await super().connect()
        
        self.accept()

    async def receive(self, text_data):
        # our webhook handling code goes here
        text_data_json = json.loads(text_data)
        message_text = text_data_json["message"]
        # do something with the user's message
        # show user's message
        user_message_html = render_to_string(
            "pegasus_chat_demo/ws/chat_message.html",
            {
                "message_text": message_text,
                "is_system": False,
            },
        )
        await self.send(text_data=user_message_html)
        self.messages.append(
            {
                "role": "user",
                "content": message_text,
            }
        )
        message_id = f"message-{uuid.uuid4().hex}"
        system_message_html = render_to_string(
            "pegasus_chat_demo/ws/chat_message.html",
            {"message_text": "", "is_system": True, "message_id": message_id},
        )
        await self.send(text_data=system_message_html)

        client = AsyncOpenAI(api_key='sk-proj-POdrrFr1pZp8Xr1Dw4axT3BlbkFJpvWqpTGOU3JAanJQMChj')
        openai_response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=self.messages,
            stream=True,
        )
        chunks = []
        async for chunk in openai_response:
            message_chunk = (chunk.choices[0].delta.content or "")
            formatted_chunk = message_chunk.replace("\n", "<br>")
            await self.send(text_data=f'<div id="{message_id}" hx-swap-oob="beforeend">{formatted_chunk}</div>')
            chunks.append(message_chunk)
        self.messages.append({"role": "system", "content": "".join(chunks)})