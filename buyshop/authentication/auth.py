from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.settings import api_settings
import uuid
from .models import Buyer, Seller
import logging

logger = logging.getLogger(__name__)

class CustomJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        """
        Handle UUID-based IDs for Buyer and Seller models based on user_type,
        which is extracted from cookies instead of the token.
        """
        try:
            user_id = validated_token.get(api_settings.USER_ID_CLAIM)
            
            logger.info(f"Extracted id from token: {user_id}")
            
            if user_id is None:
                raise InvalidToken("Token is missing or invalid.")

            try:
                user_id = uuid.UUID(user_id)  # Convert user_id to UUID
            except ValueError:
                raise InvalidToken("User ID in token is not a valid UUID")

            try:
                user = Buyer.objects.get(id=user_id) 
                logger.info(f"Found Buyer with id: {user_id}")
                return user
            except Buyer.DoesNotExist:
                try:
                    user = Seller.objects.get(id=user_id)
                    logger.info(f"Found Seller with id: {user_id}")
                    return user
                except Seller.DoesNotExist:
                    logger.info(f"No user found with id: {user_id}")
                    raise InvalidToken("Seller not found")
        except Exception as e:
            logger.error(f"Error fetching user: {str(e)}")
            raise InvalidToken(f"Error fetching user: {str(e)}")
