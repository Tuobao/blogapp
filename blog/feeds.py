from django.contrib.syndication.views import Feed

from .models import Post


class AllPostsRssFeed(Feed):
    # 显示在聚合阅读器上的标题
    title = "Tuobao个人博客"

    # 转跳的网址
    link = "/"
    # 显示的描述
    description = "Tuobao个人博客文章"

    # 显示的内容
    def items(self):
        return Post.objects.all()

    # 内容的标题
    def item_title(self, item):
        return '[%s] %s' % (item.category, item.title)

    # 内容的描述
    def item_description(self, item):
        return item.body