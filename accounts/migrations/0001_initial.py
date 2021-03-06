# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-13 16:41
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailSMSCode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('verification_code', models.CharField(max_length=6)),
                ('action', models.CharField(choices=[(0, b'Confirmation Email'), (1, b'Password Reset Code or Link Email'), (2, b'Invite User Email')], default=0, max_length=10)),
                ('is_used', models.BooleanField(default=False)),
                ('is_expired', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Email/SMS Code',
                'verbose_name_plural': 'Email/SMS Codes',
            },
        ),
    ]
