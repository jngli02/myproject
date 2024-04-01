# Generated by Django 4.2.9 on 2024-03-18 06:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0005_remove_class_name_remove_teacher_class_group_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Evaluation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('draft', '草稿'), ('submitted', '已提交')], default='draft', max_length=10)),
                ('date', models.DateField()),
                ('class_performance', models.CharField(choices=[('优', '优'), ('良', '良'), ('中', '中'), ('差', '差')], max_length=2)),
                ('class_performance_notes', models.TextField(blank=True)),
                ('homework_completion', models.CharField(choices=[('优', '优'), ('良', '良'), ('中', '中'), ('差', '差')], max_length=2)),
                ('homework_completion_notes', models.TextField(blank=True)),
                ('self_study_performance', models.CharField(choices=[('优', '优'), ('良', '良'), ('中', '中'), ('差', '差')], max_length=2)),
                ('self_study_performance_notes', models.TextField(blank=True)),
                ('class_activity_performance', models.CharField(choices=[('优', '优'), ('良', '良'), ('中', '中'), ('差', '差')], max_length=2)),
                ('class_activity_performance_notes', models.TextField(blank=True)),
                ('student_discipline', models.CharField(choices=[('优', '优'), ('良', '良'), ('中', '中'), ('差', '差')], max_length=2)),
                ('student_discipline_notes', models.TextField(blank=True)),
                ('class_contribution', models.CharField(choices=[('优', '优'), ('良', '良'), ('中', '中'), ('差', '差')], max_length=2)),
                ('class_contribution_notes', models.TextField(blank=True)),
                ('mental_health', models.CharField(blank=True, choices=[('优', '优'), ('良', '良'), ('中', '中'), ('差', '差')], max_length=2)),
                ('mental_health_notes', models.TextField(blank=True)),
                ('physical_fitness', models.CharField(blank=True, choices=[('优', '优'), ('良', '良'), ('中', '中'), ('差', '差')], max_length=2)),
                ('physical_fitness_notes', models.TextField(blank=True)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web.student')),
            ],
        ),
    ]
