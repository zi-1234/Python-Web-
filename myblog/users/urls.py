from django.urls import path
from users.views import RegisterView,ImageCodeView,SmsCodeView,LoginView,LogoutView,CenterView


# 定义子应用users的视图路由
urlpatterns = [
    # 第一个参数：路由 请求url地址
    # 第二个参数：视图函数名
    # 第三个参数：路由名，方便后续通过reverse来获取路由名

    # 处理注册请求
    path('register/', RegisterView.as_view(), name='register'),
    path('imagecode/', ImageCodeView.as_view(), name='imagecode'),
    # 处理生成短信验证码的请求
    path('smscode/', SmsCodeView.as_view(), name='smscode'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('center/', CenterView.as_view(), name='center'),

]