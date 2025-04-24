import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "buyshop.settings")
django.setup()

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
# from buyshop.middleware import JWTMiddleware  # Import custom JWT middleware

application = ProtocolTypeRouter({
    "http": get_asgi_application(),  # Handles HTTP requests
})
