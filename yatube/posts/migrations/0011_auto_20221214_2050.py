# Generated by Django 2.2.16 on 2022-12-14 17:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0010_auto_20221214_2050'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='pub_date',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации'),
        ),
        migrations.AlterField(
            model_name='post',
            name='pub_date',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации'),
        ),
    ]