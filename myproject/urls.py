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
    path('admin/', admin.site.urls),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_reset_done'),
    path('register/', views.register, name='register'),
    path('p_home/',views.p_home, name='p_home'),
    #path('t_home/',views.t_home, name='t_home'),
    path('a_home/',views.a_home, name='a_home'),
    
    #管理员界面
    path('admin_login/',views.admin_login_view,name='admin_login'),
    path('add_student/',views.add_student,name='add_student'),
    path('upload',views.add_batch,name='add_batch'),
    path('student_info', views.student_info, name='student_info'),
    path('delete_student', views.delete_student, name='delete_student'),
    path('update_student/<int:student_id>/', views.update_student, name='update_student'),
    
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
    


    #教师界面
   path('t_home', views.t_home, name='t_home'),
   path('t_student_info', views.t_student_info, name='t_student_info'),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
