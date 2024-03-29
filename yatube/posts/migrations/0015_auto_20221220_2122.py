# Generated by Django 2.2.16 on 2022-12-20 18:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0014_auto_20221218_1917'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='image',
            field=models.ImageField(blank=True, help_text='Прикрепите картинку (не обязательно)', upload_to='posts/', verbose_name='Картинка'),
        ),
        migrations.AddConstraint(
            model_name='follow',
            constraint=models.UniqueConstraint(fields=('user', 'author'), name='unique_follow'),
        ),
    ]
