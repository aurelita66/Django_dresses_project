# Generated by Django 4.2.19 on 2025-02-20 08:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('dresscode', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='designer',
            options={'ordering': ('name', 'surname')},
        ),
        migrations.AlterModelOptions(
            name='dress',
            options={'verbose_name': 'Dress', 'verbose_name_plural': 'Dresses'},
        ),
        migrations.RenameField(
            model_name='dress',
            old_name='size',
            new_name='sizes',
        ),
        migrations.RenameField(
            model_name='dress',
            old_name='style',
            new_name='styles',
        ),
        migrations.CreateModel(
            name='DressReview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('content', models.TextField(max_length=2000, verbose_name='Comment')),
                ('dress', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='dresscode.dress')),
                ('reviewer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
