import pytest
import websocket
import json


#@pytest.mark.integration_test
def test_channels(django_server, redis_server):
    """
    Test django channels.
    * Start django server
    * open two websocket connections to it
    * Send message from one websocket connection and wait for it in another.
    """
    def get_message(data: str) -> str:
        try:
            message = json.loads(data)['message']
        except:
            assert False, f'Cannot decode message from received data "{data}"'
        return message
    sender = websocket.create_connection(f'ws://{django_server}/ws/chat/test/')
    sender_channel_name = get_message(sender.recv())
    print(f'Open sender channel "{sender_channel_name}"')
    listener = websocket.create_connection(f'ws://{django_server}/ws/chat/test/')
    listener_channel_name = get_message(listener.recv())
    print(f'Open listener channel "{listener_channel_name}"')

    sent_message = 'Hello, World'
    sender.send(json.dumps({'message': sent_message}))
    received_message = get_message(listener.recv())
    assert sent_message == received_message
