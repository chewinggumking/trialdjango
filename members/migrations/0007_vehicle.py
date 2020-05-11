# Generated by Django 2.0.4 on 2018-04-18 15:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0006_auto_20180402_0137'),
    ]

    operations = [
        migrations.CreateModel(
            name='Vehicle',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vehicle', models.CharField(choices=[('TWST', 'Two Wheeler Stilt'), ('FWST', 'Four Wheeler Stilt'), ('TWOU', 'Two Wheeler Outside'), ('FWOU', 'Foue Wheeler Outside')], max_length=4)),
                ('flat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='members.Flat')),
            ],
        ),
    ]
