from django.db.models.signals import post_save
from django.dispatch import receiver
from web.models import StudentHomework, Submission

@receiver(post_save, sender=StudentHomework)
def check_submission(sender, instance, **kwargs):
    if instance.submitted:
        # 检查是否存在相应的提交信息
        if not Submission.objects.filter(student_homework=instance).exists():
            # 如果不存在提交信息，则将 submitted 字段重置为 False
            instance.submitted = False
            instance.save(update_fields=['submitted'])
