# Generated by Django 3.0 on 2020-11-08 14:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_item_item_slug'),
    ]

    operations = [
        migrations.RenameField(
            model_name='item',
            old_name='item_slug',
            new_name='slug',
        ),
    ]
