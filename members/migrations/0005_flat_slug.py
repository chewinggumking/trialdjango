# Generated by Django 2.0.1 on 2018-04-01 19:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0004_renter'),
    ]

    operations = [
        migrations.AddField(
            model_name='flat',
            name='slug',
            field=models.SlugField(blank=True),
        ),
    ]