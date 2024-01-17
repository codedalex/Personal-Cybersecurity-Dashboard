
from django.urls import path, include
from . import views
from .views import register, CustomLogoutView, CustomPasswordResetView, accounts_home, CustomLogin, create_profile, UserProfileDeleteView, logout_user, set_security_questions
from .views import email_confirmation_pending, invalid_confirmation_link, email_confirmation_success, send_sms_verification, verify_sms_code, csrf_failure_view, answer_security_questions
from .views import reset_password, forgot_password, confirm_email, verify_2fa_code, enable_2fa, enter_2fa_code, dashboard, update_profile, disable_2fa, CustomPasswordChangeView, CustomPasswordChangeDoneView


handler403 = csrf_failure_view 

urlpatterns = [
    path('accounts/', include('allauth.urls')),
    path('accounts', accounts_home, name='accounts_home'),
    path('register/', register, name='register'),
    path('login/', CustomLogin.as_view(), name='login'),
    path('logout/', logout_user, name='logout'),
    path('password_reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('accounts_home/', accounts_home, name='accounts_home'),
    path('accounts_home/<int:user_id>/', views.accounts_home, name='accounts_home'),
    path('user/create_profile/<int:user_id>/', create_profile, name='create_profile'),
    path('user/profile_delete/<int:user_id>/', UserProfileDeleteView.as_view(), name='profile_delete'),
    path('authentication/set_security_questions/<int:user_id>/', set_security_questions, name='set_security_questions'),
    path('user/forgot_password/', forgot_password, name='forgot_password'),
    path('answer_security_questions/', answer_security_questions, name='answer_security_questions'),
    path('user/reset_password/<str:uidb64>/<str:token>/', reset_password, name='reset_password'),
    path('user/password_change/', CustomPasswordChangeView.as_view(), name='password_change'),
    path('user/password_change/done/', CustomPasswordChangeDoneView.as_view(), name='custom_password_change_done'),
    path('registration/confirm_email/<str:uidb64>/<str:token>/', confirm_email, name='confirm_email'),
    path('user/enable_2fa/<int:user_id>/', enable_2fa, name='enable_2fa'),
    path('authentication/verify_2fa_code/', verify_2fa_code, name='verify_2fa_code'),
    path('user/enter_2fa_code/<int:user_id>/', enter_2fa_code, name='enter_2fa_code'),
    path('dashboard/', dashboard, name='dashboard'),
    path('user/update_profile/<int:user_id>/', update_profile, name='update_profile'),
    path('disable_2fa/', disable_2fa, name='disable_2fa'),
    path('authentication/email-confirmation-pending/<str:uidb64>/<int:user_id>/', email_confirmation_pending, name='email_confirmation_pending'),
    path('authentication/invalid-confirmation-link/<int:user_id>/', views.invalid_confirmation_link, name='invalid_confirmation_link'),
    path('authentication/email-confirmation-success/<int:user_id>/', email_confirmation_success, name='email_confirmation_success'),
    path('authentication/send_sms_verification/<int:user_id>/', views.send_sms_verification, name='send_sms_verification'),
    path('authentication/verify_sms_code/<int:user_id>/', verify_sms_code, name='verify_sms_code'),


]