from django.urls import path
from . import views

app_name = 'user_app'

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('forgot_password/', views.password_reset_request, name="forgot_password"),
    path('reset/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('account_settings/', views.AccountSettings.as_view(), name='account_settings'),
    path('logout/', views.logout_user, name='logout'),
]
