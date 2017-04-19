from django.contrib.auth.backends import ModelBackend
from account.auth_backends import EmailAuthenticationBackend, UsernameAuthenticationBackend


class EmailUserNameAUthenticationBackend(ModelBackend):

    def authenticate(self, email_username=None, password=None, **kwargs):
        user = EmailAuthenticationBackend.authenticate(email=email_username, password=password)
        if not user:
            user = UsernameAuthenticationBackend.authenticate(username=email_username, password=password)

        return user
