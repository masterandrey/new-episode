from django.core.management.base import BaseCommand, CommandError
from channels.layers import get_channel_layer
import asyncio


class Command(BaseCommand):
    help = 'Send the message to the chat room'

    def add_arguments(self, parser):
        parser.add_argument('room', type=str)
        parser.add_argument('message', type=str)

    def handle(self, *args, **options):
        room = options['room']
        message = options['message']
        try:
            print(f'"{message}" to "{room}"')

            channel_layer = get_channel_layer()

            loop = asyncio.get_event_loop()
            loop.run_until_complete(channel_layer.group_send(f'chat_{room}', {
                'type': 'chat.message',
                'message': message
            }))
            loop.close()

        except Exception as e:
            raise e
