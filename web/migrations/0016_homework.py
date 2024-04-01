# Generated by Django 4.2.9 on 2024-03-27 06:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0015_directmessage_emojis_directmessage_image_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Homework',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('content', models.TextField()),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                ('remark', models.CharField(max_length=100)),
                ('status', models.CharField(max_length=20)),
                ('class_group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web.class', verbose_name='班级')),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web.teacher')),
            ],
        ),
    ]
