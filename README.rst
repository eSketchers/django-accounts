=====
Polls
=====

Django Accounts is a simple Django app to conduct Web-based and API-based auth.
It includes login, signup, change password, forget password web based and api based views.

Dependencies:
django-user-accounts>=2.0.0
djangorestframework>=3.6.2
social-auth-app-django>=1.1.0


Detailed documentation is in the "docs" directory.

Quick start
-----------
1. Add "accounts" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'account',
        'accounts',
        'social_django',
        'rest_framework'  // (optional if you don't want to user apis),
        'rest_framework.authtoken' // (optional if you don't want to user apis)
    ]

2. Include the accounts web based URLconf in your project urls.py like this::

    url(r'^accounts/', include('accounts.urls')),

3. Run `python manage.py migrate` to create the accounts models.

4. Configurations:


