from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from django.db.models.query_utils import Q
from .tokens import account_activation_token
from .forms import UserRegistrationForm, UserLoginForm, PasswordForgotForm, SetNewPasswordForm


class LoginView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            form = UserLoginForm()
            return render(request, 'user_app/login.html', {'form': form})

        return redirect('user_app:dashboard')

    def post(self, request):
        form = UserLoginForm(request=request, data=request.POST)

        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
            )

            if user is not None:
                login(request, user)
                return redirect('user_app:dashboard')

            messages.error(request, 'Wrong login or password')
            return redirect('user_app:login')

        messages.error(request, 'Form error')
        return redirect('user_app:login')


def activate(request, uidb64, token):
    User = get_user_model()

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)

    except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
        print(e)
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Thanks for confirmation. Now you can login.')
        return redirect('user_app:login')

    else:
        messages.error(request, 'Activation link is invalid!')
        return redirect('user_app:login')


def activate_email(request, user, to_email):
    mail_subject = 'Activate your account.'

    message = render_to_string('user_app/activate.html', {
        'user': user.username,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http'
    })

    email = EmailMessage(mail_subject, message, to=[to_email])

    if email.send():
        messages.success(request, 'Please check your email')

    else:
        messages.error(request, f'Problem sending email')


def password_reset_request(request):
    if not request.user.is_authenticated:
        if request.method == 'POST':
            form = PasswordForgotForm(request.POST)
            if form.is_valid():
                user_email = form.cleaned_data['email']
                associated_user = get_user_model().objects.filter(Q(email=user_email)).first()
                if associated_user:
                    subject = "Password Reset request"
                    message = render_to_string("user_app/template_forgot_password.html", {
                        'user': associated_user,
                        'domain': get_current_site(request).domain,
                        'uid': urlsafe_base64_encode(force_bytes(associated_user.pk)),
                        'token': account_activation_token.make_token(associated_user),
                        "protocol": 'https' if request.is_secure() else 'http'
                    })
                    email = EmailMessage(subject, message, to=[associated_user.email])
                    if email.send():
                        messages.success(request,
                                         """
                                         <h2>Password reset sent</h2><hr>
                                         <p>
                                             We've emailed you instructions for setting your password, if an account exists with the email you entered. 
                                             You should receive them shortly.<br>If you don't receive an email, please make sure you've entered the address 
                                             you registered with, and check your spam folder.
                                         </p>
                                         """
                                         )
                    else:
                        messages.error(request, "Problem sending reset password email, <b>SERVER PROBLEM</b>")

                return redirect('main_app:index')

            for key, error in list(form.errors.items()):
                if key == 'captcha' and error[0] == 'This field is required.':
                    messages.error(request, "You must pass the reCAPTCHA test")
                    continue

        form = PasswordForgotForm()
        return render(request=request, template_name="user_app/forgot_password.html", context={"form": form})

    return redirect('user_app:dashboard')


def password_reset_confirm(request, uidb64, token):
    User = get_user_model()

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)

    except:
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        if request.method == 'POST':
            form = SetNewPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Password has been changed. You may log in.")
                return redirect('main_app:index')

            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)

        form = SetNewPasswordForm(user)
        return render(request, 'user_app/password_reset_confirm.html', {'form': form})

    else:
        messages.error(request, "Link is expired")

    messages.error(request, 'Something went wrong, redirecting back to Homepage')
    return redirect("main_app:index")


class RegisterView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            form = UserRegistrationForm()
            return render(request, 'user_app/register.html', {'form': form})

        return redirect('user_app:dashboard')

    def post(self, request):
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            activate_email(request, user, form.cleaned_data.get('email'))
            return redirect('user_app:login')

        else:
            messages.error(request, 'Form not valid')
            return redirect('user_app:register')


class DashboardView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return render(request, 'user_app/dashboard.html')

        return redirect('user_app:login')


class AccountSettings(View):
    def get(self, request):
        if request.user.is_authenticated:
            user = request.user
            form = SetNewPasswordForm(user)
            return render(request, 'user_app/account_settings.html', {'form': form})

        return redirect('user_app:login')

    def post(self, request):
        if request.user.is_authenticated:
            user = request.user
            form = SetNewPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Your password has been changed')
                return redirect('user_app:login')

            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)
                return redirect('user_app:account_settings')

        return redirect('user_app:login')


@login_required
def logout_user(request):
    logout(request)
    return redirect('user_app:login')
