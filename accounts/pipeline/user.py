import urllib2

from social_core.backends.facebook import FacebookOAuth2
from social_core.pipeline.user import USER_FIELDS

from django.db import models
from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model

from ..conf import settings
from ..utils import file_upload_to

User = get_user_model()


def create_user(strategy, details, backend, user=None, *args, **kwargs):
    if user:
        return {'is_new': False}

    fields = dict((name, kwargs.get(name, details.get(name)))
                  for name in backend.setting('USER_FIELDS', USER_FIELDS))
    if 'email' in fields and not fields['email']:
        fields['username'] = ''.join(fields['username'].split()).lower()
        fields['email'] = fields['username'] + '@' + backend.name + '.com'
    if not fields:
        return
    fields['is_active'] = True
    return {
        'is_new': True,
        'user': strategy.create_user(**fields)
    }


def save_profile_picture(backend, user=None, is_new=False, *args, **kwargs):
    if is_new and user and settings.ACCOUNTS_USER_PROFILE_IMAGE_FIELD_NAME:
        if isinstance(backend, FacebookOAuth2):
            if kwargs.has_key('response'):
                response = kwargs.get('response')
                url = 'http://graph.facebook.com/{0}/picture?type={1}'.format(response['id'], 'large')
                picture = urllib2.urlopen(url).read()
                uploaded_folder = file_upload_to(user, None) + '.png'
                picture_path = '{0}/{1}'.format(settings.MEDIA_ROOT, uploaded_folder)
                fh = open(picture_path, 'wb')
                fh.write(picture)
                fh.close()
                data = {settings.ACCOUNTS_USER_PROFILE_IMAGE_FIELD_NAME: uploaded_folder}
        try:
            User.objects.filter(pk=user.pk).update(**data)
            return {
                'is_new': True,
                'user': user
            }
        except:
            raise ValueError('Invalid Configurations')