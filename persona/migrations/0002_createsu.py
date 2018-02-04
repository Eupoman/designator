# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from django.db import models, migrations
from django.contrib.auth.models import User


from django.core.management import call_command

fixture_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../fixtures'))
fixture_filename = 'create_su.json'


def load_fixture(apps, schema_editor):
    fixture_file = os.path.join(fixture_dir, fixture_filename)
    call_command('loaddata', fixture_file)


class Migration(migrations.Migration):

    dependencies = [
        ('persona', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(load_fixture, reverse_code=migrations.RunPython.noop),
    ]
