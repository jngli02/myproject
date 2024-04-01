# tasks.py

from django_cron import CronJobBase, Schedule
from datetime import datetime
from .models import Evaluation, SubmittedEvaluation

class AutomaticEvaluationSubmission(CronJobBase):
    RUN_AT_TIMES = ['23:59']  # 每天 23:59 运行一次

    schedule = Schedule(run_at_times=RUN_AT_TIMES)
    code = 'myapp.automatic_evaluation_submission'  # 定义您的任务代码

    def do(self):
        # 获取当前月份
        current_month = datetime.now().month

        # 获取所有未提交的综合评价表单内容
        evaluations = Evaluation.objects.filter(status='draft')

        # 针对每个未提交的表单，检查其内容是否为空。如果不为空，则创建并保存到 SubmittedEvaluation
        for evaluation in evaluations:
            # 检查评价对象是否为空
            if not evaluation.is_empty():
                submitted_evaluation = SubmittedEvaluation(
                    student=evaluation.student,
                    date=evaluation.date,
                    class_performance=evaluation.class_performance,
                    homework_completion=evaluation.homework_completion,
                    self_study_performance=evaluation.self_study_performance,
                    class_activity_performance=evaluation.class_activity_performance,
                    student_discipline=evaluation.student_discipline,
                    class_contribution=evaluation.class_contribution,
                    mental_health=evaluation.mental_health,
                    physical_fitness=evaluation.physical_fitness,
                    # 添加其他字段
                    # ...
                    month=current_month  # 将当前月份保存到 SubmittedEvaluation 中
                )
                submitted_evaluation.save()

                # 更新状态为已提交
                evaluation.status = 'submitted'
                evaluation.save()
