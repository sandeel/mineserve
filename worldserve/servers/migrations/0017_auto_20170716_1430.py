# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-16 14:30
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('servers', '0016_auto_20170716_1429'),
    ]

    operations = [
        migrations.AlterField(
            model_name='server',
            name='expiry_date',
            field=models.DateTimeField(default=datetime.datetime(2017, 7, 16, 15, 35, 0, 884460, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='server',
            name='id',
            field=models.CharField(default='aa630264-b3cd-47b9-854d-dca4afc109d7', max_length=200, primary_key=True, serialize=False),
        ),
    ]
