# Generated by Django 2.0.1 on 2018-04-01 20:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0005_flat_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='flat',
            name='slug',
            field=models.SlugField(blank=True, unique=True),
        ),
    ]