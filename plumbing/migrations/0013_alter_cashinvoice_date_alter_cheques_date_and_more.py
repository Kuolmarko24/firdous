# Generated by Django 4.0.4 on 2022-05-23 07:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plumbing', '0012_rename_totalamountpaid_payable_amounttopay_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cashinvoice',
            name='date',
            field=models.DateField(default='2022-05-23'),
        ),
        migrations.AlterField(
            model_name='cheques',
            name='date',
            field=models.DateField(default='2022-05-23'),
        ),
        migrations.AlterField(
            model_name='customer',
            name='date',
            field=models.DateField(default='2022-05-23'),
        ),
        migrations.AlterField(
            model_name='customer',
            name='due_date',
            field=models.DateField(blank=True, default='2022-05-23', null=True),
        ),
        migrations.AlterField(
            model_name='exchangerate',
            name='date',
            field=models.DateField(default='2022-05-23'),
        ),
        migrations.AlterField(
            model_name='payable',
            name='date',
            field=models.DateField(default='2022-05-23'),
        ),
        migrations.AlterField(
            model_name='purchaseorder',
            name='date',
            field=models.DateField(default='2022-05-23'),
        ),
        migrations.AlterField(
            model_name='transfer',
            name='date',
            field=models.DateField(default='2022-05-23'),
        ),
        migrations.AlterField(
            model_name='vendor',
            name='date',
            field=models.DateField(default='2022-05-23'),
        ),
    ]