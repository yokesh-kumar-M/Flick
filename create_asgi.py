import os

services = [
    ('access_service', 'access_project'),
    ('auth_service', 'auth_project'),
    ('catalog_service', 'catalog_project'),
    ('gateway', 'gateway_project'),
    ('notification_service', 'notification_project'),
    ('recommendation_service', 'recommendation_project'),
    ('streaming_service', 'streaming_project'),
]

for service, project in services:
    path = f"{service}/{project}/asgi.py"
    with open(path, "w") as f:
        f.write(f"""import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', '{project}.settings')

application = get_asgi_application()
""")
    print(f"Created {path}")
