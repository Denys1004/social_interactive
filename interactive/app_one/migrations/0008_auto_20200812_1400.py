# Generated by Django 2.2 on 2020-08-12 18:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_one', '0007_auto_20200812_1337'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='phone_num',
            field=models.CharField(max_length=14, null=True),
        ),
    ]
