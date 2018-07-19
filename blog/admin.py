from django.contrib import admin
from .models import Post, Category, Tag
# Register your models here.
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_time', 'modified_time', 'category', 'author']

#PostAdmin 存在的意义在于在admin后台管理中，增加的Post在列表里只会显示模板里写的返回title
#在这写了 PostAdmin类,可在后台管理界面Post列表显示上述字段。
admin.site.register(Post, PostAdmin)
admin.site.register(Category)
admin.site.register(Tag)
