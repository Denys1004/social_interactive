# Generated by Django 2.2 on 2020-08-12 18:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_one', '0011_auto_20200812_1412'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='about',
            field=models.TextField(default=''),
        ),
        migrations.AlterField(
            model_name='user',
            name='phone_num',
            field=models.CharField(default='', max_length=255),
        ),
    ]