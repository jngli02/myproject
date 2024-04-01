# Generated by Django 4.2.9 on 2024-03-29 14:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0018_alter_homework_remark_attachment'),
    ]

    operations = [
        migrations.CreateModel(
            name='Submission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('submitted_at', models.DateTimeField(auto_now_add=True)),
                ('answer', models.TextField()),
                ('attachment', models.FileField(blank=True, null=True, upload_to='homework_attachments/')),
            ],
        ),
        migrations.CreateModel(
            name='StudentHomework',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('submitted', models.BooleanField(default=False)),
                ('graded', models.BooleanField(default=False)),
                ('homework', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web.homework')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web.student')),
                ('submission', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='web.submission')),
            ],
        ),
    ]
