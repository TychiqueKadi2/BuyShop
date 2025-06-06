# toota/middleware.py
import logging
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from channels.db import database_sync_to_async
from authentication.models import Buyer, Seller

logger = logging.getLogger(__name__)

@database_sync_to_async
def get_buyer_or_seller_from_jwt(token):
    try:
        validated_token = AccessToken(token)
        user_id = validated_token['user_id']
        try:
            seller = Seller.objects.get(id=user_id)
            logger.info(f"Authenticated as Seller: {user_id}")
            return seller
        except Seller.DoesNotExist:
            try:
                buyer = Buyer.objects.get(id=user_id)
                logger.info(f"Authenticated as Buyer: {user_id}")
                return buyer
            except Buyer.DoesNotExist:
                logger.error(f"No Buyer or Seller found for ID: {user_id}")
                return AnonymousUser()
    except Exception as e:
        logger.error(f"Token validation failed: {e}")
        return AnonymousUser()

class JWTMiddleware:
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        logger.info("JWT Middleware: Starting")
        headers = dict(scope["headers"])
        if b"authorization" in headers:
            auth_header = headers[b"authorization"].decode()
            if auth_header.startswith("Bearer "):
                token = auth_header.split("Bearer ")[1]
                scope["user"] = await get_user_or_driver_from_jwt(token)
            else:
                scope["user"] = AnonymousUser()
                logger.warning("JWT Middleware: No Bearer token in Authorization header")
        else:
            scope["user"] = AnonymousUser()
            logger.warning("JWT Middleware: No Authorization header provided")

        logger.info("JWT Middleware: Calling inner application")
        result = await self.inner(scope, receive, send)
        logger.info("JWT Middleware: Inner application completed")
        return result
