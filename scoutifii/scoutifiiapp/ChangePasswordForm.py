from django import forms
from django.contrib.auth import password_validation

class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(label='Current Password', widget=forms.PasswordInput)
    new_password1 = forms.CharField(label='New Password', widget=forms.PasswordInput)
    new_password2 = forms.CharField(label='Confirm New Password', widget=forms.PasswordInput)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        old_password = cleaned_data.get('old_password')
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')
        if new_password1 != new_password2:
            self.add_error('new_password1', 'Passwords do not match')
        if not password_validation.validate_password(new_password1, None):
            self.add_error('new_password1', 'Password is not valid')
        if not self.user.check_password(old_password):
            self.add_error('old_password', 'Incorrect password')