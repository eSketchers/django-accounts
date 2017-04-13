import hashlib
import random

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


class AccountsHookSet(object):

    def send_confirmation_email(self, to, ctx):
        subject = render_to_string("email/email_confirmation_subject.txt", ctx)
        subject = "".join(subject.splitlines()) # remove superfluous line breaks
        message = render_to_string("email/email_confirmation_message.html", ctx)
        msg = EmailMultiAlternatives(subject, message, settings.DEFAULT_FROM_EMAIL, to)
        msg.attach_alternative(message, "text/html")
        msg.send()

    def send_password_change_email(self, to, ctx):
        subject = render_to_string("email/password_change_subject.txt", ctx)
        subject = "".join(subject.splitlines())
        message = render_to_string("email/password_change.html", ctx)
        msg = EmailMultiAlternatives(subject, message, settings.DEFAULT_FROM_EMAIL, to)
        msg.attach_alternative(message, "text/html")
        msg.encoding = 'utf8'
        msg.send()

    def send_password_reset_email(self, to, ctx):
        subject = render_to_string("email/password_reset_subject.txt", ctx)
        subject = "".join(subject.splitlines())
        message = render_to_string("email/password_reset.html", ctx)
        msg = EmailMultiAlternatives(subject, message, settings.DEFAULT_FROM_EMAIL, to)
        msg.attach_alternative(message, "text/html")
        msg.encoding = 'utf8'
        msg.send()

    def generate_random_token(self, extra=None, hash_func=hashlib.sha256):
        if extra is None:
            extra = []
        bits = extra + [str(random.SystemRandom().getrandbits(512))]
        return hash_func("".join(bits).encode("utf-8")).hexdigest()

    def generate_signup_code_token(self, email=None):
        return self.generate_random_token([email])

    def generate_email_confirmation_token(self, email):
        return self.generate_random_token([email])

    def get_user_credentials(self, form, identifier_field):
        return {
            "username": form.cleaned_data[identifier_field],
            "password": form.cleaned_data["password"],
        }


class HookProxy(object):

    def __getattr__(self, attr):
        return getattr(settings.ACCOUNT_HOOKSET, attr)


hookset = HookProxy()