from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from .models import Post, Category, Tag
from comments.forms import CommentForm
from django.views.generic import ListView, DetailView
from django.utils.text import slugify
from markdown.extensions.toc import TocExtension
from django.db.models import Q
from django.http import Http404
from django.contrib.auth.models import User

from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status, mixins, generics, permissions
from rest_framework.views import APIView

import markdown

from .serializers import PostSerializer, UserSerializer
from .permissions import IsAuthorOrReadOnly


# Create your views here.

# index的类视图，用来代替index的视图函数， url中第二个参数指定视图函数，这里类视图.as_view()即可转换为函数
class IndexView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    paginate_by = 4

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 父类生成的字典中已有 paginator、page_obj、is_paginated 三个模板变量
        paginator = context.get('paginator')
        page = context.get('page_obj')
        is_paginated = context.get('is_paginated')

        # 调用方法获得新数据
        pagination_data = self.pagination_data(paginator, page, is_paginated)
        # 更新这些数据到context中，是一个字典
        context.update(pagination_data)

        return context

    # 新数据, 返回字典
    def pagination_data(self, paginator, page, is_paginated):
        if not is_paginated:
            return {}
        # 定义当前页左边的页码[最多两个]
        left = []
        # 定义当前页右边的页码[最多两个个]
        right = []
        # 定义左边的省略号
        left_has_more = False
        # 定义右边的省略号
        right_has_more = False
        # 始终显示第一页，但若左边的页码包含第一页则不显示
        first = False
        # 最后一页
        last = False
        # 当前页
        page_number = page.number
        # 总页数
        total_pages = paginator.num_pages
        # 整个分页后的页码列表 如分四页则是 [1, 2, 3, 4]
        page_range = paginator.page_range

        if page_number == 1:
            # 若请求的是第一页则不需要显示左边的
            # 这里是取的当前页码后两个页码，其他数字也可以改
            right = page_range[page_number:page_number + 2]

            # 如果最右边的页码比（最后一页的页码-1）小则显示右边省略号
            # 总页数也是最后一页的页码
            if right[-1] < total_pages - 1:
                right_has_more = True

            # 如果最右边的页码比（最后一页的页码）小则显示最后一页的页码
            if right[-1] < total_pages:
                last = True

        elif page_number == total_pages:
            # 若请求的是最后一页，则不显示右边的
            # 若(page_number - 3)为正数则就是该数，若为负数和0，就是0
            left = page_range[(page_number - 3) if (page_number - 3) > 0 else 0:page_number - 1]

            # 右边省略号
            if left[0] > 2:
                left_has_more = True
            # 显示第一页
            if left[0] > 1:
                first = True

        else:
            # 两边都要
            left = page_range[(page_number - 3) if (page_number - 3) > 0 else 0:page_number - 1]
            right = page_range[page_number:page_number + 2]

            # 省略号
            if left[0] > 2:
                left_has_more = True
            if right[-1] < total_pages - 1:
                right_has_more = True

            # 最前最后
            if left[0] > 1:
                first = True
            if right[-1] < total_pages:
                last = True

        data = {
            'left': left,
            'right': right,
            'left_has_more': left_has_more,
            'right_has_more': right_has_more,
            'first': first,
            'last': last,
        }
        return data


def index(request):
    # 用objects.all()方法取出所有文章
    # 用order_by()将取出的结果排序，根据方法里的参数来排
    post_list = Post.objects.all()
    return render(request, 'blog/index.html', context={
        'post_list': post_list,
    })


class PostDetailView(DetailView):
    # 这些属性的含义和 ListView 是一样的
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'

    def get(self, request, *args, **kwargs):
        # 该方法目的在于每文章访问一次，增加一次阅读量
        # get方法返回了一个httpresponse实例
        # 先调用父类方法， 才能使用self.object属性 这个属性是被访问的post实例
        response = super(PostDetailView, self).get(request, *args, **kwargs)

        self.object.increase_views()
        return response

    def get_object(self, queryset=None):
        post = super(PostDetailView, self).get_object(queryset=None)
        md = markdown.Markdown(extensions=[
            'markdown.extensions.extra',
            # 代码高亮
            'markdown.extensions.codehilite',
            # 自动生成目录
            TocExtension(slugify=slugify)
        ])
        post.body = md.convert(post.body)
        post.toc = md.toc
        return post

    def get_context_data(self, **kwargs):
        context = super(PostDetailView, self).get_context_data(**kwargs)
        form = CommentForm()
        comment_list = self.object.comment_set.all()
        context.update({
            'form': form,
            'comment_list': comment_list
        })
        return context


def detail(request, pk):
    # get_object_or_404()方法，传入的pk值若在Post存在时就返回object，若没有就返回404
    post = get_object_or_404(Post, pk=pk)

    # 阅读量加一
    post.increase_views()

    post.body = markdown.markdown(post.body,
                                  extensions=[
                                      'markdown.extensions.extra',
                                      'markdown.extensions.codehilite',
                                      'markdown.extensions.toc',
                                  ]
                                  )
    form = CommentForm()
    comment_list = post.comment_set.all()
    context = {'post': post,
               'form': form,
               'comment_list': comment_list
               }
    return render(request, 'blog/detail.html', context=context)


class ArchivesView(IndexView):

    def get_queryset(self):
        year = self.kwargs.get('year')
        month = self.kwargs.get('month')
        return super(ArchivesView, self).get_queryset().filter(created_time__year=year,
                                                               created_time__month=month
                                                               )


def archives(request, year, month):
    post_list = Post.objects.filter(created_time__year=year,
                                    created_time__month=month
                                    )
    return render(request, 'blog/index.html', context={'post_list': post_list})


class CategoryView(IndexView):

    def get_queryset(self):
        # 这里取得cate 是一个Category对象（用get_object_or_404（）方法取），Post关联了Category对象
        # 上面的archives是用的Post的year和month属性，直接取
        cate = get_object_or_404(Category, pk=self.kwargs.get('pk'))
        return super(CategoryView, self).get_queryset().filter(category=cate)


def category(request, pk):
    cate = get_object_or_404(Category, pk=pk)
    post_list = Post.objects.filter(category=cate)
    return render(request, 'blog/index.html', context={'post_list': post_list})


class TagView(IndexView):

    def get_queryset(self):
        tag = get_object_or_404(Tag, pk=self.kwargs.get('pk'))
        return super(TagView, self).get_queryset().filter(tags=tag)


# 搜索
'''
用户通过表单get方法提交的数据，Django保存在request.GET里，这类似一个python字典对象，
使用get方法，获取字典中键q对应的值，q是前端form的input框的name属性值，
属性__icontains是django内置查询表达式，contains是包含，前缀i表示不区分大小写。
查询表达式官方文档 Field lookups https://docs.djangoproject.com/en/1.10/ref/models/querysets/#field-lookups
'''


def search(request):
    q = request.GET.get('q')
    error_msg = ''

    if not q:
        error_msg = "请输入关键词"
        return render(request, 'blog/index.html', {'error_msg': error_msg})

    post_list = Post.objects.filter(Q(title__icontains=q) | Q(body__icontains=q))
    return render(request, 'blog/index.html', {'error_msg': error_msg,
                                               'post_list': post_list})


'''
rest api函数view  对文章的list、detail做接口
'''


@api_view(['GET', 'POST'])
def post_list(request, format=None):
    if request.method == 'GET':
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        print(serializer.data)
        return Response(serializer.data)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = PostSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def post_detail(request, pk, format=None):
    try:
        post = Post.objects.get(pk=pk)
    except Post.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = PostSerializer(post)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = PostSerializer(post, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


'''
rest api类的形式
'''


class PostList(APIView):

    def get(self, request, format=None):
        post = Post.objects.all()
        serializer = PostSerializer(post, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostDetail(APIView):

    def get_object(self, pk):
        try:
            return Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        post = self.get_object(pk=pk)
        serializer = PostSerializer(post)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        post = self.get_object(pk=pk)
        serializer = PostSerializer(post, request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        post = self.get_object(pk=pk)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


'''
使用rest mixins实现
'''
class PostListMix(mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  generics.GenericAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class PostDetailMix(mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin,
                    generics.GenericAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


'''
使用generic class-based views，极简
'''
class PostListGen(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class PostDetailGen(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsAuthorOrReadOnly,)


# User视图
class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
