from django.db import models
from django.utils import timezone

from users.models import User


# Create your models here.
class ArticleCategory(models.Model):
    #分类标题
    title = models.CharField(max_length=100 , blank=False)
    #创建时间
    created = models.DateTimeField(default=timezone.now)

    #内部类
    class Meta:
        db_table = 'tb_category'
        verbose_name = '文章分类信息管理'  # Admin后台显示
        verbose_name_plural = verbose_name  # Admin后台显示

    def __str__(self):
        return self.title

class Article(models.Model):
    #文章标题图
    avatar = models.ImageField(upload_to = 'article/%Y%m%d/',blank=True)
    #文章标签
    tags = models.CharField(max_length=20, blank=True)
    #文章标题
    title = models.CharField(max_length=100, blank=False)
    #概要
    sumary = models.CharField(max_length=200, blank=False)
    #正文内容
    content = models.TextField()
    #浏览量
    total_views = models.PositiveIntegerField(default=0)
    #评论数
    comments_count = models.PositiveIntegerField(default=0)
    #创建时间
    created = models.DateTimeField(default=timezone.now)
    #更新时间
    updated = models.DateTimeField(auto_now=True)

    #外键关联 User模型
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    #外键关林 ArticleCategory模型
    category = models.ForeignKey(ArticleCategory,null=True,blank=True,on_delete=models.CASCADE,related_name='article')

    #内部类
    class Meta:
        db_table = 'tb_article'
        #排序 指定模型返回的数据顺序 -表示倒序
        ordering=('-created',)
        verbose_name = '文章信息管理'  # Admin后台显示
        verbose_name_plural = verbose_name  # Admin后台显示

    def __str__(self):
        return self.title