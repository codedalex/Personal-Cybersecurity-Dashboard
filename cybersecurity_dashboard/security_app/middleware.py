from django.contrib.auth import logout

class SessionTimeoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Log out the user if the session has expired
        if request.user.is_authenticated and not request.session.get_expiry_age() > 0:
            logout(request)

        return response