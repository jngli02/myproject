from ast import Import
from email.policy import default
from django.db import models
from django.contrib.auth.models import User
from ckeditor_uploader.fields import RichTextUploadingField
from django.utils import timezone
from django.contrib.auth.hashers import make_password


class Parent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField()
    photo = models.ImageField(upload_to='parents_photos/')
    children = models.TextField()  # 存储孩子的学号，每个学号之间用逗号分隔

    def __str__(self):
        return self.name
 
class Class(models.Model):
    YEAR_CHOICES = (
        ('2020', '2020级'),
        ('2021', '2021级'),
        ('2022', '2022级'),
    )

    GRADE_CHOICES = (
        ('1', '1班'),
        ('2', '2班'),
        ('3', '3班'),
        ('4', '4班'),
        ('5', '5班'),
        ('6', '6班'),
        ('7', '7班'),
        ('8', '8班'),
    )

    year = models.CharField(max_length=4, choices=YEAR_CHOICES, verbose_name='年级', default=None)
    grade = models.CharField(max_length=1, choices=GRADE_CHOICES, verbose_name='班级', default=None)

    def __str__(self):
        return f"{self.year}级{self.grade}班"

class Student(models.Model):
    GENDER_CHOICES = (
        ('男', '男'),
        ('女', '女'),
    )

    student_id = models.CharField(max_length=20, unique=True, verbose_name='学号')
    name = models.CharField(max_length=50, verbose_name='姓名')
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name='性别')
    ethnicity = models.CharField(max_length=20, verbose_name='民族')
    class_name = models.CharField(max_length=50, verbose_name='班级')
    evaluation_id = models.CharField(max_length=20, verbose_name='综合评价编号')
    transcript_id = models.CharField(max_length=20, verbose_name='成绩单编号')
    class_group = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='students', verbose_name='班级', null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.class_group and self.class_name:
            year, grade = self.class_name.split('级')
            grade = grade.replace('班', '')
            try:
                self.class_group = Class.objects.get(year=year, grade=grade)
            except Class.DoesNotExist:
                pass  # 如果找不到对应的班级，class_group将保持为空值
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = '学生'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

class Teacher(models.Model):
    GENDER_CHOICES = (
        ('男', '男'),
        ('女', '女'),
    )
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, verbose_name='默认用户名')
    name = models.CharField(max_length=100, verbose_name='教师姓名')
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name='性别')
    teacher_id = models.CharField(max_length=50, unique=True, verbose_name='教师编号')
    class_name = models.CharField(max_length=50, verbose_name='授课班级')
    subject = models.CharField(max_length=50, verbose_name='授课科目',default=None)
    phone_number = models.CharField(max_length=20, verbose_name='电话号码')
    email = models.EmailField(verbose_name='邮箱地址')
    photo = models.ImageField(upload_to='teachers/', null=True, blank=True, verbose_name='照片')
    position = models.CharField(max_length=50, verbose_name='职位')
    class_groups = models.ManyToManyField(Class, related_name='teachers', verbose_name='授课班级')

    def save(self, *args, **kwargs):
        if not self.pk and not self.user_id:
            # 如果是新创建的教师，并且没有指定用户，则创建用户
            username = self.teacher_id  # 将教师编号作为用户名
            password = str(self.teacher_id)  # 将教师编号转换为字符串作为密码
            self.user = User.objects.create_user(username=username, password=password)
        if self.class_name:
            # 假设班级名称由逗号分隔
            class_names = self.class_name.split('，')
            for class_name in class_names:
                year, grade = class_name.split('级')
                grade = grade.replace('班','')
                try:
                    class_group = Class.objects.get(year=year, grade=grade)
                    self.class_groups.add(class_group)  # 使用add方法添加班级
                except Class.DoesNotExist:
                    print(f"Failed to add class: {class_name}")  # 打印一条消息
        super().save(*args, **kwargs)

class News(models.Model):
    title = models.CharField(max_length=200, verbose_name='主题')
    summary = models.TextField(verbose_name='简介')
    content = RichTextUploadingField(verbose_name='正文')
    add_time = models.DateTimeField(default=timezone.now, verbose_name='添加时间')

    def __str__(self):
        return self.title 

class Evaluation(models.Model):
    PERFORMANCE_CHOICES = [
        ('优', '优'),
        ('良', '良'),
        ('中', '中'),
        ('差', '差'),
    ]
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('submitted', '已提交'),
    ]
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft', verbose_name='状态')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name='学生')
    date = models.DateField(default=timezone.now, verbose_name='日期')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, verbose_name='教师', default=None)

    class_performance = models.CharField(max_length=2, choices=PERFORMANCE_CHOICES, verbose_name='课堂表现')
    class_performance_notes = models.TextField(blank=True, verbose_name='课堂表现备注')

    homework_completion = models.CharField(max_length=2, choices=PERFORMANCE_CHOICES, verbose_name='作业完成情况')
    homework_completion_notes = models.TextField(blank=True, verbose_name='作业完成情况备注')

    self_study_performance = models.CharField(max_length=2, choices=PERFORMANCE_CHOICES, verbose_name='自习表现')
    self_study_performance_notes = models.TextField(blank=True, verbose_name='自习表现备注')

    class_activity_performance = models.CharField(max_length=2, choices=PERFORMANCE_CHOICES, verbose_name='班级活动参与表现')
    class_activity_performance_notes = models.TextField(blank=True, verbose_name='班级活动参与表现备注')

    student_discipline = models.CharField(max_length=2, choices=PERFORMANCE_CHOICES, verbose_name='学生纪律')
    student_discipline_notes = models.TextField(blank=True, verbose_name='学生纪律备注')

    class_contribution = models.CharField(max_length=2, choices=PERFORMANCE_CHOICES, verbose_name='班级劳动贡献')
    class_contribution_notes = models.TextField(blank=True, verbose_name='班级劳动贡献备注')

    mental_health = models.CharField(max_length=2, choices=PERFORMANCE_CHOICES, blank=True, verbose_name='心理健康')
    mental_health_notes = models.TextField(blank=True, verbose_name='心理健康备注')

    physical_fitness = models.CharField(max_length=2, choices=PERFORMANCE_CHOICES, blank=True, verbose_name='身体素质')
    physical_fitness_notes = models.TextField(blank=True, verbose_name='身体素质备注')

class SubmittedEvaluation(models.Model):
    PERFORMANCE_CHOICES = [
        ('优', '优'),
        ('良', '良'),
        ('中', '中'),
        ('差', '差'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name='学生')
    date = models.DateTimeField(default=timezone.now, verbose_name='日期')
    class_performance = models.CharField(max_length=2, choices=PERFORMANCE_CHOICES, verbose_name='课堂表现')
    class_performance_notes = models.TextField(blank=True, verbose_name='课堂表现备注')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, verbose_name='教师', default=None)

    homework_completion = models.CharField(max_length=2, choices=PERFORMANCE_CHOICES, verbose_name='作业完成情况')
    homework_completion_notes = models.TextField(blank=True, verbose_name='作业完成情况备注')

    self_study_performance = models.CharField(max_length=2, choices=PERFORMANCE_CHOICES, verbose_name='自学表现')
    self_study_performance_notes = models.TextField(blank=True, verbose_name='自学表现备注')

    class_activity_performance = models.CharField(max_length=2, choices=PERFORMANCE_CHOICES, verbose_name='课堂活动表现')
    class_activity_performance_notes = models.TextField(blank=True, verbose_name='课堂活动表现备注')

    student_discipline = models.CharField(max_length=2, choices=PERFORMANCE_CHOICES, verbose_name='学生纪律')
    student_discipline_notes = models.TextField(blank=True, verbose_name='学生纪律备注')

    class_contribution = models.CharField(max_length=2, choices=PERFORMANCE_CHOICES, verbose_name='课堂贡献')
    class_contribution_notes = models.TextField(blank=True, verbose_name='课堂贡献备注')

    mental_health = models.CharField(max_length=2, choices=PERFORMANCE_CHOICES, blank=True, verbose_name='心理健康')
    mental_health_notes = models.TextField(blank=True, verbose_name='心理健康备注')

    physical_fitness = models.CharField(max_length=2, choices=PERFORMANCE_CHOICES, blank=True, verbose_name='身体素质')
    physical_fitness_notes = models.TextField(blank=True, verbose_name='身体素质备注')

class Grade(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name='学生', related_name='grades')
    exam_time = models.DateTimeField(verbose_name='考试时间')
    exam_type = models.CharField(max_length=50, verbose_name='考试类型')
    chinese = models.FloatField(verbose_name='语文')
    math = models.FloatField(verbose_name='数学')
    physics = models.FloatField(verbose_name='物理')
    chemistry = models.FloatField(verbose_name='化学')
    english = models.FloatField(verbose_name='英语')
    biology = models.FloatField(verbose_name='生物')
    politics = models.FloatField(verbose_name='政治')
    history = models.FloatField(verbose_name='历史')
    geography = models.FloatField(verbose_name='地理')
    total = models.FloatField(verbose_name='总分', blank=True, null=True)
    remarks = models.TextField(blank=True, verbose_name='备注')
    
class GroupMessage(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    class_group = models.ForeignKey(Class, on_delete=models.CASCADE, default=None)
    content = models.TextField()
    emojis = models.CharField(max_length=100, blank=True, null=True)  # 存储表情信息
    image = models.ImageField(upload_to='group_message_images/', blank=True, null=True)  # 存储图片信息
    sent_at = models.DateTimeField(auto_now_add=True)

class DirectMessage(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receiver')
    content = models.TextField()
    emojis = models.CharField(max_length=100, blank=True, null=True)  # 存储表情信息
    image = models.ImageField(upload_to='direct_message_images/', blank=True, null=True)  # 存储图片信息
    sent_at = models.DateTimeField(auto_now_add=True)
    
class Homework(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    content = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    remark = models.CharField(max_length=255, default='', blank=True)  # 添加备注字段
    status = models.CharField(max_length=20)
    class_group = models.ForeignKey(Class, on_delete=models.CASCADE, verbose_name='班级')

    def __str__(self):
        return self.title

class Attachment(models.Model):
    homework = models.ForeignKey(Homework, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='homework_attachments/')
    # 其他可能的字段，如文件名、文件类型等

    def __str__(self):
        return self.file.name
    

class StudentHomework(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    homework = models.ForeignKey(Homework, on_delete=models.CASCADE)
    submitted = models.BooleanField(default=False)  # 表示作业是否已提交
    graded = models.BooleanField(default=False)     # 表示作业是否已批改

    def __str__(self):
        return f"{self.student} - {self.homework}"
    

class Submission(models.Model):
    submitted_at = models.DateTimeField(auto_now_add=True)  # 提交时间
    answer = models.TextField()  # 学生的答案
    attachment = models.FileField(upload_to='homework_attachments/', blank=True, null=True)  # 附件
    student_homework = models.OneToOneField(StudentHomework, on_delete=models.CASCADE, related_name='submission', default=None)
    grading = models.IntegerField(choices=[(i, i) for i in range(1, 6)], null=True, blank=True)  # 作业打分
    approval_comment = models.TextField(blank=True)  # 审批意见

    def __str__(self):
        return f"Submission - {self.submitted_at}"
    

class HolidaySchedule(models.Model):
    title = models.CharField(max_length=100)  # 标题根据当前年份自动生成
    image = models.ImageField(upload_to='holiday_images/')


class ClassSchedule(models.Model):
    class_name = models.CharField(max_length=100)
    day_of_week = models.CharField(max_length=10)  # 星期几
    start_time = models.TimeField()  # 开始时间
    end_time = models.TimeField()  # 结束时间
    class_info = models.ForeignKey(Class, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.class_name} - {self.day_of_week} - {self.start_time}-{self.end_time}"
    

class LeaveRequest(models.Model):
    STATUS_CHOICES = (
        ('未批假', '未批假'),
        ('假期中', '假期中'),
        ('已销假', '已销假'),
        ('到时间未销假', '到时间未销假'),
    )

    parent = models.ForeignKey(Parent, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    start_date = models.DateTimeField()  # 存储开始日期和时间
    end_date = models.DateTimeField()    # 存储结束日期和时间
    reason = models.TextField()
    approved = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='未批假')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Leave Request for {self.student.name}"


   



