# Generated by Django 3.2.12 on 2022-09-14 16:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plumbing', '0036_auto_20220913_0036'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cashinvoice',
            name='date',
            field=models.DateField(default='2022-09-14'),
        ),
        migrations.AlterField(
            model_name='cheques',
            name='date',
            field=models.DateField(default='2022-09-14'),
        ),
        migrations.AlterField(
            model_name='creditreceipt',
            name='date',
            field=models.DateField(default='2022-09-14'),
        ),
        migrations.AlterField(
            model_name='customer',
            name='date',
            field=models.DateField(default='2022-09-14'),
        ),
        migrations.AlterField(
            model_name='customer',
            name='due_date',
            field=models.DateField(blank=True, default='2022-09-14', null=True),
        ),
        migrations.AlterField(
            model_name='customerreceipt',
            name='date',
            field=models.DateField(default='2022-09-14'),
        ),
        migrations.AlterField(
            model_name='exchangerate',
            name='date',
            field=models.DateField(default='2022-09-14'),
        ),
        migrations.AlterField(
            model_name='payable',
            name='date',
            field=models.DateField(default='2022-09-14'),
        ),
        migrations.AlterField(
            model_name='purchaseorder',
            name='date',
            field=models.DateField(default='2022-09-14'),
        ),
        migrations.AlterField(
            model_name='quotationreceipt',
            name='date',
            field=models.DateField(default='2022-09-14'),
        ),
        migrations.AlterField(
            model_name='transfer',
            name='date',
            field=models.DateField(default='2022-09-14'),
        ),
        migrations.AlterField(
            model_name='vendor',
            name='date',
            field=models.DateField(default='2022-09-14'),
        ),
    ]