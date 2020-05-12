# Generated by Django 2.0.1 on 2018-02-07 15:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0002_billdetails_flat_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='billdetails',
            name='elec_insurance_charges',
        ),
        migrations.AddField(
            model_name='billdetails',
            name='elec_ins_chgs',
            field=models.DecimalField(decimal_places=2, default=0, help_text='Electricity Insurance', max_digits=10, verbose_name='Electricity Insurance Charges'),
            preserve_default=False,
        ),
    ]