from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('verify-email/<uidb64>/<token>/', views.VerifyEmailView.as_view(), name='auth_verify_email'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/details/', views.UserProfileView.as_view(), name='profile_details'),
     path("password-reset/", views.RequestPasswordResetView.as_view(), name="password-reset"),
    path("password-reset-confirm/<uidb64>/<token>/", views.ResetPasswordConfirmView.as_view(), name="password-reset-confirm"),
]
