from django.core.exceptions import PermissionDenied


class UserException(PermissionDenied):
    """Base class for user-related exceptions."""

    pass


class UserNotFoundException(UserException):
    """Exception raised when a user is not found."""

    pass


class UserBlockedException(UserException):
    """Exception raised when a user is blocked."""

    pass


class UserInactiveException(UserException):
    """Exception raised when a user is inactive."""

    pass
