from social_core.pipeline.user import USER_FIELDS
from django.contrib.auth import get_user_model

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
