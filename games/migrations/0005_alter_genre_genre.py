# Generated by Django 4.2.3 on 2023-07-31 14:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0004_genre_genresynonym'),
    ]

    operations = [
        migrations.AlterField(
            model_name='genre',
            name='genre',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]