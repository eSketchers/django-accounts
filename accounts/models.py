from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from . import constants


class EmailSMSCode(models.Model):
    verification_code = models.CharField(max_length=6)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True)
    action = models.CharField(max_length=10, choices=constants.EMAIL_ACTIONS, default=constants.CONFIRMATION_EMAIL)
    is_used = models.BooleanField(default=False)
    is_expired = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Email/SMS Code')
        verbose_name_plural = _('Email/SMS Codes')

    def __str__(self):
        return self.verification_code
