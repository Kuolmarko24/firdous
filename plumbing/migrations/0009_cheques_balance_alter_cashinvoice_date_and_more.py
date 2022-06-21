# Generated by Django 4.0.4 on 2022-05-17 09:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plumbing', '0008_alter_cheques_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='cheques',
            name='balance',
            field=models.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name='cashinvoice',
            name='date',
            field=models.DateField(default='2022-05-17'),
        ),
        migrations.AlterField(
            model_name='cheques',
            name='date',
            field=models.DateField(default='2022-05-17'),
        ),
        migrations.AlterField(
            model_name='customer',
            name='date',
            field=models.DateField(default='2022-05-17'),
        ),
        migrations.AlterField(
            model_name='customer',
            name='due_date',
            field=models.DateField(blank=True, default='2022-05-17', null=True),
        ),
        migrations.AlterField(
            model_name='exchangerate',
            name='date',
            field=models.DateField(default='2022-05-17'),
        ),
        migrations.AlterField(
            model_name='purchaseorder',
            name='date',
            field=models.DateField(default='2022-05-17'),
        ),
        migrations.AlterField(
            model_name='vendor',
            name='date',
            field=models.DateField(default='2022-05-17'),
        ),
    ]
