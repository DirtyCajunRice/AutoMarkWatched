# Generated by Django 2.0.3 on 2018-03-29 20:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('amw', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='tvshow',
            old_name='status',
            new_name='continuing',
        ),
    ]