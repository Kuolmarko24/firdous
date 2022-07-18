# Generated by Django 4.0.4 on 2022-05-12 07:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('plumbing', '0006_remove_customer_rate'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cheques',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chequeId', models.CharField(max_length=150)),
                ('chooseAccount', models.CharField(choices=[('firdous', 'firdous'), ('sj', 'sj')], default='sj', max_length=20)),
                ('expenseName', models.CharField(max_length=150)),
                ('expenseCost', models.FloatField()),
                ('expenseQuantity', models.IntegerField(default=1)),
                ('totalAmountPaid', models.FloatField()),
                ('date', models.DateField(default='2022-05-12')),
            ],
        ),
        migrations.RemoveField(
            model_name='stock',
            name='stockValue',
        ),
        migrations.AlterField(
            model_name='customer',
            name='date',
            field=models.DateField(default='2022-05-12'),
        ),
        migrations.AlterField(
            model_name='customer',
            name='due_date',
            field=models.DateField(blank=True, default='2022-05-12', null=True),
        ),
        migrations.AlterField(
            model_name='exchangerate',
            name='date',
            field=models.DateField(default='2022-05-12'),
        ),
        migrations.AlterField(
            model_name='vendor',
            name='date',
            field=models.DateField(default='2022-05-12'),
        ),
        migrations.CreateModel(
            name='PurchaseOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(default=1)),
                ('totalAmountPaid', models.FloatField()),
                ('balance', models.FloatField()),
                ('date', models.DateField(default='2022-05-12')),
                ('item_purchased', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='plumbing.stock')),
                ('vendorName', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='plumbing.vendor')),
            ],
        ),
        migrations.CreateModel(
            name='CashInvoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('receiptNumber', models.CharField(max_length=150)),
                ('chooseAccount', models.CharField(choices=[('firdous', 'firdous'), ('sj', 'sj')], default='sj', max_length=20)),
                ('quantity', models.IntegerField(default=1)),
                ('totalAmountPaid', models.FloatField()),
                ('balance', models.FloatField()),
                ('date', models.DateField(default='2022-05-12')),
                ('customerName', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='plumbing.customer')),
                ('item_purchased', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='plumbing.stock')),
            ],
        ),
    ]
