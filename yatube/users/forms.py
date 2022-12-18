from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class CreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            'first_name',
            'last_name',
            'username',
            'email'
        )
