# Generated by Django 3.2.12 on 2023-05-17 09:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_20230511_1721'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('user', 'user'), ('admin', 'admin')], default='user', max_length=20, verbose_name='Роль'),
        ),
    ]
