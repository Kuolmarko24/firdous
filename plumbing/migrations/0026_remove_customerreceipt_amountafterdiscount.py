# Generated by Django 4.0.4 on 2022-08-09 11:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('plumbing', '0025_alter_cashinvoice_date_alter_cheques_date_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customerreceipt',
            name='AmountAfterDiscount',
        ),
    ]
