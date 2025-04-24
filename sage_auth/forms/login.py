import logging

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.utils.translation import gettext_lazy as _
from phonenumber_field.formfields import PhoneNumberField

from sage_auth.helpers.validators import CompanyEmailValidator
from sage_auth.utils import set_required_fields

logger = logging.getLogger(__name__)


class UserLoginForm(forms.ModelForm):
    """
    A mixin for handling dynamic user form fields and validation based on
    specified authentication strategies.
    and create a new user

    This form includes custom fields like
    email, phone number, and username, which are conditionally
    required depending on the chosen authentication strategy.
    It also manages password validation and
    custom error handling for unique constraints on user data.
    """

    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={"placeholder": "Enter password"}),
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={"placeholder": "Confirm password"}),
    )

    class Meta:
        model = get_user_model()
        fields = []

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

        username_field, required_fields = set_required_fields()

        if username_field == "email":
            self.fields["email"] = forms.EmailField(
                required=True, widget=forms.EmailInput(attrs={"placeholder": "Email"})
            )
            self.fields["email"].validators.append(CompanyEmailValidator())

        elif username_field == "phone_number":
            self.fields["phone_number"] = PhoneNumberField(
                region=getattr(settings, "DEFAULT_REGION", "IR"),
                required=True,
                widget=forms.TextInput(attrs={"placeholder": "Phone Number"}),
            )
        elif username_field == "username":
            self.fields["username"] = forms.CharField(
                required=True, widget=forms.TextInput(attrs={"placeholder": "Username"})
            )

        # Add any additional required fields based on strategies
        for field in required_fields:
            if field == "email" and "email" not in self.fields:
                self.fields["email"] = forms.EmailField(
                    required=True,
                    widget=forms.EmailInput(attrs={"placeholder": "Email"}),
                )
                self.fields["email"].validators.append(CompanyEmailValidator())

            if field == "username" and "username" not in self.fields:
                self.fields["username"] = forms.CharField(
                    required=True,
                    widget=forms.TextInput(attrs={"placeholder": "Username"}),
                )
            if field == "phone_number" and "phone_number" not in self.fields:
                self.fields["phone_number"] = PhoneNumberField(
                    region=getattr(settings, "DEFAULT_REGION", "CA"),
                    required=True,
                    widget=forms.TextInput(attrs={"placeholder": "Phone Number"}),
                )

        # Move password fields to the end
        self.fields["password1"] = self.fields.pop("password1")
        self.fields["password2"] = self.fields.pop("password2")

    def clean_password1(self):
        password = self.cleaned_data.get("password1")
        if password:
            try:
                validate_password(password)
            except ValidationError as e:
                logger.warning("Password validation failed: %s", e)
                raise forms.ValidationError(e) from e
        return password

    def clean(self):
        cleaned_data = super().clean()

        email = cleaned_data.get("email")
        phone_number = cleaned_data.get("phone_number")
        username = cleaned_data.get("username")

        if not email and not phone_number and not username:
            logger.warning("Validation failed: No identifier provided.")
            raise forms.ValidationError(
                "You must provide at least one identifier: email, phone number, or username."
            )

        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            logger.warning("Password mismatch during login attempt.")
            raise forms.ValidationError("The two password fields must match.")

        return cleaned_data

    def get_user_data(self):
        """Extract and return user data from cleaned_data."""
        return {
            "email": self.cleaned_data.get("email"),
            "phone_number": self.cleaned_data.get("phone_number"),
            "username": self.cleaned_data.get("username"),
            "password": self.cleaned_data.get("password1"),
        }

    def save(self, commit=True):
        user_data = self.get_user_data()
        User = get_user_model()
        try:
            with transaction.atomic():
                strategy = User.objects.get_authentication_strategies(user_data)
                user = strategy.create_user(user_data)
                logger.info("User created successfully: %s", user)
                return user
        except IntegrityError as error:
            logger.error("User creation failed due to integrity error: %s", error)
            raise ValidationError(
                _("A user with the provided information already exists.")
            ) from error
