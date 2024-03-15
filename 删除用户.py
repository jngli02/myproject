import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

import django
django.setup()

from django.contrib.auth.models import User

def delete_user(username):
    try:
        # 获取用户
        User.objects.filter(username=username).delete()
        print(f"用户 {username} 已被删除。")
    except User.DoesNotExist:
        print(f"用户 {username} 不存在。")

delete_user('张00316 ')
delete_user('黄00216')
delete_user('魏00116')
delete_user('张00315')
delete_user('黄00215')
delete_user('魏00115')




