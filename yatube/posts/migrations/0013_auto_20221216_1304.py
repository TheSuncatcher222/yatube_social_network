# Generated by Django 2.2.16 on 2022-12-16 10:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0012_follow'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='follow',
            options={'verbose_name': 'подписку', 'verbose_name_plural': 'Подписки'},
        ),
    ]
