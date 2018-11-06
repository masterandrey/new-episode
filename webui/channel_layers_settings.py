"""
Django channel layers settings.
"""
import socket


def channel_layers_settings() -> dict:
    """
    Return empty if REDIS is not up and running.
    So django will start channels without layers.
    """
    host = '127.0.0.1'
    port = 6379
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(5)
    try:
        s.connect((host, port))
        return {
            'default': {
                'BACKEND': 'channels_redis.core.RedisChannelLayer',
                'CONFIG': {
                    "hosts": [(host, port)],
                },
            },
        }
    except ConnectionRefusedError:
        print(f'No REDIS server found at {host}:{port}. Starting without chanels layer..')
        return {}
