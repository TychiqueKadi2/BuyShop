from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.settings import api_settings
import uuid
from .models import User  # Reference the unified User model
import logging

logger = logging.getLogger(__name__)

class CustomJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        """
        Handle UUID-based IDs for the unified User model.
        """
        try:
            # Extract the user ID from the token
            user_id = validated_token.get(api_settings.USER_ID_CLAIM)
            logger.info(f"Extracted id from token: {user_id}")

            if user_id is None:
                raise InvalidToken("Token is missing or invalid.")

            # Convert user_id to UUID
            try:
                user_id = uuid.UUID(user_id)
            except ValueError:
                raise InvalidToken("User ID in token is not a valid UUID")

            # Fetch the user from the unified User model
            try:
                user = User.objects.get(id=user_id)
                logger.info(f"Found User with id: {user_id}")
                return user
            except User.DoesNotExist:
                logger.info(f"No user found with id: {user_id}")
                raise InvalidToken("User not found")

        except Exception as e:
            logger.error(f"Error fetching user: {str(e)}")
            raise InvalidToken(f"Error fetching user: {str(e)}")
