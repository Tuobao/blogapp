from django.contrib.auth.models import User

from rest_framework import serializers
from .models import Post, Category, Tag


class PostSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), source='category.name')
    tags = serializers.SlugRelatedField(slug_field='name', queryset=Tag.objects.all(), many=True,  allow_null=True)

    class Meta:
        model = Post
        fields = ('id', 'title', 'body', 'category', 'author', 'tags', 'views')



"""
# 最初的方法，继承Serializer，和django的Form类似

class PostSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(max_length=70)
    body = serializers.CharField()

    def create(self, validated_data):

        return Post.objects.create(**validated_data)

    def update(self, instance, validated_data):

        instance.title = validated_data.get('title', instance.title)
        instance.body = validated_data.get('body', instance.body)
        instance.save()
        return instance
"""


# User的序列
class UserSerializer(serializers.ModelSerializer):
    # 由于post对user是反向关系，也就是Post类里定义了User，所以这里的ModelSerializer默认不会包含post， 所以显示添加
    posts = serializers.PrimaryKeyRelatedField(many=True, queryset=Post.objects.all())

    class Meta:
        model = User
        fields = ('id', 'username', 'posts')
