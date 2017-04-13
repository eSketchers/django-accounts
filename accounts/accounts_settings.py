from django.utils.translation import ugettext_lazy as _
from django.conf import settings


PAGES_TITLE = {
    '/signup/': _('Sign up'),
    '/login/': _('Log in'),
    '/profile/': _('Profile'),
}

GENDERS = (
    ('male', 'Male'),
    ('female', 'Female'),
    ('other', 'Other'),
)

GENDERS_DICT = (
    ('male', 'Male'),
    ('female', 'Female'),
    ('other', 'Other'),
)

# ERRORS

INACTIVE_USER_MESSAGE = getattr(settings, 'INACTIVE_USER_MESSAGE',
                                _('Your account is not active. Please contact administrator or verify your account.'))
DEFAULT_INVALID_LOGIN_MESSAGE = getattr(settings, 'DEFAULT_INVALID_LOGIN_MESSAGE',
                                        _('Invalid username/email or password.'))
PASSWORD_MISMATCH_ERROR_MESSAGE = getattr(settings, 'PASSWORD_MISMATCH_ERROR_MESSAGE',
                                          _('Password and confirm password mismatched'))
CHANGE_PASSWORD_INVALID_CURRENT_PASSWORD_MESSAGE = getattr(settings, 'CHANGE_PASSWORD_INVALID_CURRENT_PASSWORD',
                                                   _('your current password is incorrect. ' +
                                                     'Please try again with valid one.'))
CHANGE_PASSWORD_SUCCESS_MESSAGE = getattr(settings, 'CHANGE_PASSWORD_SUCCESS_MESSAGE',
                                          _('Your password has been changed successfully!'))