from account.models import EmailAddress

from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView

from django.contrib.auth import authenticate, get_user_model
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.utils.http import int_to_base36
from social_core.backends.oauth import BaseOAuth1, BaseOAuth2
from social_core.exceptions import AuthAlreadyAssociated
from social_django.utils import load_strategy, load_backend

from ...helpers import get_user_serializer_response
from . import serializers
from ... import accounts_settings
from ...hooks import hookset
from ...utils import make_token

User = get_user_model()


class LoginAPIView(APIView):
    permission_classes = (AllowAny,)
    throttle_classes = (AnonRateThrottle,)
    default_error_message = accounts_settings.DEFAULT_INVALID_LOGIN_MESSAGE
    inactive_user_message = accounts_settings.INACTIVE_USER_MESSAGE
    http_method_names = ['post', ]

    def post(self, request, format=None):
        serializer = serializers.LoginSerializer(data=request.data)
        if serializer.is_valid():
            login_user = authenticate(**serializer.data)
            if login_user is None:
                return Response({'errors': {}, 'message': self.default_error_message, 'success': False},
                                status=status.HTTP_200_OK)
            else:
                return get_user_serializer_response(login_user, self.inactive_user_message)
        return Response({'success': False, 'errors': serializer.errors, 'message': ''}, status=status.HTTP_400_BAD_REQUEST)


class SignupAPIView(CreateAPIView):
    serializer_class = serializers.SignupSerializer
    throttle_classes = (AnonRateThrottle, )
    permission_classes = (AllowAny, )
    http_method_names = ['post', ]
    model = User

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return get_user_serializer_response(login_user=serializer.instance, is_new=True)

    def perform_create(self, serializer):
        if serializer.validated_data.has_key('password_confirm'):
            del serializer.validated_data['password_confirm']
        super(SignupAPIView, self).perform_create(serializer)
        user = serializer.instance
        user.is_active = True
        user.set_password(serializer.validated_data.get('password'))
        user.save()


class ChangePasswordAPIView(APIView):
    throttle_classes = (AnonRateThrottle, )
    permission_classes = (IsAuthenticated, )
    http_method_names = ['post', ]

    invalid_password_error_message = accounts_settings.CHANGE_PASSWORD_INVALID_CURRENT_PASSWORD_MESSAGE
    inactive_user_message = accounts_settings.INACTIVE_USER_MESSAGE
    success_message = accounts_settings.CHANGE_PASSWORD_SUCCESS_MESSAGE

    def post(self, request, format=None):
        serializer = serializers.ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if user.check_password(serializer.data.get('password')):
                user.set_password(serializer.data.get('new_password'))
                user.save()
                return Response({'success': True, 'message': self.success_message},
                                status=status.HTTP_200_OK)
            else:
                return Response({'success': False, 'errors': {}, 'message': self.invalid_password_error_message},
                                status=status.HTTP_400_BAD_REQUEST)
        return Response({'success': False, 'errors': serializer.errors, 'message': ''},
                            status=status.HTTP_400_BAD_REQUEST)


class ForgotPasswordAPIView(APIView):
    throttle_classes = (AnonRateThrottle, )
    permission_classes = (AllowAny, )
    http_method_names = ['post', ]

    def post(self, request, format=None):
        serializer = serializers.ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            self.send_email(serializer.data["email"])
            return Response({'success': True,
                             'message': 'We have sent you an email for password reset. Please check your email.'},
                            status=status.HTTP_200_OK)
        return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def send_email(self, email):
        protocol = getattr(settings, "DEFAULT_HTTP_PROTOCOL", "http")
        current_site = get_current_site(self.request)
        email_qs = EmailAddress.objects.filter(email__iexact=email)
        for user in User.objects.filter(pk__in=email_qs.values("user")):
            uid = int_to_base36(user.id)
            token = make_token(user)
            password_reset_url = "{0}://{1}{2}".format(
                protocol,
                current_site.domain,
                reverse("account_password_reset_token", kwargs=dict(uidb36=uid, token=token))
            )
            ctx = {
                "user": user,
                "current_site": current_site,
                "password_reset_url": password_reset_url,
            }
            hookset.send_password_reset_email([user.email], ctx)


class SocialAuthAPIView(CreateAPIView):
    serializer_class = serializers.SocialLoginSerializer
    permission_classes = (AllowAny,)
    throttle_classes = (AnonRateThrottle, )
    http_method_names = ['post', ]
    model = User

    def create(self, request, *args, **kwargs):
        """
        Override `create` instead of `perform_create` to access request
        request is necessary for `load_strategy`
        """
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response({"errors": serializer.errors, 'success': False},
                            status=status.HTTP_400_BAD_REQUEST)

        provider = request.data['provider']

        # If this request was made with an authenticated user, try to associate this social
        # account with it
        authed_user = request.user if not request.user.is_anonymous() else None

        # `strategy` is a python-social-auth concept referencing the Python framework to
        # be used (Django, Flask, etc.). By passing `request` to `load_strategy`, PSA
        # knows to use the Django strategy
        strategy = load_strategy(request)
        # Now we get the backend that corresponds to our user's social auth provider
        # e.g., Facebook, Twitter, etc.
        backend = load_backend(strategy=strategy, name=provider, redirect_uri=None)

        if isinstance(backend, BaseOAuth1):
            # Twitter, for example, uses OAuth1 and requires that you also pass
            # an `oauth_token_secret` with your authentication request
            token = {
                'oauth_token': request.data['access_token'],
                'oauth_token_secret': request.data['access_token_secret'],
            }
        elif isinstance(backend, BaseOAuth2):
            # We're using oauth's implicit grant type (usually used for web and mobile
            # applications), so all we have to pass here is an access_token
            token = request.data['access_token']

        try:
            # if `authed_user` is None, python-social-auth will make a new user,
            # else this social account will be associated with the user you pass in
            user = backend.do_auth(token, user=authed_user)
        except AuthAlreadyAssociated:
            # You can't associate a social account with more than user
            return Response({"errors": "That social media account is already in use"},
                            status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            social = authed_user.social_auth.filter(provider=provider)[0]
            social.refersh_token(strategy)
            return Response({"errors": "Invalid access token", 'success': False},
                            status=status.HTTP_400_BAD_REQUEST)
        if user and user.is_active:
            # if the access token was set to an empty string, then save the access token
            # from the request
            auth_created = user.social_auth.get(provider=provider)
            if not auth_created.extra_data['access_token']:
                # Facebook for example will return the access_token in its response to you.
                # This access_token is then saved for your future use. However, others
                # e.g., Instagram do not respond with the access_token that you just
                # provided. We save it here so it can be used to make subsequent calls.
                auth_created.extra_data['access_token'] = token
                auth_created.save()

            # Set instance since we are not calling `serializer.save()`
            serializer.instance = user
            return get_user_serializer_response(user, accounts_settings.INACTIVE_USER_MESSAGE)
        else:
            return Response({"errors": "Error with social authentication", 'success': False},
                            status=status.HTTP_400_BAD_REQUEST)
