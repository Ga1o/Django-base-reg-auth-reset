from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth import get_user_model


class UserRegistrationForm(UserCreationForm):
    first_name = forms.CharField(label='First Name', widget=forms.TextInput(
        attrs={'class': 'form-control mb-2', 'placeholder': 'Pol Smith'}), max_length=50)
    last_name = forms.CharField(label='Last Name', widget=forms.TextInput(
        attrs={'class': 'form-control mb-2', 'placeholder': 'Pol Smith'}), max_length=50)
    username = forms.CharField(label='Nickname',
                               widget=forms.TextInput(attrs={'class': 'form-control mb-2', 'placeholder': 'Pol Smith'}),
                               max_length=50)
    email = forms.EmailField(label='Your Email', widget=forms.TextInput(
        attrs={'class': 'form-control mb-2', 'placeholder': 'name@gmail.com'}), max_length=100, required=True)
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput(
        attrs={'class': 'form-control mb-2', 'placeholder': '8 chars minimum'}))
    password2 = forms.CharField(label='Password repeat', widget=forms.PasswordInput(
        attrs={'class': 'form-control mb-2', 'placeholder': '8 chars minimum'}))

    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super(UserRegistrationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()

        return user


class UserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)

    username = forms.CharField(label='Email', widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Username or Email'}))
    password = forms.CharField(label='Password',
                               widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))


class SetNewPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(label='Password', widget=forms.PasswordInput(
        attrs={'class': 'form-control mb-2', 'placeholder': '8 chars minimum'}))
    new_password2 = forms.CharField(label='Password repeat', widget=forms.PasswordInput(
        attrs={'class': 'form-control mb-2', 'placeholder': '8 chars minimum'}))


class PasswordForgotForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super(PasswordResetForm, self).__init__(*args, **kwargs)

    email = forms.EmailField(label='Your Email', widget=forms.TextInput(
        attrs={'class': 'form-control mb-2', 'placeholder': 'name@gmail.com'}), max_length=100, required=True)
