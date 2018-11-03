import pytest
import websocket
import json


@pytest.mark.integration_test
def test_channels(django_server, redis_server):
    """
    Test django channels.
    Send message to one chat application websockets and waiting for it in another.

    Listed as parameter fixtures run all the servers necessary for the test
    """
    sender = websocket.create_connection(f'ws://{django_server}/ws/chat/test/')
    sender_channel_name = sender.recv()
    print(f'Open sender channel {sender_channel_name}')
    listener = websocket.create_connection(f'ws://{django_server}/ws/chat/test/')
    listener_channel_name = listener.recv()
    print(f'Open listener channel name {listener_channel_name}')

    sent_message = 'Hello, World'
    sender.send(json.dumps({'message': sent_message}))
    received_message = listener.recv()
    assert sent_message == json.loads(received_message)['message']
