from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

from .api.v1.serializers import UserSerializer


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