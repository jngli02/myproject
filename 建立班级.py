import os
import django

# 设置 Django 的环境变量
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

# 加载 Django 应用
django.setup()

# 导入你的模型类
from web.models import Class

def create_class(year, grade):
    """创建班级"""
    class_instance, created = Class.objects.get_or_create(year=year, grade=grade)
    if created:
        print(f"成功创建班级：{class_instance}")
    else:
        print(f"班级已存在：{class_instance}")

def main():
    # 调用 create_class 函数创建班级
    create_class(2020, 1)
    # 创建其他班级...

if __name__ == "__main__":
    main()
