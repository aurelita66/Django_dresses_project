# Generated by Django 4.2.19 on 2025-02-20 13:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dresscode', '0002_alter_designer_options_alter_dress_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='dressrental',
            name='size',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Size'),
        ),
    ]
