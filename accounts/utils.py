import time
from random import randint

from django.utils import timezone as dj_datetime
from django.contrib.auth.tokens import default_token_generator


def file_upload_to(instance, filename):
    try:
        filename = filename.encode("utf-8")
    except Exception as e:
        filename = unicode(int(time.time()))
    return '/'.join([instance.__class__.__name__, unicode(dj_datetime.now().strftime('%Y/%m/%d')),
                     unicode(int(time.time())) + filename])


def make_token(user):
    return default_token_generator.make_token(user)


def generate_random_code():
    return randint(000000, 999999)
