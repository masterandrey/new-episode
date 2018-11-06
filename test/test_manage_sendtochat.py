import pytest
import websocket
import json
import subprocess
from conftest import PYTHON_COMMAND


#@pytest.mark.integration_test
def test_manage_sendtochat(django_server, redis_server):
    """
    Test django manage command sendtochat.
    * Start django server and connect to websocket.
    * Execute the command.
    * Check that the message received by the websocket
    """
    def get_message(data: str) -> str:
        try:
            message = json.loads(data)['message']
        except:
            assert False, f'Cannot decode message from received data "{data}"'
        return message
    chat_room = 'room'
    listener = websocket.create_connection(f'ws://{django_server}/ws/chat/{chat_room}/')
    listener_channel_name = get_message(listener.recv())
    print(f'Open listener channel "{listener_channel_name}"')

    sent_message = 'Hello, World'
    print(f'Executing django manage command sendtochat {chat_room} {sent_message}')
    django_process = subprocess.Popen(
        [PYTHON_COMMAND, 'manage.py', 'sendtochat', f'{chat_room}', f'{sent_message}'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    print(django_process.communicate())
    received_message = get_message(listener.recv())
    assert sent_message == received_message
