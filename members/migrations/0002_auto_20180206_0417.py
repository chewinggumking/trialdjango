# Generated by Django 2.0.1 on 2018-02-05 22:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='flat',
            unique_together={('flat_number', 'wing')},
        ),
    ]
