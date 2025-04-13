from django.urls import path
from home.views import IndexView

# 定义子应用home的视图路由
urlpatterns = [
    # 第一个参数：路由 请求url地址
    # 第二个参数：视图函数名
    # 第三个参数：路由名，方便后续通过reverse来获取路由名

    # 处理首页
    path('', IndexView.as_view(), name='index'),
]