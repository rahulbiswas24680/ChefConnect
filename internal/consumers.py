import json

from channels.generic.websocket import AsyncWebsocketConsumer

class LocationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.location_group_name = f'location_{self.user_id}'

        await self.channel_layer.group_add(
            self.location_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.location_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        try:
            location_data_json = json.loads(text_data)
            latitude = location_data_json.get('latitude')
            longitude = location_data_json.get('longitude')

            if latitude is not None and longitude is not None:
                # Store the location in the database (optional)
                # ...

                # Broadcast the location to the group
                await self.channel_layer.group_send(
                    self.location_group_name,
                    {
                        'type': 'location_update',
                        'latitude': latitude,
                        'longitude': longitude,
                        'user_id' : self.user_id
                    }
                )
            else:
                await self.send(text_data=json.dumps({'error': 'Invalid location data'}))

        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({'error': 'Invalid JSON'}))

    async def location_update(self, event):
        latitude = event['latitude']
        longitude = event['longitude']
        user_id = event['user_id']
        await self.send(text_data=json.dumps({
            'latitude': latitude,
            'longitude': longitude,
            'user_id' : user_id
        }))