# Generated by Django 4.0.4 on 2022-05-08 19:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plumbing', '0002_remove_stock_quantity_remove_stock_unitmeasure_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='date',
            field=models.DateField(default='2022-05-08'),
        ),
        migrations.AlterField(
            model_name='customer',
            name='due_date',
            field=models.DateField(blank=True, default='2022-05-08'),
        ),
        migrations.AlterField(
            model_name='exchangerate',
            name='date',
            field=models.DateField(default='2022-05-08'),
        ),
        migrations.AlterField(
            model_name='vendor',
            name='date',
            field=models.DateField(default='2022-05-08'),
        ),
    ]
