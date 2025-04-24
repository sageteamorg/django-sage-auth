from django.contrib.auth import authenticate
from django.utils.translation import gettext as _

from sage_auth.helpers.exceptions import (
    UserBlockedException,
    UserInactiveException,
    UserNotFoundException,
)
from sage_auth.repository.services.user_service import UserService


class LoginService:
    def __init__(self, identifier, password):
        self.identifier = identifier
        self.password = password
        self.user = None
        self.user_service = UserService()

    def authenticate_user(self):
        """
        Authenticate the user based on identifier and password.
        """
        self.user = authenticate(username=self.identifier, password=self.password)
        if self.user is None:
            raise UserNotFoundException(_("Invalid credentials."))
        return True

    def is_user_blocked(self):
        """
        Check if the user is blocked.
        """
        if self.user.is_block:
            raise UserBlockedException(
                _("Your account is blocked. Please contact support.")
            )

    def is_user_active(self):
        """
        Check if the user is active.
        """
        if not self.user.is_active:
            raise UserInactiveException(
                _("Your account is inactive. Reactivation is required.")
            )

    def handle_login(self):
        """
        Handle login logic: check blocked and active status.
        """
        self.user = self.user_service.get_user(self.identifier)

        if not self.user:
            raise UserNotFoundException(_("No user found with this identifier."))

        self.is_user_blocked()
        self.is_user_active()

        if not self.authenticate_user():
            raise UserNotFoundException(_("Invalid credentials."))
        return True
