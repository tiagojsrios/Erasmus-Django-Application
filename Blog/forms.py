from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .fields import MultiFileField


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', )


class UploadForm(forms.Form):
    attachments = MultiFileField(min_num=1, max_num=3, max_file_size=1024*1024*5)

