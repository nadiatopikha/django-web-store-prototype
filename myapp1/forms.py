from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import *
from django.contrib.auth.forms import UserChangeForm

class CustomUserSignUpForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].label = "Ім'я"
        self.fields['last_name'].label = "Прізвище"
        self.fields['username'].label = "Ім'я користувача"
        self.fields['email'].label = "Електронна пошта"

class CustomUserLoginForm(AuthenticationForm):
    email = forms.EmailField(
        label='Електронна пошта',
        widget=forms.EmailInput(attrs={'autofocus': True})
    )
    password = forms.CharField(
        label='Пароль',
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password'}),
    )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('username', None)
        self.order_fields(['email', 'password'])
        
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'image', 'category']

class CustomUserChangeForm(UserChangeForm):
    password = forms.CharField(widget=forms.PasswordInput(), required=False)

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'username', 'password')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].label = "Ім'я"
        self.fields['last_name'].label = "Прізвище"
        self.fields['username'].label = "Ім'я користувача"
        self.fields['email'].label = "Електронна пошта"
        self.fields['password'].label = "Пароль"