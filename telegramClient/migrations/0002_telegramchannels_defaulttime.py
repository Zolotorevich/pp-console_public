# Generated by Django 4.2.3 on 2023-07-16 15:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('telegramClient', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='telegramchannels',
            name='defaultTime',
            field=models.CharField(default=1700, max_length=255),
            preserve_default=False,
        ),
    ]