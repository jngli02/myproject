from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout

from .models import Parent

from django.http import JsonResponse
from django.http import HttpResponse
from django.template import loader
from .forms import StudentForm
from django.views.decorators.csrf import csrf_exempt
import pandas as pd
import io
from django.shortcuts import get_object_or_404

from .models import Student
from .models import Teacher
from .models import Class
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import NewsForm
from .models import News
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.core.files.storage import default_storage



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
    return redirect('login')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user_type = request.POST['user_type']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            # 用户验证成功后，将用户名存储在 session 中
            request.session['username'] = username

            if user_type == 'parent':
                try:
                    parent = Parent.objects.get(user=user)  # 在 Parent 表中查找用户
                except Parent.DoesNotExist:
                    return render(request, 'login.html', {'error': 'Parent account does not exist'})
            elif user_type == 'teacher':
                try:
                    teacher = Teacher.objects.get(user=user)  # 在 Teacher 表中查找用户
                except Teacher.DoesNotExist:
                    return render(request, 'login.html', {'error': 'Teacher account does not exist'})

            login(request, user)

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

def a_home(request):
    template = loader.get_template('a_home.html')
    return HttpResponse(template.render(request=request))

def add_student(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            student_id = form.cleaned_data.get('student_id')
            if Student.objects.filter(student_id=student_id).exists():
                messages.error(request, '学号已存在')
            else:
                form.save()
                messages.success(request, '添加成功')
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
                teacher_id = row['教师编号']
                existing_teacher = Teacher.objects.filter(teacher_id=teacher_id).first()
                if existing_teacher and existing_teacher.user:
                    existing_user = existing_teacher.user
                    if existing_teacher:
                        existing_teacher.delete()
                    existing_user.delete()
                    print(f"Deleted existing teacher with ID: {teacher_id}")

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
                messages.success(request, '删除成功')
            else:
                messages.error(request, '教师不存在')

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
            messages.error(request, '未找到该教师')
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
    template = loader.get_template('p_home.html')
    return HttpResponse(template.render(request=request))

def p_student_info(request):
    # 获取对应的家长对象
    parent = Parent.objects.get(user=request.user)

    print('parent.children:', parent.children)  # 调试代码

    # 获取家长的孩子的学号
    children_ids = parent.children.split(',') if parent.children else []
    print('children_ids:', children_ids)  # 调试代码

    # 获取家长的所有孩子的信息
    children = Student.objects.filter(student_id__in=children_ids)
    print('children:', children)  # 调试代码

    # 渲染页面并传递孩子信息
    return render(request, 'p_student_info.html', {'children': children})



#教师界面
def t_home(request):
    template = loader.get_template('t_home.html')
    return HttpResponse(template.render(request=request))

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













