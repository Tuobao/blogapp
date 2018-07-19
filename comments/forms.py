from django import forms
from .models import Comment

#由于建立了数据库模型，这里的表单继承自forms.ModelForm 可对应到Comment
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['name','email','url','text']