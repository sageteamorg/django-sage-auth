from sage_auth.forms import UserLoginForm
from sage_auth.mixins.login import LoginViewMixin


class LoginView(LoginViewMixin):
    form_class = UserLoginForm
    template_name = "login.html"

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)
