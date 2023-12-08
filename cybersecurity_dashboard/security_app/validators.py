

from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from .utils import get_common_passwords, get_special_characters
import re

def calculate_password_strength(password):
    # Criteria weights
    length_weight = 2
    uppercase_weight = 2
    lowercase_weight = 2
    number_weight = 2
    special_char_weight = 2

    # Get the special characters
    special_characters = get_special_characters()

    # Calculate the length score
    length_score = min(len(password) / 8.0, 1.0) * length_weight
    # Calculate the uppercase letter score
    uppercase_score = min(sum(1 for char in password if char.isupper()) / len(password), 1.0) * uppercase_weight
    # Calculate the lowercase letter score
    lowercase_score = min(sum(1 for char in password if char.islower()) / len(password), 1.0) * lowercase_weight
    # Calculate the numeric digit score
    number_score = min(sum(1 for char in password if char.isdigit()) / len(password), 1.0) * number_weight
    # Calculate the special character score
    special_char_score = min(sum(1 for char in password if char in special_characters) / len(password), 1.0) * special_char_weight

    # Total score
    total_score = length_score + uppercase_score + lowercase_score + number_score + special_char_score
    # Convert the score into percentage
    password_strength = int(total_score * 100)

    return password_strength




class CustomPasswordValidator:
    def validate(self, password, user=None):
        # Check if the pssword is too common
        common_passwords = get_common_passwords()
        if password.lower() in common_passwords:
            raise ValidationError(_('This password is too common.'), 
            code='password_too_common')

        # Check if the password contains both letters and numbers
        if not any(char.isdigit() for char in password) or not any(char.isalpha() for char in password):
            raise ValidationError(
                _("Password must contain both letters and numbers."),
                code="password_not_complex"
            )

        # Check if the password contains special characters
        special_characters = get_special_characters()
        if not any(char in special_characters for char in password):
            raise ValidationError(
                _("Password must contain at least one of these special characters: !@#$%^&*"),
                code="password_no_special_chars"
                )

    def get_help_text(self):
        return _("Your password should be complex and include a mix of uppercase and lowercase letters, numbers, and special characters.")


