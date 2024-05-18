# forms.py
from django import forms
from .models import Student
from .models import Teacher,Parent
from .models import News
from .models import Evaluation,User
from django.contrib.auth.forms import UserChangeForm, PasswordChangeForm
from .models import SubmittedEvaluation, Homework, Attachment, HolidaySchedule,Class,LeaveRequest


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['student_id', 'name', 'gender', 'ethnicity', 'class_name', 'evaluation_id', 'transcript_id']

class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['teacher_id','name', 'gender', 'class_name', 'phone_number', 'email', 'photo', 'position']
        
class ClassForm(forms.ModelForm):
    class Meta:
        model = Class
        fields = ['year', 'grade']
        

class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = ['title', 'summary', 'content']


class EvaluationForm(forms.ModelForm):
    class Meta:
        model = Evaluation
        exclude = ['teacher']  # 排除教师字段
       
        
class SubmittedEvaluationForm(forms.ModelForm):
    class Meta:
        model = SubmittedEvaluation
        fields = '__all__'
        
class HomeworkForm(forms.ModelForm):
    class Meta:
        model = Homework
        fields = ['title', 'content', 'start_time', 'end_time', 'remark', 'status', 'class_group']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'placeholder': '选择开始时间'}),
            'end_time': forms.DateTimeInput(attrs={'placeholder': '选择截止时间'}),
            'title': forms.TextInput(),
            'content': forms.Textarea(),
            'remark': forms.TextInput(),
            'status': forms.HiddenInput(),  # 将 status 字段设置为隐藏字段
            'class_group': forms.Select(),
        }

    def __init__(self, *args, **kwargs):
        super(HomeworkForm, self).__init__(*args, **kwargs)
        self.fields['status'].required = False  # 将 status 字段设置为非必填字段



class AttachmentForm(forms.ModelForm):
    class Meta:
        model = Attachment
        fields = ['file']
        
AttachmentFormSet = forms.inlineformset_factory(
    Homework, Attachment, form=AttachmentForm, extra=1, can_delete=True
)


class HolidayScheduleForm(forms.ModelForm):
    class Meta:
        model = HolidaySchedule
        fields = ['title', 'image']

    def clean_title(self):
        title = self.cleaned_data.get('title')
        # 在这里可以对标题进行验证或处理
        return title

from .models import ClassSchedule

class UploadExcelForm(forms.ModelForm):
    class Meta:
        model = ClassSchedule
        fields = ['class_name', 'day_of_week', 'start_time', 'end_time', 'class_info']
        
class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ['student', 'start_date', 'end_date', 'reason']
        widgets = {
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date:
            if end_date < start_date:
                raise forms.ValidationError("结束日期不能早于开始日期")

        return cleaned_data


class ProfileForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('username', 'email')  # 移除 'first_name' 和 'last_name'
        
class CustomPasswordChangeForm(PasswordChangeForm):
    class Meta:
        model = User

class ParentForm(forms.ModelForm):
    class Meta:
        model = Parent
        fields = ('phone_number','email')  # 添加需要编辑的字段

class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ('phone_number', 'email')  # 添加需要编辑的字段