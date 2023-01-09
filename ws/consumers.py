import json
from channels.generic.websocket import AsyncWebsocketConsumer
import logging


logger = logging.getLogger(__name__)


class RiskOnlineConsumer(AsyncWebsocketConsumer):

    async def connect(self):

        logger.debug(f'connecting {self.channel_name}')
        await self.channel_layer.group_add(
            'risk_online',
            self.channel_name
        )
        await self.accept()

    async def receive(self, text_data=None, bytes_data=None, **kwargs):
        text_data = json.loads(text_data)
        status = text_data['status']
        logger.debug(f'{self.channel_name} receive: {str(status)}')

        if status == 'Connected':
            await self.send(
                json.dumps({'message': 'First!', })
            )

        elif status == 'Get':
            pass

        elif status == 'Close':
            await self.channel_layer.group_discard(
                'risk_online',
                self.channel_name
            )
            await self.close(1000)

        else:
            await self.channel_layer.group_discard(
                'risk_online',
                self.channel_name
            )
            await self.close(1000)

    async def broadcast(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))

    async def disconnect(self, code):
        """
        Called when a WebSocket connection is closed.
        """
        logger.debug(f'disconnected {self.channel_name}')
        await self.channel_layer.group_discard(
            'risk_online',
            self.channel_name
        )
        await self.close()
