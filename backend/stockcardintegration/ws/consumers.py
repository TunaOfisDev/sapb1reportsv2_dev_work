# path: backend/stockcardintegration/ws/consumers.py

from channels.generic.websocket import AsyncWebsocketConsumer
import json

class ProductPriceListConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("product_price_list", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("product_price_list", self.channel_name)

    async def price_list_refresh(self, event):
        await self.send(text_data=json.dumps({
            "action": "refresh"
        }))
