# Generated by Django 3.2.12 on 2023-05-11 15:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipe', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='recipe',
            old_name='time',
            new_name='cooking_time',
        ),
    ]
