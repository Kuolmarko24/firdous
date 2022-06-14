# Generated by Django 4.0.4 on 2022-06-14 07:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('currencies', '0006_increase_name_max_length'),
        ('plumbing', '0019_alter_cashinvoice_date_alter_cheques_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='cashinvoice',
            name='currency',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='currencies.currency'),
        ),
        migrations.AddField(
            model_name='cheques',
            name='currency',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='currencies.currency'),
        ),
        migrations.AddField(
            model_name='customer',
            name='currency',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='currencies.currency'),
        ),
        migrations.AddField(
            model_name='payable',
            name='currency',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='currencies.currency'),
        ),
        migrations.AddField(
            model_name='purchaseorder',
            name='currency',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='currencies.currency'),
        ),
        migrations.AddField(
            model_name='stock',
            name='currency',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='currencies.currency'),
        ),
        migrations.AddField(
            model_name='transfer',
            name='currency',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='currencies.currency'),
        ),
    ]
