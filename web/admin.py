from django.contrib import admin
from .models import News

class NewsAdmin(admin.ModelAdmin):
    list_display = ['title', 'summary', 'add_time']  # 在列表页面中显示的字段
    search_fields = ['title', 'summary']  # 可以搜索的字段

admin.site.register(News, NewsAdmin)  # 注册模型和ModelAdmin子类
