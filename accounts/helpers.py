from django.utils import timezone
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

from account.models import EmailConfirmation

from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.utils.http import int_to_base36
from django.contrib.auth.tokens import default_token_generator

from .api.v1.serializers import UserSerializer
from . import models, constants, utils
from .conf import settings
from .hooks import hookset


def is_follower(user, follower):

    if user.is_authenticated() and user.id != follower.id:
        followers = user.followers.values_list('followed_to', flat=True)
        if follower.pk in followers:
            return True
    return False


def get_user_serializer_response(login_user, message=None, is_new=False):
    response_status = status.HTTP_200_OK
    response = {}
    if login_user.is_active:
        serializer = UserSerializer(login_user)
        token, created = Token.objects.get_or_create(user=login_user)
        response.update({'user': serializer.data, 'success': True, 'token': token.key})
        if is_new:
            response_status = status.HTTP_201_CREATED
    else:
        response_status = status.HTTP_400_BAD_REQUEST
        response.update({'errors': {}, 'message': message, 'success': False})
    return Response(response, status=response_status)


def is_user_active(user):
    return user.is_active


def setup_email_sms_code(user):
    pass


def save_confirmation_code(user, action=constants.CONFIRMATION_EMAIL):
    models.EmailSMSCode.objects.filter(user=user, action=action, is_used=False, is_expired=False).update(is_expired=True)
    is_exists = True
    while is_exists:
        code = utils.generate_random_code()
        try:
            models.EmailSMSCode.objects.get(
                verification_code=code,
                is_used=False,
                is_expired=False,
                action=action
            )
        except:
            models.EmailSMSCode.objects.create(
                verification_code=code,
                user=user,
                action=action
            )
            is_exists = False

    return code


def send_email(user, action, request):
    ctx = {
        'user': user,
        'current_site': get_current_site(request),
        'is_code_activated': settings.ACCOUNTS_USE_CODE_IN_EMAILS,
        'code': save_confirmation_code(user, action),
        'link': None,
    }

    if action == constants.PASSWORD_RESET_CODE_OR_LINK:
        ctx['link'] = get_password_reset_link(ctx)
        hookset.send_password_reset_email([user.email], ctx)
    elif action == constants.CONFIRMATION_EMAIL:
        ctx['link'] = get_confirmation_email_link(ctx)
        hookset.send_confirmation_email([user.email], ctx)


def get_password_reset_link(ctx):
    protocol = getattr(settings, "DEFAULT_HTTP_PROTOCOL", "http")
    return "{0}://{1}{2}".format(
        protocol,
        ctx['current_site'].domain,
        reverse('password-reset', kwargs=dict(uidb36=int_to_base36(ctx['user'].id), token=utils.make_token(ctx['user'])))
    )


def get_confirmation_email_link(ctx):
    try:
        protocol = getattr(settings, "DEFAULT_HTTP_PROTOCOL", "http")
        email_confirmation = EmailConfirmation.create(ctx['user'].emailaddress_set.all()[0])
        email_confirmation.sent = timezone.now()
        email_confirmation.save()
        return "{0}://{1}{2}".format(
            protocol,
            ctx['current_site'].domain,
            reverse('confirm-email', kwargs=dict(key=email_confirmation.key))
        )
    except:
        pass

