# Generated by Django 4.2.9 on 2024-03-18 08:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0007_alter_evaluation_class_activity_performance_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='SubmittedEvaluation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('submission_date', models.DateTimeField(auto_now_add=True, verbose_name='提交日期')),
                ('class_performance', models.CharField(choices=[('优', '优'), ('良', '良'), ('中', '中'), ('差', '差')], max_length=2, verbose_name='课堂表现')),
                ('class_performance_notes', models.TextField(blank=True, verbose_name='课堂表现备注')),
                ('homework_completion', models.CharField(choices=[('优', '优'), ('良', '良'), ('中', '中'), ('差', '差')], max_length=2, verbose_name='作业完成情况')),
                ('homework_completion_notes', models.TextField(blank=True, verbose_name='作业完成情况备注')),
                ('self_study_performance', models.CharField(choices=[('优', '优'), ('良', '良'), ('中', '中'), ('差', '差')], max_length=2, verbose_name='自学表现')),
                ('self_study_performance_notes', models.TextField(blank=True, verbose_name='自学表现备注')),
                ('class_activity_performance', models.CharField(choices=[('优', '优'), ('良', '良'), ('中', '中'), ('差', '差')], max_length=2, verbose_name='课堂活动表现')),
                ('class_activity_performance_notes', models.TextField(blank=True, verbose_name='课堂活动表现备注')),
                ('student_discipline', models.CharField(choices=[('优', '优'), ('良', '良'), ('中', '中'), ('差', '差')], max_length=2, verbose_name='学生纪律')),
                ('student_discipline_notes', models.TextField(blank=True, verbose_name='学生纪律备注')),
                ('class_contribution', models.CharField(choices=[('优', '优'), ('良', '良'), ('中', '中'), ('差', '差')], max_length=2, verbose_name='课堂贡献')),
                ('class_contribution_notes', models.TextField(blank=True, verbose_name='课堂贡献备注')),
                ('mental_health', models.CharField(blank=True, choices=[('优', '优'), ('良', '良'), ('中', '中'), ('差', '差')], max_length=2, verbose_name='心理健康')),
                ('mental_health_notes', models.TextField(blank=True, verbose_name='心理健康备注')),
                ('physical_fitness', models.CharField(blank=True, choices=[('优', '优'), ('良', '良'), ('中', '中'), ('差', '差')], max_length=2, verbose_name='身体素质')),
                ('physical_fitness_notes', models.TextField(blank=True, verbose_name='身体素质备注')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web.student', verbose_name='学生')),
            ],
        ),
    ]
