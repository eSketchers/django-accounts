from account.models import EmailAddress

from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView

from django.contrib.auth import authenticate, get_user_model
from social_core.backends.oauth import BaseOAuth1, BaseOAuth2
from social_core.exceptions import AuthAlreadyAssociated
from social_django.utils import load_strategy, load_backend

from . import serializers
from ...conf import settings
from ... import constants, helpers, models

User = get_user_model()


class LoginAPIView(APIView):
    permission_classes = (AllowAny,)
    throttle_classes = (AnonRateThrottle,)
    response_serializer = serializers.UserSerializer
    http_method_names = ['post', ]
    user = None

    def post(self, request, format=None):
        serializer = serializers.LoginSerializer(data=request.data)
        if serializer.is_valid():
            self.user = authenticate(**serializer.data)
            if self.user is None:
                return Response({'errors': {}, 'message': settings.ACCOUNTS_INVALID_LOGIN_MESSAGE, 'success': False},
                                status=status.HTTP_200_OK)
            else:
                return self.response()
        return Response({'success': False, 'errors': serializer.errors, 'message': ''}, status=status.HTTP_400_BAD_REQUEST)

    def response(self):
        return helpers.get_user_serializer_response(self, message=settings.ACCOUNTS_INACTIVE_USER_MESSAGE)


class SignupAPIView(CreateAPIView):
    serializer_class = serializers.SignupSerializer
    throttle_classes = (AnonRateThrottle, )
    permission_classes = (AllowAny, )
    response_serializer = serializers.UserSerializer
    http_method_names = ['post', ]
    model = User
    user = None

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        response = self.perform_create(serializer)
        return response

    def perform_create(self, serializer):
        if serializer.validated_data.has_key('password_confirm'):
            del serializer.validated_data['password_confirm']
        super(SignupAPIView, self).perform_create(serializer)
        self.user = serializer.instance
        return self.after_create(serializer)

    def after_create(self, serializer):
        if self.user:
            user = serializer.instance
            user.set_password(serializer.validated_data.get('password'))
            if settings.ACCOUNT_EMAIL_CONFIRMATION_REQUIRED:
                user.is_active = False
            if settings.ACCOUNT_EMAIL_CONFIRMATION_EMAIL:
                user.save()
                helpers.send_email(user, constants.CONFIRMATION_EMAIL, self.request)
                return Response({'success': True,
                                 'message': settings.ACCOUNTS_CONFIRMATION_EMAIL_MESSAGE,
                                 'code_verification_enabled': settings.ACCOUNTS_USE_CODE_IN_EMAILS},
                                status=status.HTTP_200_OK)
            else:
                user.is_active = True
            user.save()
        return self.response()

    def response(self):
        return helpers.get_user_serializer_response(self,
                                                    message=settings.ACCOUNTS_ACTIVE_USER_MESSAGE,
                                                    is_new=True)


class ChangePasswordAPIView(APIView):
    throttle_classes = (AnonRateThrottle, )
    permission_classes = (IsAuthenticated, )
    http_method_names = ['post', ]

    invalid_password_error_message = settings.ACCOUNTS_CHANGE_PASSWORD_INVALID_CURRENT_PASSWORD_MESSAGE
    inactive_user_message = settings.ACCOUNTS_INACTIVE_USER_MESSAGE
    success_message = settings.ACCOUNTS_CHANGE_PASSWORD_SUCCESS_MESSAGE

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
                             'message': settings.ACCOUNTS_PASSWORD_RESET_EMAIL_SENT_MESSAGE,
                             'code_verification_enabled': settings.ACCOUNTS_USE_CODE_IN_EMAILS,
                             },
                            status=status.HTTP_200_OK)
        return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def send_email(self, email):
        email_qs = EmailAddress.objects.filter(email__iexact=email)
        for user in User.objects.filter(pk__in=email_qs.values("user")):
            helpers.send_email(user, constants.PASSWORD_RESET_CODE_OR_LINK, self.request)


class ResendPasswordResetVerificationCodeOrEmail(APIView):
    permission_classes = (AllowAny, )
    throttle_classes = (AnonRateThrottle, )

    def post(self, request, format=None):
        serializer = serializers.PasswordResetVerificationCodeSerializer(data=request.data)
        if serializer.is_valid():
            user = self.request.user
            if not helpers.is_user_active(user):
                return Response({'success': True,
                                 'message': settings.ACCOUNTS_RESEND_CODE_SUCCESS_MESSAGE,
                                 'active_user': user.is_active
                                 })
            return Response({'success': True, 'message': settings.ACCOUNTS_ACTIVE_USER_MESSAGE})
        return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordAPIView(APIView):
    throttle_classes = (AnonRateThrottle,)
    permission_classes = (AllowAny,)
    http_method_names = ['post', ]

    def post(self, request, format=None):
        serializer = serializers.PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            try:
                code = models.EmailSMSCode.objects.get(
                    verification_code=serializer.data.get('code', None),
                    is_used=False,
                    is_expired=False,
                    action=constants.PASSWORD_RESET_CODE_OR_LINK
                )
                user = code.user
                user.set_password(serializer.data.get('new_password', None))
                user.save()

                code.is_used = True
                code.save()
                return Response({'success': True, 'message': settings.ACCOUNTS_PASSWORD_RESET_SUCCESS_MESSAGE},
                                status=status.HTTP_200_OK)
            except:
                return Response({'success': False, 'message': settings.ACCOUNTS_INVALID_CODE_MESSAGE}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class VerifyCodeAPIView(APIView):
    permission_classes = (AllowAny, )
    AnonRateThrottle = (AnonRateThrottle, )

    # def post(self, request, format=None):


class SocialAuthAPIView(CreateAPIView):
    serializer_class = serializers.SocialLoginSerializer
    response_serializer = serializers.UserSerializer
    permission_classes = (AllowAny,)
    throttle_classes = (AnonRateThrottle, )
    http_method_names = ['post', ]
    model = User
    user = None

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
            print e
            # social = authed_user.social_auth.filter(provider=provider)[0]
            # social.refersh_token(strategy)
            return Response({"errors": "Invalid access token", 'success': False},
                            status=status.HTTP_400_BAD_REQUEST)
        if user:
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
            self.user = user
            return self.response()
        else:
            return Response({"errors": "Error with social authentication", 'success': False},
                            status=status.HTTP_400_BAD_REQUEST)

    def response(self):
        return helpers.get_user_serializer_response(self, message=settings.ACCOUNTS_ACTIVE_USER_MESSAGE)