from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            # Modify the query to use Q object for both email and username
            user = UserModel.objects.get(Q(email=username) | Q(username=username))
        except UserModel.DoesNotExist:
            print(f"User with email/username {username} does not exist.")
            return None

        if user.check_password(password):
            print(f"User {user.username} authenticated successfully.")
            return user
        else:
            print(f"User {user.username} authentication failed. Incorrect password.")
            return None

    def get_user(self, user_id):
        UserModel = get_user_model()
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None



