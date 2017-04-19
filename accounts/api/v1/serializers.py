from rest_framework import serializers
from rest_framework.fields import empty

from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from django.conf import settings


User = get_user_model()


class LoginSerializer(serializers.Serializer):

    username = serializers.CharField(max_length=255, required=False)
    password = serializers.CharField(max_length=255)
    email = serializers.CharField(max_length=255, required=False)

    def __init__(self, instance=None, data=empty, **kwargs):
        if data.has_key('email'):
            self.fields['email'].required = True
        else:
            self.fields['username'].required = True
            self.fields['username'].error_messages['required'] = _('username or email is required')
        super(LoginSerializer, self).__init__(data=data, **kwargs)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class SignupSerializer(serializers.ModelSerializer):
    password_confirm = serializers.CharField(max_length=255)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'password', 'password_confirm', )
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError(settings.ACCOUNTS_PASSWORD_MISMATCH_ERROR_MESSAGE)
        return data


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')


class ChangePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=255, required=True)
    new_password = serializers.CharField(max_length=255, required=True)
    new_password_confirm = serializers.CharField(max_length=255, required=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    def validate(self, attrs):
        if attrs.get('new_password', None) != attrs.get('new_password_confirm', None):
            raise serializers.ValidationError(settings.ACCOUNTS_PASSWORD_MISMATCH_ERROR_MESSAGE)
        return attrs


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255, required=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class SocialLoginSerializer(serializers.Serializer):
    provider = serializers.CharField(max_length=255, required=True)
    access_token = serializers.CharField(max_length=1000, required=True)
    access_token_secret = serializers.CharField(max_length=1000, required=False)

    def __init__(self, instance=None, data=None, **kwargs):
        if data.has_key('provider') and data['provider'] == 'twitter':
            self.fields['access_token_secret'].required = True
        super(SocialLoginSerializer, self).__init__(data=data, **kwargs)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class PasswordResetSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=6, min_length=1, required=False)
    new_password = serializers.CharField(required=True)
    new_password_confirm = serializers.CharField(required=True)

    def __init__(self, instance=None, data=empty, **kwargs):
        if settings.ACCOUNTS_USE_CODE_IN_EMAILS:
            self.fields['code'].required = True
        super(PasswordResetSerializer, self).__init__(data=data, **kwargs)

    def validate(self, attrs):
        if attrs.get('new_password', None) != attrs.get('new_password_confirm', None):
            raise serializers.ValidationError(settings.ACCOUNTS_PASSWORD_MISMATCH_ERROR_MESSAGE)
        return attrs

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class ConfirmAccountVerificationCodeSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=6, min_length=1, required=True)
