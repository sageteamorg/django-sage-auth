import logging
from typing import Optional

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist

# Initialize logger
logger = logging.getLogger(__name__)

User = get_user_model()


class UserService:
    """
    Service for retrieving user-related information.
    """

    def get_user(self, identifier: str) -> Optional[User]:
        """
        Retrieve a user by email or phone number, based on the configured authentication methods.

        Args:
            identifier (str): The user's email or phone number.

        Returns:
            User: The retrieved user object if found, or None if no user matches the identifier.

        Raises:
            ValueError: If no valid authentication methods are configured.
            MultipleObjectsReturned: If more than one user matches the identifier.
        """
        # Validate the presence of authentication methods
        email_password_enabled = settings.AUTHENTICATION_METHODS.get(
            "EMAIL_PASSWORD", False
        )
        phone_password_enabled = settings.AUTHENTICATION_METHODS.get(
            "PHONE_PASSWORD", False
        )

        if not email_password_enabled and not phone_password_enabled:
            logger.error("No valid authentication methods are configured in settings.")
            raise ValueError(
                "No valid authentication methods are configured in settings."
            )

        try:
            if email_password_enabled:
                logger.info("Attempting to retrieve user by email.")
                return User.objects.get(email=identifier)
            elif phone_password_enabled:
                logger.info("Attempting to retrieve user by phone number.")
                return User.objects.get(phone_number=identifier)
        except ObjectDoesNotExist:
            logger.warning(f"No user found with identifier: {identifier}")
            return None
        except MultipleObjectsReturned:
            logger.error(
                f"Multiple users found with the identifier: {identifier}. "
                "Ensure unique constraints are in place."
            )
            raise MultipleObjectsReturned(
                "Multiple users found with the same identifier. Ensure unique constraints are in place."
            )

    @staticmethod
    def validate_identifier(identifier: str) -> bool:
        """
        Validate the identifier for basic security and correctness.

        Args:
            identifier (str): The user's email or phone number.

        Returns:
            bool: True if the identifier is valid, False otherwise.
        """
        # Example validation for email or phone number formats
        # This can be extended to use regex or specialized libraries for better validation
        if "@" in identifier:  # Simplistic email validation
            return True
        if identifier.isdigit():  # Simplistic phone number validation
            return True
        logger.warning(f"Invalid identifier format: {identifier}")
        return False
