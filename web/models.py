from ast import Import
from email.policy import default
from django.db import models
from django.contrib.auth.models import User
from ckeditor_uploader.fields import RichTextUploadingField
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from pandas.core.base import NoNewAttributesMixin


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
            username = self.teacher_id
            password = str(self.teacher_id)
            self.user = User.objects.create_user(username=username, password=password)
        super().save(*args, **kwargs)  # 先保存Teacher对象
        if self.class_name:
            class_names = self.class_name.split('，')
            for class_name in class_names:
                year, grade = class_name.split('级')
                grade = grade.replace('班', '')
                try:
                    class_group = Class.objects.get(year=year, grade=grade)
                    self.class_groups.add(class_group)  # 然后添加班级对象到class_groups字段中
                except Class.DoesNotExist:
                    pass





class News(models.Model):
    title = models.CharField(max_length=200, verbose_name='主题')
    summary = models.TextField(verbose_name='简介')
    content = RichTextUploadingField(verbose_name='正文')
    add_time = models.DateTimeField(default=timezone.now, verbose_name='添加时间')

    def __str__(self):
        return self.title
    



    







