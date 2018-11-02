from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import chat.routing
import webui_list.routing


application = ProtocolTypeRouter({
    # (http->django views is added by default)
    'websocket': AuthMiddlewareStack(
        URLRouter(
            chat.routing.websocket_urlpatterns + webui_list.routing.websocket_urlpatterns
        )
    ),
})

channel_routing = {
    # You can name your channel anything you want, you probably see 'websocket.*' in most tutorials.
    'your_channel_name': lambda x: print('Channel Triggered Event!'),
}