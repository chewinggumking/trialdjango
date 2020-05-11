# Generated by Django 2.0.2 on 2018-02-13 13:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0005_auto_20180207_2143'),
    ]

    operations = [
        migrations.AddField(
            model_name='flatbill',
            name='add_item_amt_1',
            field=models.DecimalField(decimal_places=2, default=0, help_text='Amount for Additional Item 1', max_digits=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='flatbill',
            name='add_item_amt_2',
            field=models.DecimalField(decimal_places=2, default=0, help_text='Amount for Additional Item 2', max_digits=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='flatbill',
            name='add_item_name_1',
            field=models.CharField(blank=True, max_length=100, verbose_name='Additional Items e.g. Building Maintenance'),
        ),
        migrations.AddField(
            model_name='flatbill',
            name='add_item_name_2',
            field=models.CharField(blank=True, max_length=100, verbose_name='Additional Items e.g. Emergency_fund'),
        ),
    ]
