# Generated by Django 3.2.12 on 2022-09-12 18:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plumbing', '0033_cart_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='stock',
            name='usdPrice',
            field=models.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name='cashinvoice',
            name='date',
            field=models.DateField(default='2022-09-12'),
        ),
        migrations.AlterField(
            model_name='cashinvoice',
            name='totalAmountPaid',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='cheques',
            name='date',
            field=models.DateField(default='2022-09-12'),
        ),
        migrations.AlterField(
            model_name='creditreceipt',
            name='date',
            field=models.DateField(default='2022-09-12'),
        ),
        migrations.AlterField(
            model_name='customer',
            name='date',
            field=models.DateField(default='2022-09-12'),
        ),
        migrations.AlterField(
            model_name='customer',
            name='due_date',
            field=models.DateField(blank=True, default='2022-09-12', null=True),
        ),
        migrations.AlterField(
            model_name='customerreceipt',
            name='date',
            field=models.DateField(default='2022-09-12'),
        ),
        migrations.AlterField(
            model_name='exchangerate',
            name='date',
            field=models.DateField(default='2022-09-12'),
        ),
        migrations.AlterField(
            model_name='payable',
            name='date',
            field=models.DateField(default='2022-09-12'),
        ),
        migrations.AlterField(
            model_name='purchaseorder',
            name='date',
            field=models.DateField(default='2022-09-12'),
        ),
        migrations.AlterField(
            model_name='quotationreceipt',
            name='date',
            field=models.DateField(default='2022-09-12'),
        ),
        migrations.AlterField(
            model_name='transfer',
            name='date',
            field=models.DateField(default='2022-09-12'),
        ),
        migrations.AlterField(
            model_name='vendor',
            name='date',
            field=models.DateField(default='2022-09-12'),
        ),
    ]