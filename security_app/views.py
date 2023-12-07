
from django.shortcuts import render, redirect, get_object_or_404
from security_app.models import CustomUser, SecurityGroup, AuditTrail
from django_otp.plugins.otp_totp.models import TOTPDevice
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden
from django.http import Http404
from django.views.generic.edit import DeleteView
from django.core.mail import send_mail
from django.core.files import File
from django.conf import settings
from pathlib import Path
import base64, logging, qrcode, os
from django.utils import timezone
from django.contrib.auth import views as auth_views
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from urllib.parse import parse_qs, urlparse
from django.core.files.images import ImageFile
from django.contrib import messages, auth
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth import authenticate,  login as auth_login, logout, get_user_model
from django.contrib.auth.views import LoginView,LogoutView, PasswordResetView
from .forms import  CustomUserCreationForm, CustomAuthenticationForm, CustomPasswordResetForm, UserProfileForm, SecurityQuestionForm, SecurityAnswerForm
from .models import CustomUser, AuditTrail
from .utils import send_sms_verification_code, parse_user_agent, get_screen_resolution, get_geolocation, generate_device_identifier, get_network_info
from .validators import calculate_password_strength
from django.contrib.auth.hashers import make_password

# Create your views here.

logger = logging.getLogger(__name__)

def accounts_home(request, user_id=None):
    if request.user.is_authenticated:
        if user_id is not None:
            # Fetch the user based on the user_id from the URL
            user = get_object_or_404(CustomUser, id=user_id)

            # Check if the email is confirmed
            if not user.email_confirmed:
                # Redirect to email confirmation pending if email is not confirmed
                return render(request, 'authentication/email_confirmation_pending.html', {'user_id': user_id})

            # Check if the phone number is confirmed
            # if not user.phone_number_verified:
            #     # Redirect to phone number confirmation if phone number is not confirmed
            #     return render(request, 'phone_confirmation_pending.html', {'user_id': user_id})

            # render user accounts home
            return render(request, 'accounts_home.html', {'user': request.user})
            
        else:
            # redirect to an appropriate page or show an error
            messages.error(request, 'User ID not provided in the URL.')
            return HttpResponse('User ID not provided in the URL.')
    else:
        return render(request, 'accounts_home.html')


def register(request):
    """Handles user registration process."""

    if request.method == 'POST':
        """User submitted registration form."""
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            """Form data is valid, create user account."""
            user = form.save()

            """Send confirmation email to user."""
            current_site = get_current_site(request)
            subject = "Activate Your Account"
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            message = render_to_string('registration/confirmation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uidb64': uidb64,
                'token': token,
            })

            user.email_user(subject, message)

            """Redirect user to confirmation page."""
            messages.success(request, "Account created successfully. Please check your email to confirm.")
            return redirect('email_confirmation_pending', uidb64=uidb64, user_id=user.id)
    else:
        """User request is GET, create empty registration form."""
        form = CustomUserCreationForm()

    """Render registration form to user."""
    return render(request, 'registration/register.html', {'form': form})


def confirm_email(request, uidb64, token):
    User = get_user_model()

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        
        # Check if the email is already confirmed
        if user.email_confirmed:
            messages.info(request, 'Email already confirmed. Please confirm your phone number.')
            return redirect('email_confirmation_success', user_id=user.id)
        else:
            # mark email as confirmed
            user.email_confirmed = True
            user.save()
            messages.success(request, 'Email confirmed successfully. You can now confirm your Phone Number')
            return redirect('email_confirmation_success', user_id=user.id)
    else:
        raise Http404('Invalid confirmation link.')

def email_confirmation_success(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    return render(request, 'authentication/email_confirmation_success.html', {'user': user})


def email_confirmation_pending(request, uidb64, user_id=None):
    user = get_object_or_404(CustomUser, id=user_id)

    if user.email_confirmed:
        # If the email is confirmed, redirect to the login page
        messages.info(request, 'Email already confirmed. Please login.')
        return redirect('login')
    else:
        # if the email is not confirmed, render the pending template
        return render(request, 'authentication/email_confirmation_pending.html', {'user_id': user_id})



def invalid_confirmation_link(request):
    return render(request,'auhentication/invalid_confirmation_link.html')

# @login_required
def send_sms_verification(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)

    if user.phone_number_verified:
        messages.info(request, 'Phone number already verified.')
        return render(request, 'accounts_home.html', {'user': user})

    # Send SMS verification code
    send_sms_verification_code(user.phone_number, user.id)

    messages.success(request, 'SMS verification code sent. Please check your phone.')
    return render(request, 'authentication/sms_verification.html', {'user': user})

# @login_required
def verify_sms_code(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)

    if request.method == 'POST':
        entered_code = request.POST.get('sms_verification_code')

        if send_sms_verification_code(user.id, entered_code):
            # code is valid, mark the phone number as verified
            user.phone_number_verified = True
            user.save()

            messages.success(request, 'Phone number verified successfully.')
            return render(request, 'accounts_home.html', {'user': user})
        else:
            messages.error(request, 'Invalid verification code.')
    return render(request, 'authenticaion/verify_sms_code.html', {'user': user})

class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm

class CustomLogin(auth_views.LoginView):

    def post(self, request, *args, **kwargs):

        if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']

            # Print debug information
            print(f"Attempting to authenticate user: {username}")

            user = authenticate(request, username=username, password=password)

            if user is not None:
                auth_login(request, user)
                messages.success(request, 'Login successful!')

                if request.user.is_authenticated:
                    if request.user.is_2fa_enabled:
                        return redirect(reverse('enter_2fa_code', kwargs={'user_id': user.id}))
                    else:
                        print("2FA not enabled, redirecting to accounts_home directly.")
                        return redirect(reverse('accounts_home', kwargs={'user_id': user.id}))


            else:
                print(f"Authentication failed for user: {username}")
                messages.error(request, 'Login failed. Please check your credentials.')
                return redirect('login')  # Add this line to exit the login process on failed authentication

        else:
            return render(request, 'login.html')



# Logout Fuction
def logout_user(request):
    logout(request)
    # Display success message
    messages.success(request, 'Logout Successfull!')
    # Redirect to home page
    return redirect('login')

class CustomLogoutView(LogoutView):
    pass



@login_required
def create_profile(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)

    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()

            if not (user.security_question_1 and user.security_question_2):
                return redirect('set_security_questions', user_id=user.id)

            messages.success(request, f"Profile created successfully")
            return render(request, 'accounts_home.html', {'user': user})
    else:
        form = UserProfileForm(instance=user)
    return render(request, 'user/create_profile.html', {'form': form})

@login_required
def update_profile(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)

    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()

            messages.success(request, "Profile updated successfully")
            return redirect("accounts_home", user_id=user.id)
    else:
        form = UserProfileForm(instance=user)

    return render(request, 'user/update_profile.html', {'form': form})

# @login_required
class UserProfileDeleteView(DeleteView):
    model = CustomUser
    success_url = reverse_lazy('accounts_home')
    template_name = 'user/profile_delete_confirm.html'

    def get_object(self, queryset=None):
        return self.request.user

@login_required        
def set_security_questions(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == "POST":
        form1 = SecurityQuestionForm(request.POST, instance=user)
        if form1.is_valid():
            if form1.cleaned_data.get('security_question_1') and form1.cleaned_data.get('security_question_2'):
                # save the security questions associated with the user
            
                # save the security questions associated with the user
                form1.save()
                messages.success(request, "Security questions set successfully")
                return redirect('enable_2fa', user_id=user.id)
            else:
                messages.error(request, "Please answer both security questions.")
    else:
        form1 = SecurityQuestionForm()

    return render(request, 'authentication/Set_security_questions.html', {'form': form1})

@csrf_protect
def forgot_password(request):
    if request.method == "POST":
        form = SecurityAnswerForm(request.POST)
        if form.is_valid():
            user = form.get_user()
            if user:
                # User and security answers are correct
                # Generate a reset token and send an email with a reset link
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                reset_url = reverse('reset_password', kwargs={'uidb64': uid, 'token': token})

                # Send a password reset email
                send_mail(
                    'Password Reset',
                    f'Use the following link to reset your password: {request.build_absolute_uri(reset_url)}',
                    'alexmutonga3@gmail.com',  # Replace with your email
                    [user.email],
                    fail_silently=False,
                )

                messages.success(request, 'Password reset link has been sent to your email.')
                return redirect('login')
            else:
                messages.error(request, 'Invalid security answers. Please try again.')
    else:
        form = SecurityAnswerForm()

    return render(request, 'user/forgot_password.html', {'form': form})

    


def reset_password(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = CustomPasswordResetForm(user, request.POST)
            if form.is_valid():
                # Update the password strength
                user.password_strength = calculate_password_strength(form.cleaned_data['password1'])
                
                # Update the last password change timestamp
                user.last_password_change = timezone.now()

                # Save the user
                user.password = make_password(form.cleaned_data['password1'])
                user.save()

                return render(request, 'password_reset_done.html')
        else:
            form = CustomPasswordResetForm(user, initial={'user': user})  # Pass user=user here
        return render(request, 'user/reset_password.html', {'form': form, 'uidb64': uidb64, 'token': token})

    else:
        messages.error(request, 'Invalid reset link.')
        return redirect('login')


@login_required
def enable_2fa(request, user_id):
    user = request.user

    # Check if 2FA is already enabled
    if user.is_2fa_enabled:
        messages.info(request, "Two-Factor Authentication is already enabled.")
        return redirect("accounts_home")

    # Check if the user already has a confirmed TOTP device
    totp_device = TOTPDevice.objects.filter(user=request.user, confirmed=True).first()

    if not totp_device:
        # If the user doesn't have a confirmed TOTP device, create one
        totp_device = TOTPDevice.objects.create(user=request.user, confirmed=True)

    # Generate TOTP secret
    totp_secret = totp_device.config_url

    # Extract actual TOTP secret from the URL
    actual_totp_secret = parse_qs(urlparse(totp_secret).query)['secret'][0]

    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    # totp_secret = request.session.get('totp_secret', '')
    img_qr = qrcode.make(totp_secret)
    img_qr = img_qr.resize((300, 300))  # adjust the size accordingly

    # Load the logo image
    logo_path = os.path.join(settings.BASE_DIR, 'security_app', 'images', 'qrcode.png')
    logo_img = Image.open(logo_path)

    # Convert the logo image to RGB mode without an alpha channel
    logo_img = logo_img.convert('RGB')

    # Resize the logo image to your desired size
    logo_img = logo_img.resize((50, 50))  # adjust the size accordingly

    # Create a blank image with a white background
    combined_img = Image.new("RGB", (max(img_qr.width, logo_img.width), max(img_qr.height, logo_img.height)), "white")

    # Paste the QR code onto the blank image
    combined_img.paste(img_qr, ((combined_img.width - img_qr.width) // 2, (combined_img.height - img_qr.height) // 2))

    # Paste the logo onto the combined image
    combined_img.paste(logo_img, ((combined_img.width - logo_img.width) // 2, (combined_img.height - logo_img.height) // 2))

    # Save the combined image to BytesIO
    img_bytes_io = BytesIO()
    combined_img.save(img_bytes_io, format='PNG')
    img_data = img_bytes_io.getvalue()

    # Convert BytesIO to base64
    totp_secret_data_uri = "data:image/png;base64," + base64.b64encode(img_data).decode()

    # Pass both totp_secret_data_uri and actual_totp_secret to the template
    context = {
        'totp_secret': totp_secret_data_uri,
        'actual_totp_secret': actual_totp_secret,
    }

    if not (user.security_question_1 and user.security_question_2):
        # If security questions are not set, redirect to set them first
        messages.error(request, 'Please set security questions before enabling 2FA.')
        return redirect('set_security_questions', user_id=user.id)

    if request.session.get('top_verified', False):
        # If 2FA setup is complete, update user status and redirect
        user.is_2fa_enabled = True
        user.security_questions_answered = True
        user.save()
        del request.session['top_verified']
        return render(request, 'accounts_home', user_id=user.id)
    else:
        # If 2FA setup is not complete, show an error message
        messages.error(request, 'Please complete the 2FA setup process.')
        return render(request, 'user/enable_2fa.html', context)


def enter_2fa_code(request, user_id):
    user = request.user

    # Check if 2FA is enabled for the user
    if not user.is_2fa_enabled:
        messages.error(request, "You must first enable two factor authentication.")
        return redirect('accounts_home')

    if request.method == 'POST':
        totp_code = request.POST.get('totp_code')
        totp_device = TOTPDevice.objects.get(user=request.user)

        if totp_device.verify_token(totp_code):
            # Code is valid, log in the user
            request.session['top_verified'] = True
            return redirect('accounts_home', user_id=request.user.id)
        else:
            messages.error(request, 'Invalid 2FA code. Please try again.')
    return render(request, 'user/enter_2fa_code.html', {'user':user})

@login_required
def verify_2fa_code(request):
    if request.method == 'POST':
        verification_code = request.POST.get('verification_code')

        # Get all TOTPDevice objects for the user
        totp_devices = TOTPDevice.objects.filter(user=request.user)

        # Verify the verification code for each TOTPDevice
        for totp_device in totp_devices:
            if totp_device.verify_token(verification_code):
                # Code is valid, log in the user
                messages.success(request, 'Authenticated successfully.')

                # Update user's 2FA status
                request.user.is_2fa_enabled = True
                request.user.save()

                return redirect('accounts_home', user_id=request.user.id)

        # If none of the TOTPDevices had a valid code
        messages.error(request, 'Invalid Verification code. Please try again.')

    return render(request, 'authentication/verify_2fa_code.html')

@login_required
def disable_2fa(request):
    user = request.user

    if not (user.security_question_1 and user.security_question_2):
        # If security questions are not set, prompt the user to set them first
        messages.error(request, 'Please set security questions before disabling 2FA.')
        return redirect('set_security_questions', user_id=user.id)

    if request.method == 'POST':
        form = SecurityAnswerForm(request.POST, instance=user)
        if form.is_valid():
            # Make sure to use the cleaned_data attribute after validating the form
            security_question_1_answer = form.cleaned_data.get('answer_security_1')
            security_question_2_answer = form.cleaned_data.get('answer_security_2')

            # Add print statements for debugging
            print(f"User's answer to security question 1: {security_question_1_answer}")
            print(f"User's answer to security question 2: {security_question_2_answer}")
            print(f"Database answer to security question 1: {user.answer_security_1}")
            print(f"Database answer to security question 2: {user.answer_security_2}")

            # Check if security questions are answered correctly
            if (
                user.answer_security_1 and user.answer_security_2 and
                security_question_1_answer == user.answer_security_1 and
                security_question_2_answer == user.answer_security_2
            ):
                # Disable 2FA
                user.is_2fa_enabled = False
                user.save()

                messages.success(request, 'Two-Factor Authentication disabled successfully.')
                return redirect('login')
            else:
                messages.error(request, 'Incorrect Answers')
        else:
            # Handle form validation errors
            print(form.errors)
            messages.error(request, 'Form validation error')

    return render(request, 'user/disable_2fa.html', {'user': user, 'form': SecurityAnswerForm()})




@login_required
def dashboard(request):
    user = request.user
    password_strength = user.password_strength 
    logger.info('Password Strength: %s', password_strength)

    # Record device information
    user.last_device_info = {
        'user_agent': request.META.get('HTTP_USER_AGENT'),
        'device_type': parse_user_agent(request.META.get('HTTP_USER_AGENT'), component='device_type'),
        'os': parse_user_agent(request.META.get('HTTP_USER_AGENT'), component='os'),
        'browser': parse_user_agent(request.META.get('HTTP_USER_AGENT'), component='browser'),
        'screen_resolution': get_screen_resolution(),
        'ip_address': request.META.get('REMOTE_ADDR'),
        'geolocation': get_geolocation(request.META.get('REMOTE_ADDR')),
        'device_identifier': generate_device_identifier(request),
        'network_info': get_network_info(request),
    }
    user.save()

    # Get data for the dashboard
    password_strength = user.password_strength
    last_device_info = user.last_device_info

    # Extract OS information
    os_info = last_device_info['os']
    os_display = f"{os_info['os_type']} {os_info['os_version']}"

    # Extract browser information
    browser_info = last_device_info['browser']
    browser_display = browser_info['browser_family']

    # Example: Fetch recent audit trail entries
    recent_audits = AuditTrail.objects.filter(user=user).order_by('-timestamp')[:10]

    context = {
        'password_strength': password_strength,
        'last_password_change': user.last_password_change,
        'login_attempts': user.login_attempts,
        'successful_logins': user.successful_logins,
        'failed_login_timestamp': user.failed_login_timestamp,
        'account_created_timestamp': user.account_created_timestamp,
        'account_updated_timestamp': user.account_updated_timestamp,
        'two_factor_method': user.two_factor_method,
        'security_question_reset_attempts': user.security_question_reset_attempts,
        'security_question_reset_timestamp': user.security_question_reset_timestamp,
        'total_time_spent': user.total_time_spent,
        'recent_audits': recent_audits,
        'last_device_used': user.last_device_used,
        'last_device_info': user.last_device_info,
        'device_history': user.device_history,
        'location_history': user.location_history,
        'active_sessions': user.active_sessions,
        'security_alerts': user.security_alerts,
        'os_display': os_display,
        'browser_display': browser_display,
    }

    return render(request, 'dashboard.html', context)





def csrf_failure_view(request, reason=""):
    # get template with csrf_failure name
    template = loader.get_template('csrf_failure.html')
    
    # context with 'reason' as key
    context = {'reason': reason}
    
    # return forbidden HttpResponse with template rendering
    return HttpResponseForbidden(template.render(context, request))



