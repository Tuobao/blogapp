from django.shortcuts import render, get_object_or_404, redirect
from blog.models import Post

from .models import Comment
from .forms import CommentForm

# Create your views here.
def post_comment(request, post_pk):
    #获取被评论的文章
    post = get_object_or_404(Post, pk=post_pk)
    #如果http是POST请求
    if request.method == 'POST':
        #用户提交的数据存在request.POST中
        #利用这种字典数据构造CommentForm 实例
        form = CommentForm(request.POST)

        #.is_valid()方法自动验证 form的数据是否符合格式
        if form.is_valid():
            #.save保存到数据库,commit=False作用是仅生成实例，不保存到数据库
            comment = form.save(commit=False)
            #评论关联到被评论的文章
            comment.post = post
            #保存到数据库
            comment.save()
            #rendirect方法会调用post的模型的get_absolute_url方法
            return redirect(post)
        else:
            #获取该文章下全部评论
            # post.***_set属性可以锁定到Post模型下的***模型，通过.all()方法获取post下的所有***
            comment_list = post.comment_set.all()
            context = {'post': post,
                       'form': form,
                       'comment_list': comment_list
                       }
            return  render(request, 'blog/detail.html', context=context)

    return redirect(post)