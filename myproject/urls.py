"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views 
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from django.urls import path
from web import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    
    #主页
    path('', views.home, name='home'), 
    path('admin/', admin.site.urls),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_reset_done'),
    path('register/', views.register, name='register'),
    path('p_home/',views.p_home, name='p_home'),
    #path('t_home/',views.t_home, name='t_home'),
    path('a_home/',views.a_home, name='a_home'),
    path('upload_holiday_schedule',views.upload_holiday_schedule, name='upload_holiday_schedule'),
    path('calendar',views.calendar, name='calendar'),
    path('add_classschedule',views.add_classschedule, name='add_classschedule'),
    path('p_classschedule',views.p_classschedule, name='p_classschedule'),

    
    #管理员界面
    path('admin_login/',views.admin_login_view,name='admin_login'),
    path('add_student/',views.add_student,name='add_student'),
    path('upload',views.add_batch,name='add_batch'),
    path('student_info', views.student_info, name='student_info'),
    path('delete_student', views.delete_student, name='delete_student'),
    path('update_student/<int:student_id>/', views.update_student, name='update_student'),
    path('create_class', views.create_class, name='create_class'),
    
    #path('add_news', views.add_news, name='add_news'),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('news_list', views.news_list, name='news_list'),
    path('news_detail/<int:news_id>/', views.news_detail, name='news_detail'),
    
    path('teacher_info', views.teacher_info, name='teacher_info'),

    path('delete_teacher', views.delete_teacher, name='delete_teacher'),
    path('update_teacher/<int:teacher_id>/', views.update_teacher, name='update_teacher'),
    path('update_photo/<int:teacher_id>/', views.update_photo, name='update_photo'),
    
    #家长界面
    path('p_student_info', views.p_student_info, name='p_student_info'),
    path('class_group/<int:class_id>/', views.class_group, name='class_group'),
    path('homework_info', views.homework_info, name='homework_info'),
    path('leave_request/', views.leave_request, name='leave_request'),


    #教师界面
    path('t_home', views.t_home, name='t_home'),
    path('t_student_info', views.t_student_info, name='t_student_info'),
    path('evaluation/<int:student_id>/', views.evaluation, name='evaluation'),
    path('evaluation_history/<int:student_id>/', views.evaluation_history, name='evaluation_history'),
    path('upload_grades', views.t_add_grades, name='t_add_grades'),
    path('s_exam_scores/<int:student_id>/', views.s_exam_scores, name='s_exam_scores'),
    path('class_exam_scores/<int:class_id>/', views.class_exam_scores, name='class_exam_scores'),
    path('add_homework/<str:teacher_id>/', views.add_homework, name='add_homework'),
    path('view_homework_submissions', views.view_homework_submissions, name='view_homework_submissions'),
    path('t_classschedule',views.t_classschedule, name='t_classschedule'),
    path('leave_approval',views.leave_approval, name='leave_approval'),

    path('user_detail/<int:user_id>/', views.user_detail, name='user_detail'),
    path('direct_chat/<int:user_id>/<int:class_id>/', views.direct_chat, name='direct_chat'),
    
    path('submit_homework/<int:homework_id>/<int:student_id>/', views.submit_homework, name='submit_homework'),
    path('view_submissions/<int:homework_id>/', views.view_submissions, name='view_submissions'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
