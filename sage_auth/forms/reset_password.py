from django.contrib.auth.forms import SetPasswordForm
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class ResetPasswordConfrimFormMixin(SetPasswordForm):
    class Meta:
        model = settings.AUTH_USER_MODEL

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for _name, field in self.fields.items():
            field.widget.attrs.update({"class": "form-control"})
