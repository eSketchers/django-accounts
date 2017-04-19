from django.utils.translation import ugettext_lazy as _


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

CONFIRMATION_EMAIL = 0
PASSWORD_RESET_CODE_OR_LINK = 1
INVITE_USER = 2

EMAIL_ACTIONS = (
    (CONFIRMATION_EMAIL, 'Confirmation Email'),
    (PASSWORD_RESET_CODE_OR_LINK, 'Password Reset Code or Link Email'),
    (INVITE_USER, 'Invite User Email'),
)