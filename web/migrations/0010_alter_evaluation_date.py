# Generated by Django 4.2.9 on 2024-03-18 09:18

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0009_remove_submittedevaluation_submission_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='evaluation',
            name='date',
            field=models.DateField(default=django.utils.timezone.now, verbose_name='日期'),
        ),
    ]
