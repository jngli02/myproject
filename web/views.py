from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages as msg
from django.contrib.auth import views as auth_views
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from user_sessions.models import Session
from user_sessions.models import Session as UserSession
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .utils import replace_emoji
from django.core.files.base import ContentFile
import base64

from .models import Parent

from django.http import JsonResponse
from django.http import HttpResponse
from django.template import loader
from .forms import StudentForm
from django.views.decorators.csrf import csrf_exempt
import pandas as pd
import io
import os
from django.shortcuts import get_object_or_404

from .models import Student, Evaluation, Teacher,Class,Grade,GroupMessage,DirectMessage, Homework, Attachment,StudentHomework,Submission,HolidaySchedule,ClassSchedule,LeaveRequest
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import NewsForm
from .models import News
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.core.files.storage import default_storage
from django.utils import timezone
from .forms import EvaluationForm, SubmittedEvaluation
from .forms import SubmittedEvaluationForm
from .forms import HomeworkForm, AttachmentFormSet, HolidayScheduleForm,UploadExcelForm,LeaveRequestForm

from django.db.models import Avg, Count
from collections import defaultdict
from .forms import ClassForm

from datetime import datetime

from django.contrib.sessions.models import Session
from django.urls import resolve
from openpyxl import load_workbook


def home(request):

    # 获取所有学生信息
    all_students = Student.objects.all()

    # 获取所有教师信息
    all_teachers = Teacher.objects.all()

    # 计算学生和教师的总数
    total_students = all_students.count()
    total_teachers = all_teachers.count()

    # 如果你需要获取更多的学生和教师统计信息，比如按性别、班级等分类的统计信息，你可以这样做：
    gender_distribution_students = all_students.values('gender').annotate(count=Count('id'))
    class_distribution_students = all_students.values('class_name').annotate(count=Count('id'))

    gender_distribution_teachers = all_teachers.values('gender').annotate(count=Count('id'))
    class_distribution_teachers = all_teachers.values('class_name').annotate(count=Count('id'))

    # 获取每个教师的在线状态
    teachers_online_status = {}
    for teacher in all_teachers:
        teachers_online_status[teacher.id] = is_user_online(teacher.user)

    # 统计在线和不在线人数
    online_count = sum(1 for online_status in teachers_online_status.values() if online_status)
    offline_count = total_teachers - online_count

    # 计算在线人数比例
    online_percentage = round((online_count / total_teachers) * 100, 2)

    # 星期英文到中文的映射字典
    weekday_mapping = {
        'Monday': '星期一',
        'Tuesday': '星期二',
        'Wednesday': '星期三',
        'Thursday': '星期四',
        'Friday': '星期五',
        'Saturday': '星期六',
        'Sunday': '星期日',
    }

    # 获取今天的日期
    today = datetime.now().date()

    # 获取今天是星期几
    today_weekday = today.strftime('%A')
    # 使用映射字典将英文星期转换为中文星期
    today_weekday_cn = weekday_mapping.get(today_weekday, today_weekday)
    print(today_weekday_cn)

    # 获取今天的课程表
    today_schedule = ClassSchedule.objects.filter(day_of_week=today_weekday_cn)

    # 计算课程总数
    total_classes = today_schedule.count()

    # 将数据传递给模板
    context = {
        'all_students': all_students,
        'all_teachers': all_teachers,
        'total_students': total_students,
        'total_teachers': total_teachers,
        'gender_distribution_students': gender_distribution_students,
        'class_distribution_students': class_distribution_students,
        'gender_distribution_teachers': gender_distribution_teachers,
        'class_distribution_teachers': class_distribution_teachers,
        'online_count': online_count,
        'offline_count': offline_count,
        'online_percentage': online_percentage,
        'total_classes': total_classes,
        'today_weekday': today_weekday,
    }

    return render(request, 'home.html', context)

def admin_login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_staff:  # 检查用户是否是管理员
                login(request, user)
                return redirect('a_home')  # 重定向到管理员主页
            else:
                return render(request, 'admin_login.html', {'error': '您不是管理员'})
        else:
            return render(request, 'admin_login.html', {'error': '无效的登录凭证'})
    else:
        return render(request, 'admin_login.html')

class PasswordResetView(auth_views.PasswordResetView):
    template_name = 'password_reset_form.html'
    email_template_name = 'password_reset_email.html'
    subject_template_name = 'password_reset_subject.txt'
    success_url = 'done/'

def logout_view(request):
    logout(request)
    online_users.remove(request.session.get('username'))  # 从在线用户列表中移除用户
    return redirect('login')


def create_class(request):
    if request.method == 'POST':
        # 处理班级创建和删除
        if 'create' in request.POST:
            form = ClassForm(request.POST)
            if form.is_valid():
                year = form.cleaned_data['year']
                grade = form.cleaned_data['grade']
                if Class.objects.filter(year=year, grade=grade).exists():
                    error_message = f"{year}级{grade}班已存在！"
                else:
                    form.save()
        elif 'delete' in request.POST:
            class_id = request.POST.get('delete')
            class_obj = Class.objects.get(pk=class_id)
            class_obj.delete()
        return redirect('a_home')

    form = ClassForm()
    class_list = Class.objects.all()
    return render(request, 'create_class.html', {'form': form, 'class_list': class_list})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user_type = request.POST['user_type']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            # 登录用户
            login(request, user)

            

            # 根据用户类型重定向到不同的页面
            if user_type == 'parent':
                return redirect('p_home')
            elif user_type == 'teacher':
                return redirect('t_home')
        else:
            return render(request, 'login.html', {'error': 'Invalid login credentials'})
    else:
        return render(request, 'login.html')

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        parent_name = request.POST['parent_name']
        gender = request.POST['gender']
        phone_number = request.POST['phone_number']
        email = request.POST['email']
        photo = request.FILES['photo'] if 'photo' in request.FILES else None
        children = request.POST['children']

        if password == confirm_password:
            user = User.objects.create_user(username=username, password=password, email=email)
            parent = Parent(user=user, name=parent_name, gender=gender, phone_number=phone_number, photo=photo, children=children)
            parent.save()

            # 处理孩子的学号...
            return redirect('login')
        else:
            return render(request, 'register.html', {'error': '密码和确认密码不匹配'})

    return render(request, 'register.html')

@login_required
def a_home(request):
    template = loader.get_template('a_home.html')
    return HttpResponse(template.render(request=request))

def add_student(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            student_id = form.cleaned_data.get('student_id')
            if Student.objects.filter(student_id=student_id).exists():
                msg.error(request, '学号已存在')
            else:
                form.save()
                msg.success(request, '添加成功')
        return redirect('add_student')
    else:
        form = StudentForm()
    return render(request, 'add_student.html', {'form': form})

@csrf_exempt
def add_batch(request):
    if request.method == 'POST':
        file = request.FILES['file']
        data = pd.read_excel(file)
        data = data.drop_duplicates()
        for index, row in data.iterrows():
            if '学号' in row:
                existing_student = Student.objects.filter(student_id=row['学号']).first()
                if existing_student:
                    existing_student.delete()
                    print(f"Deleted existing student with ID: {row['学号']}")

                student = Student(
                    student_id=row['学号'],
                    name=row['姓名'],
                    gender=row['性别'],
                    ethnicity=row['民族'],
                    evaluation_id=row['综合评价编号'],
                    transcript_id=row['成绩单编号']
                )
                class_name = row['班级']
                if class_name:
                    year, grade = class_name.split('级')
                    grade = grade.replace('班', '')
                    try:
                        class_group = Class.objects.get(year=year, grade=grade)
                        student.class_group = class_group
                    except Class.DoesNotExist:
                        pass
                
                student.save()
                print(f"Added new student with ID: {row['学号']}")
            elif '教师编号' in row:
                class_names = row['授课班级'].split('，')
                for class_name in class_names:
                    year, grade = class_name.split('级')
                    grade = grade.replace('班', '')
                    try:
                        class_group = Class.objects.get(year=year, grade=grade)
                        teacher, created = Teacher.objects.get_or_create(
                            teacher_id=row['教师编号'],
                            defaults={
                                'name': row['姓名'],
                                'gender': row['性别'],
                                'subject': row['授课科目'],
                                'phone_number': row['电话号码'],
                                'email': row['邮箱'],
                                'position': row['职位']
                            }
                        )
                        if not teacher.user_id:
                            username = teacher.teacher_id
                            password = str(teacher.teacher_id)
                            teacher.user = User.objects.create_user(username=username, password=password)
                            teacher.save()
                        teacher.class_groups.add(class_group)
                        print(f"Added new teacher with ID: {row['教师编号']}")
                    except Class.DoesNotExist:
                        pass
        return HttpResponseRedirect(reverse('add_batch'))
    else:
        return render(request, 'add_batch.html')
    

def upload_holiday_schedule(request):
    if request.method == 'POST':
        form = HolidayScheduleForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            # 处理表单保存成功后的逻辑
            return redirect('a_home')  # 重定向到成功页面
    else:
        form = HolidayScheduleForm()
    return render(request, 'upload_holiday_schedule.html', {'form': form})


def calendar(request):
    # 获取当前时间
    current_time = timezone.now()

    # 获取当前年份
    current_year = current_time.year

    # 根据当前年份获取对应的校历信息，如果不存在则显示管理员未上传
    try:
        calendar_entry = HolidaySchedule.objects.get(title=f"{current_year}年校历")
        calendar_image_path = calendar_entry.image.url
    except HolidaySchedule.DoesNotExist:
        # 如果当前年份的校历信息不存在，显示管理员未上传的提示信息
        calendar_image_path = None

    # 将当前年份和校历图片路径传递到前端
    context = {
        'current_year': current_year,
        'calendar_image_path': calendar_image_path
    }

    # 渲染模板并返回响应
    return render(request, 'calendar.html', context)


def add_classschedule(request):
    if request.method == 'POST':
        
        # form = request.POST.get('class_info')
        if True:
            
                file = request.FILES['file']
                file_name = file.name
                year = file_name[0:4]
                grade = file_name[-7]
                print(year,grade)
                data = pd.read_excel(file)  # 使用Pandas读取Excel文件
                # 获取班级信息
                # class_name = data.iloc[0, 0]  # 第一行的第一列单元格
                # if class_name:
                #     class_name_parts = class_name.split(' ')
                #     year = class_name_parts[0][:4]  # 假设年级信息在班级信息的前四个字符
                #     grade = class_name_parts[0][4:]  # 假设班级信息的剩余部分是班级
                #     class_obj, _ = Class.objects.get_or_create(year=year, grade=grade)

                # 固定的星期几列表
                day_of_weeks = ['星期一', '星期二', '星期三', '星期四', '星期五']

                # 获取课程信息
                rows_data = []
                for start_row in [0, 5]:  # 课程信息的起始行，使用0-based索引
                    end_row = start_row + 4  # 每个长方形表格有五行课程信息
                    for row in range(start_row, end_row):
                        time_range = data.iloc[row, 0]
                        start_time, end_time = time_range.split('-')
                        course_info = data.iloc[row, 1:6].tolist()  # 获取每行的课程信息
                        rows_data.append((start_time, end_time, course_info))

                # 处理课程表数据
                for time_data in rows_data:
                    start_time, end_time, course_info = time_data
                    for day_index, course_name in enumerate(course_info):
                        if course_name:
                            day_of_week = day_of_weeks[day_index]
                            # 存储课程表信息到数据库中
                            class_info = Class.objects.get(year=year,grade=grade)
                                
                            ClassSchedule.objects.create(
                                class_info=class_info,
                                day_of_week=day_of_week,
                                start_time=start_time,
                                end_time=end_time,
                                class_name=course_name
                            )

                return redirect('a_home')  # 重定向到成功页面，记得在urls.py中设置success_page对应的URL

    else:
        
        form = UploadExcelForm()
    
    return render(request, 'add_classschedule.html', {'form': form})




def student_info(request):
    # 从数据库中获取所有学生信息，并按照学号升序排序
    all_students = Student.objects.all().order_by('student_id')

    # 每页显示的学生数量
    per_page = 10

    # 获取搜索框中输入的学生学号
    student_id = request.GET.get('student_id')

    # 如果搜索框中有输入学号
    if student_id:
        # 尝试获取对应学生的对象
        student = Student.objects.filter(student_id=student_id).first()
        if student:
            # 获取该学生在所有学生中的索引位置
            index = list(all_students).index(student)
            # 计算该学生所在的页数
            page_number = index // per_page + 1
            # 重新定义分页器，只显示该学生所在页的学生信息
            paginator = Paginator(all_students, per_page)
            try:
                students = paginator.page(page_number)
            except EmptyPage:
                # 如果计算出的页数超出范围，则显示最后一页
                students = paginator.page(paginator.num_pages)
            except PageNotAnInteger:
                # 如果页数不是整数，则显示第一页
                students = paginator.page(1)
            # 渲染页面并传递学生信息
            return render(request, 'student_info.html', {'students': students, 'searched_student': student})
        else:
            # 如果未找到对应学生，则显示所有学生信息
            paginator = Paginator(all_students, per_page)
            page_number = request.GET.get('page')
            students = paginator.get_page(page_number)
            messages.error(request, '未找到该学生')
            return render(request, 'student_info.html', {'students': students})

    # 如果请求的方法是POST，说明是删除
    if request.method == 'POST':
        # 获取要删除的学生ID
        delete_id = request.POST.get('delete_id')
        # 如果存在要删除的学生ID
        if delete_id:
            # 根据学生ID获取学生对象
            student = get_object_or_404(Student, id=delete_id)
            # 如果找到了对应的学生对象，则执行删除操作
            if student:
                # 删除学生对象
                student.delete()
                # 返回删除成功的消息
                messages.success(request, '删除成功')
            else:
                # 返回学生不存在的消息
                messages.error(request, '学生不存在')
            # 重定向到当前页面，以防止重复提交表单
            return redirect('student_info')

    # 如果未搜索学生，则显示所有学生信息
    paginator = Paginator(all_students, per_page)
    page_number = request.GET.get('page')
    students = paginator.get_page(page_number)
    # 渲染页面并传递学生信息
    return render(request, 'student_info.html', {'students': students})

def delete_student(request):
    if request.method == 'POST':
        delete_id = request.POST.get('delete_id')
        if delete_id:
            student = get_object_or_404(Student, id=delete_id)
            student.delete()
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error', 'message': '未提供学生ID'})
    else:
        return JsonResponse({'status': 'error', 'message': '无效的请求方法'})

def update_student(request, student_id):
    # 根据学生ID获取学生对象
    student = get_object_or_404(Student, id=student_id)
    
    if request.method == 'POST':
        # 创建一个表单实例并用POST数据填充它
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()  # 保存更新后的学生信息
            return redirect('student_info')  # 重定向到学生信息页面
    else:
        # 如果请求是GET，创建一个表单并将学生对象的数据传递给它
        form = StudentForm(instance=student)
    
    # 渲染模板并传递表单和学生对象
    return render(request, 'update_student.html', {'form': form, 'student': student})


# def add_news(request):
#     if request.method == 'POST':
#         form = NewsForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return HttpResponseRedirect(reverse('news_list') + '?added=true')
#     else:
#         form = NewsForm()
#     return render(request, 'add_news.html', {'form': form})

def news_list(request):
    news_added = request.GET.get('added') == 'true'
    news = News.objects.all().order_by('-add_time')
    return render(request, 'news_list.html', {'news': news, 'news_added': news_added})

def news_detail(request, news_id):
    news = get_object_or_404(News, id=news_id)
    return render(request, 'news_detail.html', {'news': news})

def teacher_info(request):
    if request.method == 'POST':
        # 获取要删除的教师的用户名
        username = request.POST.get('delete_username')
        if username:
            # 根据用户名获取要删除的教师对象
            teacher = Teacher.objects.filter(user__username=username).first()
            if teacher:
                # 删除教师对象
                user = teacher.user
                teacher.delete()
                user.delete()
                msg.success(request, '删除成功')
            else:
                msg.error(request, '教师不存在')

            return redirect('teacher_info')  # 立即重定向到相同的页面

    all_teachers = Teacher.objects.all().order_by('teacher_id')
    per_page = 10
    teacher_id = request.GET.get('teacher_id')

    if teacher_id:
        teacher = Teacher.objects.filter(teacher_id=teacher_id).first()
        if teacher:
            index = list(all_teachers).index(teacher)
            page_number = index // per_page + 1
            paginator = Paginator(all_teachers, per_page)
            try:
                teachers = paginator.page(page_number)
            except EmptyPage:
                teachers = paginator.page(paginator.num_pages)
            except PageNotAnInteger:
                teachers = paginator.page(1)

            return render(request, 'teacher_info.html', {'teachers': teachers, 'searched_teacher': teacher})
        else:
            paginator = Paginator(all_teachers, per_page)
            page_number = request.GET.get('page')
            teachers = paginator.get_page(page_number)
            msg.error(request, '未找到该教师')
            return render(request, 'teacher_info.html', {'teachers': teachers})

    paginator = Paginator(all_teachers, per_page)
    page_number = request.GET.get('page')
    teachers = paginator.get_page(page_number)

    return render(request, 'teacher_info.html', {'teachers': teachers})

def update_teacher(request, teacher_id):
    # 获取对应的教师对象
    teacher = get_object_or_404(Teacher, id=teacher_id)

    if request.method == 'POST':
        # 更新教师信息
        teacher.teacher_id = request.POST.get('teacher_id')
        teacher.name = request.POST.get('name')
        teacher.gender = request.POST.get('gender')
        teacher.class_name = request.POST.get('class_name')
        teacher.subject = request.POST.get('subject')
        teacher.phone_number = request.POST.get('phone_number')
        teacher.email = request.POST.get('email')
        teacher.position = request.POST.get('position')

        # 获取上传的文件
        file = request.FILES.get('photo')
        if file:
            # 将文件保存为教师对象的 photo 属性
            teacher.photo.save(file.name, file)

        # 保存教师对象
        teacher.save()

        # 重定向到教师信息页面
        return redirect('teacher_info')

    # 如果请求的方法不是 POST，那么渲染更新教师信息的页面
    return render(request, 'update_teacher.html', {'teacher': teacher})

def delete_teacher(request):
    if request.method == 'POST':
        # 获取要删除的教师的教师编号
        teacher_id = request.POST.get('teacher_id')

        # 根据教师编号获取教师对象
        teacher = Teacher.objects.filter(teacher_id=teacher_id).first()

        if teacher:
            # 删除教师对象
            user = teacher.user
            teacher.delete()
            if user:
                user.delete()
            messages.success(request, '删除成功')
        else:
            messages.error(request, '教师不存在')

        # 重定向到添加批量教师界面
        return redirect('add_batch')

def update_photo(request, teacher_id):
    # 获取对应的教师对象
    teacher = get_object_or_404(Teacher, id=teacher_id)

    if request.method == 'POST':
        # 获取上传的文件
        file = request.FILES.get('photo')

        if file:
            # 将文件保存为教师对象的 photo 属性
            teacher.photo.save(file.name, file)
            teacher.save()

        # 重定向到教师信息页面
        return redirect('teacher_info')


#家长界面
def p_home(request):
    # 获取当前登录的家长对象
    parent = Parent.objects.get(user=request.user)
    
    # 获取家长的孩子的学号
    children_ids = parent.children.split(',') if parent.children else []

    # 获取家长的所有孩子的信息
    children = Student.objects.filter(student_id__in=children_ids)

    # 将家长的孩子信息传递给模板
    return render(request, 'p_home.html', {'children': children})

def p_student_info(request):
    # 获取对应的家长对象
    parent = Parent.objects.get(user=request.user)

    # 获取家长的孩子的学号
    children_ids = parent.children.split(',') if parent.children else []

    # 获取家长的所有孩子的信息
    children = Student.objects.filter(student_id__in=children_ids)

    # 渲染页面并传递孩子信息
    return render(request, 'p_student_info.html', {'children': children})


#使用教师界面的s_exam_scores的视图查看学生成绩

def is_user_online(user):
    # 获取当前用户的所有会话
    user_sessions = Session.objects.filter(expire_date__gte=timezone.now())
    # 遍历会话列表，检查用户是否在线
    for session in user_sessions:
        session_data = session.get_decoded()
        if str(user.id) == session_data.get('_auth_user_id'):
            return True
    return False


def class_group(request, class_id):
    # 获取班级对象
    class_group = get_object_or_404(Class, id=class_id)

    # 获取班级的所有教师
    teachers = class_group.teachers.all()
    t = {}
    for teacher in teachers:
        t[teacher.user.id] = is_user_online(teacher.user)
    teachers_info_all = [{'id': teacher.id, 'name': teacher.name, 'subject': teacher.subject, 'user_id': teacher.user_id, 'is_online': t[teacher.user.id]} for teacher in teachers]

    # 获取班级的所有学生
    students = Student.objects.filter(class_group=class_group)

    # 获取班级的所有家长，并获取他们的孩子的信息
    parent_children_map = defaultdict(list)
    for student in students:
        for parent in Parent.objects.filter(children__contains=student.student_id):
            parent_children_map[parent.user.username].append(student.name)

    # 获取所有家长的用户ID列表
    parent_user_ids = [parent.user.id for parent in Parent.objects.filter(user__username__in=parent_children_map.keys())]

    # 获取所有用户的在线状态
    user_online_status = {user_id: is_user_online(User.objects.get(id=user_id)) for user_id in parent_user_ids}

    # 构建家长信息列表，并添加在线状态
    parents_info_all = []
    for username, children in parent_children_map.items():
        parent = Parent.objects.get(user__username=username)
        parents_info_all.append({
            'id': parent.id,
            'username': username,
            'children': ', '.join(children),
            'user_id': parent.user_id,
            'is_online': user_online_status.get(parent.user.id, False)  # 获取对应用户ID的在线状态，如果不存在则默认为False
        })

    # 获取历史消息
    messages = GroupMessage.objects.filter(class_group_id=class_id)

    if request.method == 'GET':
        # 渲染页面并传递教师和家长信息以及班级ID和消息列表
        return render(request, 'class_group.html', {'class_group': class_group, 'class_id': class_id, 'messages': messages, 'teachers_info_all': teachers_info_all, 'parents_info_all': parents_info_all})

    elif request.method == 'POST':
        sender = request.user
        class_group_id = class_id
        content = request.POST.get('content')
        image = request.FILES.get('image')  # 获取上传的图片文件

        # 保存图片到服务器上的指定路径
        if image:
            image_name = image.name
            image_path = os.path.join(settings.MEDIA_ROOT, 'images', image_name)
            with open(image_path, 'wb') as f:
                for chunk in image.chunks():
                    f.write(chunk)

            # 构造图片的HTML标签
            image_tag = f'<img src="/media/images/{image_name}" alt="{image_name}">'
            content += f'<br>{image_tag}'
            
        # 替换消息内容中的表情代码为表情图片标签
        content = replace_emoji(content)

        # 保存消息到数据库
        GroupMessage.objects.create(sender=sender, class_group_id=class_group_id, content=content)

        # 获取历史消息
        messages = GroupMessage.objects.filter(class_group_id=class_id)

        # 返回渲染后的页面，包括教师和家长信息以及班级ID和消息列表
        return render(request, 'class_group.html', {'class_group': class_group, 'class_id': class_id, 'messages': messages, 'teachers_info_all': teachers_info_all, 'parents_info_all': parents_info_all})
    else:
        return JsonResponse({'error': 'Invalid request method'})

def direct_chat(request, user_id, class_id):
    user = request.user
    chat_partner = get_object_or_404(User, id=user_id) #对话者
    
    # 检查是否是同一个用户
    if user == chat_partner:
        msg.error(request, "You cannot chat with yourself.")
        return HttpResponseRedirect(reverse('class_group', args=(class_id,)))  # 重定向到class_group界面

    if request.method == 'POST':
        # 处理 POST 请求
        content = request.POST.get('content', None)
        image_data = request.POST.get('image_data', None)  # 获取图片的base64编码数据

        # 处理上传的图片
        if image_data:
            # 从base64编码的数据中获取图片数据
            format, imgstr = image_data.split(';base64,') 
            ext = format.split('/')[-1] 

            # 创建一个新的图片文件
            image = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

            # 创建 DirectMessage 实例并保存到数据库
            DirectMessage.objects.create(sender=user, receiver=chat_partner, image=image)

        # 处理表情
        if content:
            # 替换消息内容中的表情代码为表情图片标签
            content = replace_emoji(content)

            # 创建 DirectMessage 实例并保存到数据库
            DirectMessage.objects.create(sender=user, receiver=chat_partner, content=content)

        # 重定向到私聊页面以避免表单重复提交
        return HttpResponseRedirect(reverse('direct_chat', args=(user_id, class_id)))

    messages = DirectMessage.objects.filter(sender=user, receiver=chat_partner) | DirectMessage.objects.filter(sender=chat_partner, receiver=user)
    
    return render(request, 'direct_chat.html', {'chat_partner': chat_partner, 'messages': messages, 'user_id': user_id, 'class_id': class_id})


def homework_info(request):
    if request.user.is_authenticated:
        # 获取对应的家长对象
        parent = Parent.objects.get(user=request.user)

        # 获取家长的孩子的学号
        children_ids = parent.children.split(',') if parent.children else []

        # 获取家长的所有孩子的信息
        children = Student.objects.filter(student_id__in=children_ids)
        homework_list = []

        for child in children:
            # 获取特定孩子所在的班级
            class_group = child.class_group
            # 获取该班级下的作业列表
            child_homework = Homework.objects.filter(class_group=class_group)
            child_submission_info = []
            
            for hw in child_homework:
                # 获取学生对应的作业信息
                student_homework = StudentHomework.objects.filter(student=child, homework=hw).first()
                if student_homework:
                    # 获取学生的提交信息
                    submission = Submission.objects.filter(student_homework=student_homework).first()

                    # 获取教师的批改内容和评分
                    if submission:
                        grading = submission.grading
                        approval_comment = submission.approval_comment

                    child_submission_info.append({
                        'homework': hw,
                        'student_homework': student_homework,
                        'submission': submission,
                        'grading': grading,
                        'approval_comment': approval_comment
                    })
                else:
                    child_submission_info.append({
                        'homework': hw,
                        'student_homework': None,
                        'submission': None,
                        'grading': None,
                        'approval_comment': ""
                    })

            homework_list.append({'child': child, 'submission_info': child_submission_info})

        return render(request, 'homework_info.html', {'homework_list': homework_list, 'parent_info': parent})
    else:
        # 如果用户未登录，可以根据需要进行重定向或显示错误信息
        return render(request, 'error.html', {'error_message': 'Please login to view homework.'})



def view_homework_submissions(request):
    if request.method == 'POST':
        submission_id = request.POST.get('submission_id')
        grade = request.POST.get('grade')
        approval_comment = request.POST.get('approval_comment')

        # 获取提交记录对象
        submission = get_object_or_404(Submission, pk=submission_id)

        # 保存评分和审批意见到提交记录对象中
        submission.grading = grade
        submission.approval_comment = approval_comment
        submission.graded = True
        submission.save()

        return JsonResponse({'message': '评分和审批意见已保存'})

    # 假设教师已经登录，获取当前登录的教师
    if hasattr(request.user, 'teacher'):
        teacher = request.user.teacher
    else:
        return HttpResponse("当前用户不是教师，请使用教师账号登录")

    # 获取教师所授的班级列表
    class_groups = teacher.class_groups.all()

    # 获取班级ID（如果通过GET请求传递）
    class_id = request.GET.get('class_id')

    # 初始化学生作业信息列表
    students_with_homework = []

    if not class_id:
        # 如果没有班级ID，即选择了全部班级，则获取所有班级的学生作业信息
        for class_group in class_groups:
            # 获取该班级的所有学生作业记录，按提交时间降序排序
            student_homeworks = StudentHomework.objects.filter(student__class_group=class_group)
            # 遍历学生作业记录
            for student_homework in student_homeworks:
                submission = Submission.objects.filter(student_homework=student_homework).first()
                submitted_at = submission.submitted_at if submission else None
                students_with_homework.append({
                    'student': student_homework.student,
                    'homework_title': student_homework.homework.title,
                    'submitted_at': submitted_at,
                    'answer': submission.answer if submission else None,
                    'attachment': submission.attachment.url if submission and submission.attachment else None,
                    'graded': student_homework.graded,  # 获取批阅信息
                    'submitted': True if submission else False,  # 检查是否已提交
                })
    else:
        # 如果有班级ID，获取该班级的学生作业信息
        class_group = get_object_or_404(Class, id=class_id)
        # 获取该班级的所有学生作业记录，按提交时间降序排序
        student_homeworks = StudentHomework.objects.filter(student__class_group=class_group)
        # 遍历学生作业记录
        for student_homework in student_homeworks:
            submission = Submission.objects.filter(student_homework=student_homework).first()
            submitted_at = submission.submitted_at if submission else None
            students_with_homework.append({
                'student': student_homework.student,
                'homework_title': student_homework.homework.title,
                'submitted_at': submitted_at,
                'answer': submission.answer if submission else None,
                'attachment': submission.attachment.url if submission and submission.attachment else None,
                'graded': student_homework.graded,  # 获取批阅信息
                'submitted': True if submission else False,  # 检查是否已提交
            })

    context = {
        'class_groups': class_groups,
        'students_with_homework': students_with_homework,
        'selected_class_id': class_id,
    }

    return render(request, 'view_homework_submissions.html', context)


def p_classschedule(request):
    parent = request.user.parent
    children_ids = [int(id) for id in parent.children.split(',') if id.strip()]
    children = Student.objects.filter(student_id__in=children_ids)
    schedules = []
    
    # 获取所有孩子的所有课程安排
    all_schedules = []
    for child in children:
        child_schedules = ClassSchedule.objects.filter(class_info=child.class_group)
        all_schedules.extend(child_schedules)
    
    # 获取所有不重复的时间段
    unique_times = sorted(set((schedule.start_time.strftime("%H:%M"), schedule.end_time.strftime("%H:%M")) for schedule in all_schedules))
    
    # 构建时间表格
    timetable = {}
    for schedule in all_schedules:
        class_name = schedule.class_info.__str__()
        if class_name not in timetable:
            timetable[class_name] = {}
            for time_range in unique_times:
                timetable[class_name][time_range] = {day_of_week: None for day_of_week in ['星期一', '星期二', '星期三', '星期四', '星期五']}
    
    # 填充时间表格
    for schedule in all_schedules:
        start_time = schedule.start_time.strftime("%H:%M")
        end_time = schedule.end_time.strftime("%H:%M")
        class_name = schedule.class_info.__str__()
        timetable[class_name][(start_time, end_time)][schedule.day_of_week] = schedule.class_name
        
    # 获取当前时间
    current_time = timezone.now().strftime("%H:%M")

    # 构建每个孩子当前时间的课程表
    children_current_schedules = {}
    for child in children:
        current_schedule = ClassSchedule.objects.filter(
            class_info=child.class_group,
            start_time__lte=current_time,
            end_time__gte=current_time,
            day_of_week__in=['星期一', '星期二', '星期三', '星期四', '星期五']  # 仅查询星期一至星期五的课程
        ).first()
        if current_schedule:
            children_current_schedules[child.name] = current_schedule.class_name
        else:
            children_current_schedules[child.name] = "无课程"

    # 如果是星期六或星期天，则将当前上课信息置为空
    today = timezone.now().weekday()  # 获取今天是星期几，星期一为0，星期天为6
    if today >= 5:  # 如果是星期六或星期天
        for child_name in children_current_schedules:
            children_current_schedules[child_name] = "无课程"

    
    return render(request, 'p_classschedule.html', {'timetable': timetable, 'children_current_schedules': children_current_schedules, 'children': children})



@login_required
def leave_request(request):
    if request.method == 'POST':
        student_id = request.POST.get('student')
        start_date_str = request.POST.get('start_date')
        start_time_str = request.POST.get('start_time')
        end_date_str = request.POST.get('end_date')
        end_time_str = request.POST.get('end_time')
        reason = request.POST.get('reason')
        
        # 获取对应的家长对象
        parent = Parent.objects.get(user=request.user)

        # 获取家长的孩子的学号
        children_ids = parent.children.split(',') if parent.children else []

        # 获取学生对象
        student = Student.objects.get(pk=student_id)
        
        # 将日期和时间字符串合并为datetime对象
        start_datetime_str = f"{start_date_str} {start_time_str}"
        end_datetime_str = f"{end_date_str} {end_time_str}"
        start_datetime = datetime.strptime(start_datetime_str, '%Y-%m-%d %H:%M')
        end_datetime = datetime.strptime(end_datetime_str, '%Y-%m-%d %H:%M')

        # 创建请假申请记录
        leave_request = LeaveRequest.objects.create(
            parent=parent,
            student=student,
            start_date=start_datetime,
            end_date=end_datetime,
            reason=reason,
            approved=False  # 默认为未批准
        )
        return redirect('p_home')  # 重定向到成功页面或其他页面

    else:
        # 获取当前家长的孩子列表
        parent = Parent.objects.get(user=request.user)
        children_ids = parent.children.split(',') if parent.children else []
        children = Student.objects.filter(student_id__in=children_ids)
        
        # 获取每个孩子的所有请假记录
        leave_records = []
        for child in children:
            leave_records.extend(LeaveRequest.objects.filter(student=child))
        
        return render(request, 'leave_request.html', {'parent_children': children, 'leave_records': leave_records})






#教师界面
def t_home(request):
    # 获取当前用户教师对象
    teacher = Teacher.objects.get(user=request.user)
    print(teacher.teacher_id)
    # 获取该教师所教的班级
    class_groups = teacher.class_groups.all()
    # 将班级信息传递到模板中
    return render(request, 't_home.html', {'class_groups': class_groups,'teacher': teacher})

@csrf_exempt
def t_student_info(request):

    # 假设教师已经登录，获取当前登录的教师
    if hasattr(request.user, 'teacher'):
        teacher = request.user.teacher
    else:
        # 如果当前用户没有关联到教师对象，可以进行相应处理，比如返回错误页面或重定向到登录页面
        # 这里你可以根据实际需求进行修改
        return HttpResponse("当前用户不是教师，请使用教师账号登录")


    # 获取教师所授的班级列表
    class_groups = teacher.class_groups.all()
    # for e in class_groups:
    #     print(e)
    # 获取班级ID（如果通过GET请求传递）
    class_id = request.GET.get('class_id')

    # 如果有班级ID，获取该班级的学生列表
    students = []
    if class_id:
        class_group = Class.objects.get(id=class_id)
        students = class_group.students.all()

    # 处理表单提交逻辑
    if request.method == 'POST':
        # 处理添加综合评价和考试成绩单的逻辑
        # 这里添加你的处理代码
        pass

    return render(request, 't_student_info.html', {'class_groups': class_groups, 'students': students})


def evaluation_history(request, student_id):
    try:
        #家长获取学生综合评价信息
        student = Student.objects.get(student_id=student_id)
        evaluations = SubmittedEvaluation.objects.filter(student=student)
        print(student)
        print(student_id)
    except:
        # 教师获取该学生的所有提交的综合评价信息
        evaluations = SubmittedEvaluation.objects.filter(student_id=student_id)
    
    return render(request, 'evaluation_history.html', {'evaluations': evaluations})

def evaluation(request, student_id):
    # 获取学生的信息
    student = Student.objects.get(id=student_id)

    # 获取当前的日期和时间
    current_time = timezone.now()

    # 获取当前月份的评价
    evaluation = Evaluation.objects.filter(student=student).first()

    # 如果评价不存在，创建一个新的评价
    if not evaluation:
        evaluation = Evaluation(student=student)
        evaluation.save()

    # 检查是否在web_submittedevaluation表中存在学生的信息
    submitted_evaluation_exists = SubmittedEvaluation.objects.filter(student=student).exists()

    # 获取当前教师的授课科目
    subject = request.user.teacher.subject

    # 实例化表单时，传递学生和日期信息
    form = EvaluationForm(instance=evaluation, initial={'student': student, 'date': current_time})

    if request.method == 'POST':
        form = EvaluationForm(request.POST, instance=evaluation)
        if form.is_valid():
            if 'save' in request.POST:
                form.save()  # 在这里保存Evaluation对象
                alert_message = '保存成功！'
            elif 'submit' in request.POST:
                # 如果已存在提交的评价，禁止再次提交
                if submitted_evaluation_exists:
                    alert_message = '已提交的评价不能再次提交！'
                else:
                    # 使用SubmittedEvaluationForm来创建一个新的SubmittedEvaluation对象
                    submitted_evaluation_form = SubmittedEvaluationForm(request.POST)
                    if submitted_evaluation_form.is_valid():
                        # 将表单的数据保存到SubmittedEvaluation对象中
                        submitted_evaluation = submitted_evaluation_form.save(commit=False)
                        submitted_evaluation.student = student
                        submitted_evaluation.save()
                        # 更改原来的Evaluation对象的状态为已提交
                        evaluation.status = 'submitted'
                        evaluation.save()
                        alert_message = '提交成功！'
                    else:
                        # 打印表单的错误信息
                        print(submitted_evaluation_form.errors)
                        alert_message = '提交失败，请检查表单信息！'  # 添加错误提示
            return redirect('t_student_info')
        else:
            # 如果表单验证失败，也应该提供正确的表单实例以显示错误消息
            form = EvaluationForm(instance=evaluation, initial={'student': student, 'date': current_time})

    # 如果当前教师的授课科目不是心理或体育，移除"心理健康"和"身体素质"这两个字段
    if subject not in ['心理', '体育']:
        del form.fields['mental_health']
        del form.fields['mental_health_notes']
        del form.fields['physical_fitness']
        del form.fields['physical_fitness_notes']

    return render(request, 'evaluation.html', {'form': form, 'student': student, 'current_time': current_time, 'submitted_evaluation_exists': submitted_evaluation_exists})

def t_add_grades(request):
    if request.method == 'POST':
        # 使用 'file' 来获取文件字段
        excel_file = request.FILES['file']
        data = pd.read_excel(excel_file)
        for i, row in data.iterrows():
            # 修改这里以匹配学号和学生姓名列名
            student_id = row['学号']
            student_name = row['姓名']
            # 使用学号和学生姓名获取学生对象
            student = Student.objects.get(student_id=student_id, name=student_name)
            grade = Grade(
                student=student,
                exam_time=row['考试时间'],
                exam_type=row['考试类型'],
                chinese=row['语文'],
                math=row['数学'],
                physics=row['物理'],
                chemistry=row['化学'],
                english=row['英语'],
                biology=row['生物'],
                politics=row['政治'],
                history=row['历史'],
                geography=row['地理'],
                remarks=row['备注'],
                total=row['总分']
            )
            # 计算总分
            grade.save()
        return render(request, 't_add_grades.html')
    else:
        return render(request, 't_add_grades.html')

def s_exam_scores(request, student_id):
    # 获取该学生的所有考试成绩并按时间排序
    try:
        student = Student.objects.get(student_id=student_id)
        print(student)
        exam_scores = Grade.objects.filter(student=student).order_by('-exam_time')
    except:
        exam_scores = Grade.objects.filter(student_id=student_id).order_by('-exam_time')
    # 渲染模板并将考试成绩传递给模板
    return render(request, 's_exam_scores.html', {'exam_scores': exam_scores})

def class_exam_scores(request, class_id):
    # 获取指定班级的所有成绩，包含学生姓名
    exam_scores = Grade.objects.filter(student__class_group_id=class_id).select_related('student')
    
    exam_dates = exam_scores.values_list('exam_time', flat=True).distinct()
    
    # 计算每个日期的总分平均分和各科平均分
    scores_datas = []
    for exam_date in exam_dates:
        scores = Grade.objects.filter(exam_time=exam_date)
        total_average = scores.aggregate(Avg('total'))['total__avg']
        subject_averages = scores.aggregate(
            Avg('chinese'), Avg('math'), Avg('physics'), Avg('chemistry'), 
            Avg('english'), Avg('biology'), Avg('politics'), Avg('history'), Avg('geography')
        )
        print(exam_date.strftime("%Y-%m-%d"))
        scores_datas.append({
            'exam_date': exam_date,  # 将日期对象转换为字符串格式
            'total_average': total_average,
            'subject_averages': {
                '语文': subject_averages['chinese__avg'],
                '数学': subject_averages['math__avg'],
                '物理': subject_averages['physics__avg'],
                '化学': subject_averages['chemistry__avg'],
                '英语': subject_averages['english__avg'],
                '生物': subject_averages['biology__avg'],
                '政治': subject_averages['politics__avg'],
                '历史': subject_averages['history__avg'],
                '地理': subject_averages['geography__avg'],
            }
        })
    # 渲染模板
    return render(request, 'class_exam_scores.html', {'exam_scores': exam_scores,'scores_datas': scores_datas,'class_id': class_id})


def add_homework(request, teacher_id):
    try:
        teacher = Teacher.objects.get(id=teacher_id)
    except Teacher.DoesNotExist:
        print("Teacher not found:", teacher_id)
        return redirect('teacher_not_found')

    if request.method == 'POST':
        form = HomeworkForm(request.POST, request.FILES)
        if form.is_valid():
            # 保存作业表单数据
            homework = form.save(commit=False)
            homework.teacher = teacher

            # 设置作业状态
            now = timezone.now()
            if now < homework.start_time:
                homework.status = "未开始"
            elif now > homework.end_time:
                homework.status = "已超时"
            else:
                homework.status = "可作答"

            homework.save()

            # 处理附件上传
            file = request.FILES.get('file')
            if file:
                attachment = Attachment.objects.create(homework=homework, file=file)

            # 获取选定的班级
            selected_class = homework.class_group

            # 为选定的班级中的每个学生创建 StudentHomework 记录
            for student in Student.objects.filter(class_group=selected_class):
                StudentHomework.objects.create(student=student, homework=homework)

            return redirect('add_homework', teacher_id=teacher_id)
        else:
            print("Form errors:", form.errors)
    else:
        form = HomeworkForm()

    return render(request, 'add_homework.html', {'form': form, 'teacher': teacher})


def t_classschedule(request):
    # 获取当前教师所教的班级
    teacher = request.user.teacher
    class_groups = teacher.class_groups.all()
    
    # 获取教师所教的唯一科目
    subject = teacher.subject
    
    # 获取所有班级的课程安排
    all_schedules = []
    for class_group in class_groups:
        class_schedules = ClassSchedule.objects.filter(class_info=class_group)
        all_schedules.extend(class_schedules)
    
    # 获取所有不重复的时间段
    unique_times = sorted(set((schedule.start_time.strftime("%H:%M"), schedule.end_time.strftime("%H:%M")) for schedule in all_schedules))
    
    # 构建时间表格
    timetable = {}
    for schedule in all_schedules:
        class_name = schedule.class_info.__str__()
        if class_name not in timetable:
            timetable[class_name] = {}
            for time_range in unique_times:
                timetable[class_name][time_range] = {day_of_week: None for day_of_week in ['星期一', '星期二', '星期三', '星期四', '星期五']}
    
    # 填充时间表格
    for schedule in all_schedules:
        start_time = schedule.start_time.strftime("%H:%M")
        end_time = schedule.end_time.strftime("%H:%M")
        class_name = schedule.class_info.__str__()
        timetable[class_name][(start_time, end_time)][schedule.day_of_week] = schedule.class_name
    
    # 获取当前时间
    current_time = timezone.now().strftime("%H:%M")
    
    # 构建每个班级当前时间的课程表
    class_current_schedules = {}
    for class_group in class_groups:
        # 仅查询星期一至星期五的课程
        current_schedule = ClassSchedule.objects.filter(
            class_info=class_group,
            start_time__lte=current_time,
            end_time__gte=current_time,
            day_of_week__in=['星期一', '星期二', '星期三', '星期四', '星期五']
        ).first()
        if current_schedule:
            class_current_schedules[class_group.__str__()] = current_schedule.class_name
        else:
            class_current_schedules[class_group.__str__()] = "无课程"
    
    # 如果是星期六或星期天，则将当前上课信息置为空
    today = timezone.now().weekday()  # 获取今天是星期几，星期一为0，星期天为6
    if today >= 5:  # 如果是星期六或星期天
        for class_group_name in class_current_schedules:
            class_current_schedules[class_group_name] = "无课程"
    
    return render(request, 't_classschedule.html', {'timetable': timetable, 'class_current_schedules': class_current_schedules, 'class_groups': class_groups, 'subject': subject})


@login_required
def leave_approval(request):
    # 首先确保用户是教师
    if not request.user.is_authenticated or not hasattr(request.user, 'teacher'):
        return JsonResponse({'error': '您不是教师，无法进行此操作'}, status=403)

    # 获取当前教师对象
    teacher = request.user.teacher
    
    now = timezone.now()
    
    # 获取教师所教授的班级和职位
    teacher_class_groups = teacher.class_groups.all()
    teacher_position = teacher.position

    # 获取学生请假记录
    leave_requests = LeaveRequest.objects.filter(student__class_group__in=teacher_class_groups)

    if request.method == 'POST':
        # 处理请假批准、拒绝、销假或未返校操作
        request_id = request.POST.get('request_id')
        action = request.POST.get('action')

        # 获取请假记录对象
        leave_request = LeaveRequest.objects.get(pk=request_id)
        
        # 检查教师是否有权限进行操作
        student_class = leave_request.student.class_group

        if str(student_class) in teacher_position:
            if '班主任' in teacher_position:
                # 根据操作类型更新请假记录状态
                if action == 'approve':
                    leave_request.approved = True
                    leave_request.status = '假期中'
                elif action == 'reject':
                    leave_request.approved = False
                    leave_request.status = '未批假'
                elif action == 'cancel':
                    leave_request.approved = False
                    leave_request.status = '已销假'
                elif action == 'not_returned':
                    leave_request.status = '未返校'
                
                # 保存更新后的请假记录
                leave_request.save()
            else:
                return JsonResponse({'error': '您不是班主任，无法进行此操作'}, status=403)
        else:
            return JsonResponse({'error': '您不是本班班主任，无法进行此操作'}, status=403)

    # 将更新后的记录信息传递到前端并渲染页面
    return render(request, 'leave_approval.html', {'leave_requests': leave_requests, 'teacher_position': teacher_position, 'now': now})




#共用界面
def user_detail(request, user_id):
    # 尝试从 Teacher 表中获取用户信息
    teacher = Teacher.objects.filter(id=user_id).first()

    # 如果在 Teacher 表中找不到用户信息，则尝试从 Parent 表中获取用户信息
    if not teacher:
        parent = Parent.objects.filter(id=user_id).first()
    else:
        parent = None  # 如果在 Teacher 表中找到了用户信息，则不需要在 parent 中设置任何值

    # 渲染模板并将相应用户信息传递给模板
    return render(request, 'user_detail.html', {'teacher': teacher, 'parent': parent})


def submit_homework(request, homework_id, student_id):
    # 获取作业对象
    homework = get_object_or_404(Homework, id=homework_id)
    print(homework.id)
    
    # 获取学生对象
    student = get_object_or_404(Student, id=student_id)
    print(student)
    # 获取或创建学生作业记录
    student_homework, created = StudentHomework.objects.get_or_create(student=student.id, homework=homework.id)
    print(student_homework.id)
    if request.method == 'POST':
        # 处理提交表单
        answer = request.POST.get('answer')
        attachment = request.FILES.get('attachment')

        # 创建或更新提交记录
        submission, submission_created = Submission.objects.get_or_create(student_homework=student_homework)
        submission.answer = answer
        if attachment:
            submission.attachment = attachment
        submission.save()

        # 标记作业为已提交
        student_homework.submitted = True
        student_homework.save()

        # 重定向到作业信息页面或其他适当页面
        return redirect('homework_info')

    return render(request, 'submit_homework.html', {'homework': homework})



def view_submissions(request, homework_id):
    # 获取作业对象
    homework = get_object_or_404(Homework, id=homework_id)
    
    # 获取该作业的所有已提交的作业信息
    submissions = Submission.objects.filter(student_homework__homework=homework)
    
    return render(request, 'view_submissions.html', {'homework': homework, 'submissions': submissions})

















