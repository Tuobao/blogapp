from django.conf.urls import url

from rest_framework.urlpatterns import format_suffix_patterns
from . import views

app_name = 'blog'
urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^post/(?P<pk>[0-9]+)/$', views.PostDetailView.as_view(), name='detail'),
    url(r'^archives/(?P<year>[0-9]{4})/(?P<month>[0-9]{1,2})/$', views.ArchivesView.as_view(), name='archives'),
    url(r'^category/(?P<pk>[0-9])+/$', views.CategoryView.as_view(), name='category'),
    url(r'^tag/(?P<pk>[0-9]+)/$', views.TagView.as_view(), name='tag'),

    url(r'^post_api/$', views.PostListGen.as_view()),
    url(r'^post_api/(?P<pk>[0-9]+)$', views.PostDetailGen.as_view()),
    url(r'^user_api/$', views.UserList.as_view()),
    url(r'^user_api/(?P<pk>[0-9]+)$', views.UserDetail.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)



'''
前端模板上{% url 'blog:name' %}  -->  urls.py里相同的name  -->
对应的视图函数或者类  -->  返回到前端，用{{ 属性 }}来渲染
'''