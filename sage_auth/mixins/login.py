import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext as _

from sage_auth.helpers.exceptions import (
    UserBlockedException,
    UserInactiveException,
    UserNotFoundException,
)
from sage_auth.repository.services import LoginService

logger = logging.getLogger(__name__)


class LoginViewMixin(LoginView):
    username_field_name = "username"
    password_field_name = "password"

    def form_valid(self, form):
        identifier = form.cleaned_data.get(self.username_field_name)
        password = form.cleaned_data.get(self.password_field_name)

        logger.info("Attempting login for identifier: %s", identifier)

        service = LoginService(identifier, password)

        try:
            if service.handle_login():
                logger.info("Login successful for: %s", identifier)
                return super().form_valid(form)

        except UserNotFoundException as e:
            logger.warning("Login failed: User not found (%s)", identifier)
            messages.error(self.request, str(e))
        except UserBlockedException as e:
            logger.warning("Login failed: User blocked (%s)", identifier)
            messages.error(self.request, str(e))
        except UserInactiveException as e:
            logger.warning("Login failed: User inactive (%s)", identifier)
            strategy = getattr(settings, "AUTH_STRATEGY", "email")
            if strategy == "email":
                messages.warning(
                    self.request,
                    _("An email has been sent to reactivate your account."),
                )
            elif strategy == "phone_number":
                messages.warning(
                    self.request, _("An SMS has been sent to reactivate your account.")
                )
            self.request.session["otp_identifier"] = identifier
            return redirect(reverse_lazy("otp_verification"))

        logger.info("Redirecting back to login after failed attempt.")
        return redirect(reverse_lazy("login"))

    def form_invalid(self, form):
        logger.warning("Login form validation failed. Errors: %s", form.errors)
        messages.error(self.request, _("Please correct the errors below."))
        return super().form_invalid(form)
