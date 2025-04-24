from django.urls import reverse_lazy

from ..forms.register import UserCreationForm
from sage_auth.mixins.signup import UserCreationMixin


class RegisterView(UserCreationMixin):
    template_name = "auth/register.html"
    form_class = UserCreationForm
    success_url = reverse_lazy("auth:register-otp-verification")
    already_login_url = "/"
