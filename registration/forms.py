from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from better_profanity import profanity
import re
from django.core.exceptions import ValidationError

# Create your forms here.

from better_profanity import profanity
import re

class NewUserForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def clean_username(self):
        username = self.cleaned_data.get('username')
        
        # Profanity check
        if profanity.contains_profanity(username):
            raise ValidationError("Username contains inappropriate language.")
        
        # Block admin-like names
        restricted_names = ['admin', 'administrator', 'mod', 'moderator', 'root', 'staff', 'support', 'official']
        if username.lower() in restricted_names:
            raise ValidationError("This username is not allowed.")
        
        # Block excessive numbers (common in spam accounts)
        if re.search(r'\d{5,}', username):
            raise ValidationError("Username cannot contain long sequences of numbers.")
        
        # Minimum length (Django already checks this, but being explicit)
        if len(username) < 3:
            raise ValidationError("Username must be at least 3 characters.")
            
        return username

    def save(self, commit=True):
        user = super(NewUserForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

