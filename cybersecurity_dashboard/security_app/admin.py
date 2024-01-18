

from django.urls import reverse
from django.contrib import admin
from django.utils.html import format_html
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, SecurityGroup, AuditTrail, UserRequest, PasswordResetToken
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

    actions = ['resolve_user_requests', 'send_recovery_email']

    def resolve_user_requests(self, request, queryset):
        for user in queryset:
            UserRequest.objects.filter(user=user, resolved=False).update(resolved=True)
    resolve_user_requests.short_description = 'Mark Selected user requests as resolved'

    def user_requests_link(self, obj):
        return format_html('<a href="{}">View User Requests</a>', reverse('admin:security_app_userrequest_changelist') + f'?user__id__exact={obj.id}')

    user_requests_link.short_description = 'User Requests'
    user_requests_link.allow_tags = True

    list_display = ('username', 'email', 'phone_number', 'is_active', 'is_staff', 'user_requests_link')

    def send_recovery_email(self, request, queryset):
        for user in queryset:
            send_recovery_email(user)
        self.message_user(request, f'Recovery email sent to {queryset.count()} users.')

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(PasswordResetToken)
admin.site.register(SecurityGroup)
admin.site.register(AuditTrail)
admin.site.register(UserRequest)



