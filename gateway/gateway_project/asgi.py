import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gateway_project.settings')

_django_app = get_asgi_application()


async def application(scope, receive, send):
    """ASGI wrapper that handles lifespan events to close the shared httpx
    client on shutdown so we don't leak connections."""
    if scope['type'] == 'lifespan':
        while True:
            message = await receive()
            if message['type'] == 'lifespan.startup':
                await send({'type': 'lifespan.startup.complete'})
            elif message['type'] == 'lifespan.shutdown':
                try:
                    from frontend.proxy import aclose_async_client
                    await aclose_async_client()
                except Exception:
                    pass
                await send({'type': 'lifespan.shutdown.complete'})
                return
    else:
        await _django_app(scope, receive, send)
