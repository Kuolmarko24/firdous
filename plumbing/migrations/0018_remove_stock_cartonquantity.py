# Generated by Django 4.0.4 on 2022-05-23 13:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('plumbing', '0017_remove_cheques_chequeid_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stock',
            name='cartonQuantity',
        ),
    ]
