


from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, SecurityGroup, AuditTrail
from .forms import CustomUserAdminForm

# Register your models here.
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserAdminForm
    form = CustomUserAdminForm

    list_display = ('username', 'email', 'phone_number', 'is_active', 'is_staff')
    list_filter = ('is_active', 'is_staff')
    search_fields = ('username', 'email', 'phone_number')

    fieldsets = (
    (None, {'fields': ('username', 'password')}),
    ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'phone_number', 'profile_picture',
                                    'country', 'state', 'city', 'zipcode', 'address1', 'address2',
                                    'security_question_1', 'answer_security_1', 'security_question_2',
                                    'answer_security_2', 'two_factor_enabled', 'password_strength', 'last_password_change', 
                                    'login_attempts', 'successful_logins', 'failed_login_timestamp', 'account_created_timestamp', 'account_updated_timestamp',
                                    'two_factor_method', 'security_question_reset_attempts', 'security_question_reset_timestamp', 'total_time_spent', 'last_device_used', 
                                    'device_history', 'active_sessions', 'security_alerts')}),
    ('Permissions', {'fields': ('is_active', 'is_staff', 'user_permissions')}),
    ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username','email'),
            }),
            )

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(SecurityGroup)
admin.site.register(AuditTrail)



