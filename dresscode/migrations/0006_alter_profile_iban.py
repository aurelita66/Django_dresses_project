# Generated by Django 4.2.19 on 2025-02-21 12:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dresscode', '0005_alter_profile_iban'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='iban',
            field=models.CharField(max_length=50, unique=True, verbose_name='IBAN'),
        ),
    ]
