

from .validators import CustomPasswordValidator
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser, Permission, Group
from django.core.validators import MinLengthValidator
from django.utils.translation import gettext as _
from django.utils.text import capfirst
from django.utils import timezone
from django.db.models.signals import post_save
from django.contrib.auth.signals import user_logged_in, user_login_failed
from django.dispatch import receiver
from django.contrib.auth import authenticate
from django.contrib.gis.geoip2 import GeoIP2
from .utils import send_sms_verification_code, parse_user_agent, get_screen_resolution, get_geolocation, generate_device_identifier, get_network_info


# Create your models here.
def custom_password_validator():
    return CustomPasswordValidator()

class CustomUser(AbstractUser):
    is_staff = models.BooleanField(default=False)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True, default='default_profile_pic.png')
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, unique=True, blank=True, null=True)
    country = models.CharField(max_length=70, blank=True)
    state = models.CharField(max_length=70, blank=True)
    city = models.CharField(max_length=70, blank=True)
    zipcode = models.CharField(max_length=15, unique=False, blank=True, null=True)
    address1 = models.CharField(max_length=15, unique=False, blank=True, null=True)
    address2 = models.CharField(max_length=15, unique=False, blank=True, null=True)
    security_question_1 = models.CharField(max_length=255, blank=True, null=True)
    answer_security_1 = models.CharField(max_length=255, blank=True, null=True)
    security_question_2 = models.CharField(max_length=255, blank=True, null=True)
    answer_security_2 = models.CharField(max_length=255, blank=True, null=True)
    top_secret = models.CharField(max_length=16, blank=True, null=True)
    is_2fa_enabled = models.BooleanField(default=False)
    two_factor_enabled = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    last_login_ip = models.GenericIPAddressField(blank=True, null=True)
    last_login_timestamp = models.DateTimeField(blank=True, null=True)
    is_locked_out = models.BooleanField(default=False)
    password_validator = CustomPasswordValidator()
    is_2fa_enabled = models.BooleanField(default=False)
    security_questions_answered = models.BooleanField(default=False)
    email_confirmed = models.BooleanField(default=False)
    phone_number_verified = models.BooleanField(default=False)
    last_login_ip = models.GenericIPAddressField(blank=True, null=True)
    last_login_timestamp = models.DateTimeField(blank=True, null=True)
    SECURITY_QUESTION_CHOICES = [
        ('favorite_color', 'What is your favorite color?'),
        ('first_pet', 'What was the name of your first pet?'),
        ('birth_city', 'In which city were you born?'),
        ('favorite_book', 'What is your favorite book?'),
        ('high_school', 'Which high school did you attend?'),
    ]

    security_question_1 = models.CharField(max_length=255, choices=SECURITY_QUESTION_CHOICES, blank=True, null=True)
    answer_security_1 = models.CharField(max_length=255, blank=True, null=True)
    security_question_2 = models.CharField(max_length=255, choices=SECURITY_QUESTION_CHOICES, blank=True, null=True)
    answer_security_2 = models.CharField(max_length=255, blank=True, null=True)

    
    # Dashboard-related fields
    password_strength = models.IntegerField(default=0, help_text="Strength of the user's password.")
    last_password_change = models.DateTimeField(blank=True, null=True, help_text="Timestamp of the last password change.")
    login_attempts = models.IntegerField(default=0, help_text="Number of failed login attempts.")
    login_attempts = models.IntegerField(default=0, help_text="Number of failed login attempts.")
    successful_logins = models.IntegerField(default=0, help_text="Number of successful logins.")
    failed_login_timestamp = models.DateTimeField(blank=True, null=True, help_text="Timestamp of the last failed login attempt.")
    account_created_timestamp = models.DateTimeField(default=timezone.now, help_text="Timestamp when the account was created.")
    account_updated_timestamp = models.DateTimeField(default=timezone.now, help_text="Timestamp when the account was last updated.")
    two_factor_method = models.CharField(max_length=20, blank=True, null=True, help_text="Method used for Two-Factor Authentication (e.g., SMS, Email, App).")
    security_question_reset_attempts = models.IntegerField(default=0, help_text="Number of failed security question reset attempts.")
    security_question_reset_timestamp = models.DateTimeField(blank=True, null=True, help_text="Timestamp of the last failed security question reset attempt.")
    total_time_spent = models.DurationField(default='0:00', help_text="Total time spent on dashboard since account creation or reset")
    last_device_used = models.CharField(max_length=255, blank=True, null=True)
    last_device_info = models.JSONField(default=dict, blank=True, null=True)
    device_history = models.JSONField(default=list)
    location_history = models.JSONField(default=list)
    active_sessions = models.JSONField(default=list)
    security_alerts = models.JSONField(default=list)
    
    # Update your model's save method to handle device and location history
    def save(self, *args, **kwargs):
        if self.last_login_ip:
            # Update device history
            self.device_history.append({
                'device': self.last_device_used,
                'timestamp': self.last_login_timestamp
            })

            #  Update last device informattion
            device_info = {
                "user_agent": request.META['HTTP_USER_AGENT'],
                'device_type': purse_user_agent(request.META.get('HTTP_USER_AGENT')), # Custom function to extract device type
                'os': purse_user_agent(request.META.get("HTTP_USER_AGENT"), componet='os'), #custom function to extract os
                'browser': purse_user_agent(request.META.get(HTTP_USER_AGENT), component='browser'), # Custom function to extract browser
                'screen_resoltion': get_screen_resolution(request), # Custom fuction to get screen resolution
                'ip_address':request.META.get('REMOTE_ADDR'),
                'geolocation': get_geolocation(request.META.get('REMOTE_ADDR')), #Custom function to get geo-location
                'device_identifier': generate_device_identifier(request), # custom function to generate device identifier
                'network_info': get_network_info(request),# custom fucytion to get network info
                # 'country': geolocate(request).country,
                # 'city': geolocate(request).city,

            }

            self.last_device_info = device_info

            # Update location history
            self.location_history.append({
                'location': self.last_login_ip,
                'timestamp': self.last_login_timestamp
            })

            # Update last password change timestamp
            if self.pk is not None:
                original = self.__class__.objects.get(pk=self.pk)
                if not check_password(self.password, original.password):
                    self.last_password_change = timezone.now()

        super().save(*args, **kwargs)

     # Password policies
    password_policy = [
        MinLengthValidator(8, message=_("Password must be at least 8 characters.")),
        CustomPasswordValidator,  # Include the validator directly here
    ]
    password = models.CharField(max_length=128, validators=password_policy)

    def save(self, *args, **kwargs):
        # Capitalize first letters
        self.first_name = capfirst(self.first_name)
        self.last_name = capfirst(self.last_name)
        self.country = capfirst(self.country)
        self.state = capfirst(self.state)
        self.city = capfirst(self.city)
        self.address1 = capfirst(self.address1)
        self.address2 = capfirst(self.address2)

        super().save(*args, **kwargs)

    class Meta:
        permissions = [
            ("can_view_sensitive_data", "Can view sensitive data"),
            # Add more custom permissions as needed
        ]

    def assign_default_permissions(self):
        """Assigns default permissions to the user."""
        permission = Permission.objects.get(codename='can_view_sensitive_data')
        self.user_permissions.add(permission)
        # group, created = Group.objects.get_or_create(name="Default")
        # self.groups.add(group)
    
    def has_security_questions(self):
        return self.answer_security_1 is not None and self.answer_security_2 is not None

    def disable_2fa(self):
        self.is_2fa_enabled = False
        self.save()

    def disable_security_questions(self):
        self.security_question_1 = None
        self.security_question_2 = None
        self.answer_security_1 = None
        self.answer_security_2 = None
        self.save()


class UserRequest(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    problem_description = models.TextField(default='')
    resolved = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

@receiver(user_logged_in)
def user_logged_in_handler(sender, request, user, **kwargs):
    # Increament Login attempts on each Login
    user.login_attempts += 1

    # If the login is successfull, increament successful logins
    if user.is_authenticated:
        user.successful_logins += 1
    # Update the last login ip and the last login timestamp when the user logs in
    user.last_login_ip = request.META.get('REMOTE_ADDR')
    user.last_login_timestamp = timezone.now()

     # Record device information
    user.last_device_used = request.META.get('HTTP_USER_AGENT')  # Example, you can customize this based on your needs

    # Update the device Histoty
    user.device_history.append({

        'device' : user.last_device_used,
        'timestamp': user.last_login_timestamp.isoformat() # convert timestamp into ISO format
    })

    # Save the changes
    user.save()

@receiver(user_login_failed)
def user_login_failed_handler(sender, credentials, request, **kwargs):
    # Retrieve the user instance using the provided credentials and request
    username = credentials.get('username')
    password = credentials.get('password')

    # Retrieve the user using the custom user model
    user = get_user_model().objects.filter(username=username).first()

    # If the user exists and the login attempt failed, increament login attempts
    if user:
        user.login_attempts += 1
        user.failed_login_timestamp = timezone.now()
        # Save the changes
        user.save()

# Create Custom User Groups
class SecurityGroup(Group):
    class Meta:
        proxy = True

# Add default permissions to the custom user group
# security_group, created = SecurityGroup.objects.get_or_create(name='Security Group')
# if created:
#     security_group.permissions.add(Permission.objects.get(codename='can_view_sensitive_data'))


    
class AuditTrail(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)  #('CustomUser', on_delete=models.CASCADE, related_name="audits")
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.action}"
    
    


