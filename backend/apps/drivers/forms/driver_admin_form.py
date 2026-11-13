from django import forms

from apps.drivers.models import Driver

# Same rule as DriverRegisterSerializer.password
MIN_PASSWORD_LENGTH = 6


class DriverAdminForm(forms.ModelForm):
    """
    The admin never sees or types password_hash. Before, the hash was a plain text field:
    typing a password there stored it unhashed (and the driver could no longer log in).
    """
    new_password = forms.CharField(
        label="New password",
        required=False,
        strip=False,
        min_length=MIN_PASSWORD_LENGTH,
        widget=forms.PasswordInput(render_value=False),
        help_text="Leave empty to keep the current password. Setting one logs the driver out everywhere.",
    )

    class Meta:
        model = Driver
        exclude = ['password_hash']

    def clean_new_password(self):
        password = self.cleaned_data.get('new_password')
        # A driver added in the admin needs a password to log in at all
        if not self.instance.pk and not password:
            raise forms.ValidationError("Set a password for the new driver.")
        return password
