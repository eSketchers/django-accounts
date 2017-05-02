from __future__ import unicode_literals

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from appconf import AppConf


class AccountsAppConf(AppConf):
    LOGIN_URL = 'user-login'
    LOGOUT_URL = 'user-logout'
    PASSWORD_CHANGE_REDIRECT_URL = 'account_password'
    PASSWORD_RESET_REDIRECT_URL = 'user-login'
    EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL = 'user-login'
    EMAIL_CONFIRMATION_URL = "confirm-email"
    USE_LINK_IN_EMAILS = True
    USE_CODE_IN_EMAILS = False
    USER_PROFILE_IMAGE_FIELD_NAME = None
    # Default Messages

    INACTIVE_USER_MESSAGE = _('Your account is not active. Please contact administrator or verify your account.')
    CONFIRMATION_EMAIL_MESSAGE = _('We have sent an email to your account. Please check the email and verify your account')
    INVALID_LOGIN_MESSAGE = _('Invalid username/email or password.')
    PASSWORD_MISMATCH_ERROR_MESSAGE = _('Password and confirm password mismatched')
    CHANGE_PASSWORD_INVALID_CURRENT_PASSWORD_MESSAGE = _(
        'your current password is incorrect. Please try again with valid one.')
    CHANGE_PASSWORD_SUCCESS_MESSAGE = _('Your password has been changed successfully!')
    ACTIVE_USER_MESSAGE = _('You are already an active user')
    RESEND_CODE_SUCCESS_MESSAGE = _(
        'We have sent you verification code on your email. Please visit your email to get the code.')
    PASSWORD_RESET_EMAIL_SENT_MESSAGE = _('We have sent you an email to reset password on your email address. Please check your email.')
    PASSWORD_RESET_SUCCESS_MESSAGE = _(
        'Your password has been reset successfully. Please login with your new password.')
    INVALID_CODE_MESSAGE = _(
        'You have entered invalid code or Your given code is expired. Please enter a valid one and try again.'
    )