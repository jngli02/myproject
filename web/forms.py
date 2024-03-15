# forms.py
from django import forms
from .models import Student
from .models import Teacher
from .models import News

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['student_id', 'name', 'gender', 'ethnicity', 'class_name', 'evaluation_id', 'transcript_id']

class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['teacher_id','name', 'gender', 'class_name', 'phone_number', 'email', 'photo', 'position']
        

class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = ['title', 'summary', 'content']





