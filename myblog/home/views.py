from django.http import HttpResponseNotFound,HttpResponse
from django.shortcuts import render
from django.views import View
from home.models import ArticleCategory,Article
from django.core.paginator import Paginator,EmptyPage
# Create your views here.
class IndexView(View):
    def get(self, request):
        #1.获取所有分类信息
        categories = ArticleCategory.objects.all()
        #2.接收用户点击的分类id，若未传递分类id则默认值给1
        cat_id = request.GET.get('cat_id', 1)
        #3.根据分类id进行分类的査询
        try:
            category = ArticleCategory.objects.get(id=cat_id)
        except ArticleCategory.DoesNotExist:
            return HttpResponseNotFound('没有此分类')

        #4.获取分页参数
        # 当前页码 默认展示第一页
        page_num = request.GET.get('page_num' , 1)
        # 每页展示记录数 默认每页展示10条记录
        page_size = request.GET.get('page_size' , 10)
        #5.根据分类信息査询文章数据
        articles = Article.objects.filter(category=category)

        #6.创建分页器
        paginator = Paginator(articles,per_page=page_size)
        #7.进行分页处理
        try:
            #文章分页数据
            page_article = paginator.page(page_num)
            #总页数
            total_page = paginator.num_pages
        except EmptyPage:
            return HttpResponseNotFound('未查到匹配文章记录')

        #8.组织数据传递给模板
        context = {
            'categories':categories,
            'category':category,
            'articles':page_article,
            'total_page':total_page,
            'page_num':page_num,
            'page_size':page_size
        }
        return render(request , 'index.html' , context=context)
