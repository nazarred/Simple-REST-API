# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-08-15 08:40
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('posts', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='like',
            unique_together=set([('post', 'user')]),
        ),
    ]
