# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-16 14:29
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('servers', '0016_auto_20170716_1429'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='sale',
            name='server',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='servers.Server'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='sale',
            name='user',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
