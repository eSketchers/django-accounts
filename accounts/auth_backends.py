from django.contrib.auth.backends import ModelBackend
from account.auth_backends import EmailAuthenticationBackend, UsernameAuthenticationBackend


class EmailUserNameAuthenticationBackend(ModelBackend):

    def authenticate(self, username=None, password=None, **kwargs):
        backend = EmailAuthenticationBackend()
        user = backend.authenticate(username=username, password=password)
        if not user:
            backend = UsernameAuthenticationBackend()
            user = backend.authenticate(username=username, password=password)

        return user
