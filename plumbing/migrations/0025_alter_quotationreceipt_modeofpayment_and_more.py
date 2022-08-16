# Generated by Django 4.0.4 on 2022-08-13 11:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plumbing', '0024_quotationreceipt_alter_cashinvoice_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quotationreceipt',
            name='modeOfPayment',
            field=models.CharField(choices=[('Bank', 'Bank'), ('Cash', 'Cash')], max_length=100),
        ),
        migrations.AlterField(
            model_name='quotationreceipt',
            name='purchasedFrom',
            field=models.CharField(choices=[('firdous', 'firdous'), ('sj', 'sj')], default='sj', max_length=20),
        ),
    ]