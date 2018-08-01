from haystack import indexes

from .models import Post


class PostIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        return Post

    def index_queryset(self, using=None):
        return self.get_model().objects.all()

'''
django haystack的写法，对某个app下面的数据进行全文检索，就要在该app下创建search_indexes.py，
里面创建一个***Index类，***为app下模型，需继承SearchIndex和Indexable
每个索引下必有且仅有一个字段含有document=True，表示该字段为搜索内容
use_template-True 定义给哪些内容建立索引，搜索时，将搜索内容与所有索引匹配。
模板路径为 templates/search/indexes/youapp/\<model_name>_text.txt
'''
