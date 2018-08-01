from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.html import strip_tags
import markdown

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Post(models.Model):
    #标题
    title = models.CharField(max_length=70)
    #正文  储存比较短的字符串可以用Char 这里储存大量文字，使用Text
    body= models.TextField()
    #创建时间 和 更新时间
    created_time = models.DateTimeField()
    modified_time = models.DateTimeField()

    #摘要 允许为空  char要求必须存入数据 加入 blank=True允许为空值
    excerpt = models.CharField(max_length=200, blank=True)

    #分类和标签的关联
    #ForeignKey 外键即一对多
    #ManyToManyField 多对多
    category = models.ForeignKey(Category)
    tags = models.ManyToManyField(Tag, blank=True)

    # 文章作者 User 从django.contrib.auth.models包里导入
    # django.contrib.auth 是 Django 内置的应用，专门用于处理网站用户的注册、登录等流程，User 是 Django 为我们已经写好的用户模型。
    # 一篇文章有一个作者，一个作者可有多篇文章，为一对多关系，外键
    author = models.ForeignKey(User, related_name='author')

    #阅读量
    views = models.PositiveIntegerField(default=0, editable=False)

    def __str__(self):
        return self.title

    # 自定义get_absolute_url方法 reverse需要从django.urls导入
    def get_absolute_url(self):
        return reverse('blog:detail', kwargs={'pk': self.pk})

    def increase_views(self):
        self.views += 1
        self.save(update_fields=['views'])

    def save(self, *args, **kwargs):
        # 如果没有填写摘要，则自动生成摘要
        if not self.excerpt:
            md = markdown.Markdown(extensions=[
                'markdown.extensions.extra',
                'markdown.extensions.codehilite',
            ])

            self.excerpt = strip_tags(md.convert(self.body))[:54]
        super(Post, self).save(*args, **kwargs)

    class Meta:
        ordering = ['-created_time']


