

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordResetForm, UserChangeForm, PasswordChangeForm
from .models import CustomUser
from django.db.models import Q

class CustomUserCreationForm(UserCreationForm):
    # name=forms.CharField(label='Name', widget=forms.TextInput(attrs={'class':'form-control'}))
    email=forms.EmailField(label='Email Address',widget=forms.TextInput(attrs={'class':'form-control'}))
    username=forms.CharField(label='Username', widget=forms.TextInput(attrs={'class':'form-control'}))
    phone_number=forms.CharField(label='Phone No',widget=forms.TextInput(attrs={'class':'form-control'}))
    password1=forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class':'form-control'}))
    password2=forms.CharField(label='Confirm Password', widget=forms.PasswordInput(attrs={'class':'form-control'}))
    # profile_picture=forms.ImageField(label='profile_image')

    class Meta:
        model = CustomUser
        fields = ('username', 'email','phone_number',  'password1', 'password2')  # Add other fields as needed
    

class UserProfileForm(forms.ModelForm):
    first_name=forms.CharField(label='First Name', widget=forms.TextInput(attrs={'class':'form-control'}))
    last_name=forms.CharField(label='Last Name', widget=forms.TextInput(attrs={'class':'form-control'}))
    country=forms.CharField(label='Country', widget=forms.TextInput(attrs={'class':'form-control'}))
    state=forms.CharField(label='State', widget=forms.TextInput(attrs={'class':'form-control'}))
    city=forms.CharField(label='City', widget=forms.TextInput(attrs={'class':'form-control'}))
    zipcode=forms.CharField(label='Zipcode', widget=forms.TextInput(attrs={'class':'form-control'}))
    address1=forms.CharField(label='Primary Address', widget=forms.TextInput(attrs={'class':'form-control'}))
    address2=forms.CharField(label='Secondary Address', required=False, widget=forms.TextInput(attrs={'class':'form-control'}))
    profile_picture=forms.ImageField(label='profile_image', required=False)


    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name','country', 'state', 'city', 
        'zipcode', 'address1', 'address2','profile_picture']

class SecurityQuestionForm(forms.ModelForm):
    security_question_1=forms.CharField(label='Security question 1:', widget=forms.TextInput(attrs={'class':'form-control'}))
    answer_security_1=forms.CharField(label='Answer security 1:', widget=forms.TextInput(attrs={'class':'form-control'}))
    security_question_2=forms.CharField(label='Security question 2', widget=forms.TextInput(attrs={'class':'form-control'}))
    answer_security_2=forms.CharField(label='Answer security 2:', widget=forms.TextInput(attrs={'class':'form-control'}))

    class Meta:
        model = CustomUser
        fields = ['security_question_1', 'answer_security_1', 
                    'security_question_2', 'answer_security_2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        security_questions_choices = [
            ('favorite_color', 'What is your favorite color?'),
            ('first_pet', 'What was the name of your first pet?'),
            ('birth_city', 'In which city were you born?'),
            ('favorite_book', 'What is your favorite book?'),
            ('high_school', 'Which high school did you attend?'),

        ]
         # Set choices for security questions in the form
        self.fields['security_question_1'].widget = forms.Select(choices=security_questions_choices)
        self.fields['security_question_2'].widget = forms.Select(choices=security_questions_choices)



class SecurityAnswerForm(forms.Form):
    username = forms.CharField(label='Username', widget=forms.TextInput(attrs={'class': 'form-control'}))
    answer_security_1 = forms.CharField(label='Answer security 1', widget=forms.TextInput(attrs={'class': 'form-control'}))
    answer_security_2 = forms.CharField(label='Answer security 2', widget=forms.TextInput(attrs={'class': 'form-control'}))

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        answer_security_1 = cleaned_data.get('answer_security_1')
        answer_security_2 = cleaned_data.get('answer_security_2')

        user = CustomUser.objects.filter(username=username, answer_security_1=answer_security_1, answer_security_2=answer_security_2).first()

        if not user:
            raise forms.ValidationError('Invalid security answers or username.')

    def get_user(self):
        username = self.cleaned_data.get('username')
        return CustomUser.objects.get(username=username)


class CustomAuthenticationForm(AuthenticationForm):
    class Meta:
        model = CustomUser

class CustomPasswordResetForm(PasswordResetForm):
    email=forms.EmailField(label='Email Address',widget=forms.TextInput(attrs={'class':'form-control'}))
    password1 = forms.CharField(label='New Password', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        self.user.set_password(self.cleaned_data["password1"])
        if commit:
            self.user.save()
        return self.user


class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(label='Old Password', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    new_password1 = forms.CharField(label='New Password', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    new_password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = CustomUser
        fields = ['old_password', 'new_password1', 'new_password2']



class CustomUserAdminForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = '__all__'




