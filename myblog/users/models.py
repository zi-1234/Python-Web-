from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.
class User(AbstractUser):
    #手机号字段 max_length最大长度 unique唯一字段 blank设置不允许为空
    mobile = models.CharField(max_length=11,unique=True,blank=False)

    #头像字段 upload_to头像上传的地址 blank设置允许为空
    avatar = models.ImageField(upload_to='avatar/%Y%m%d/',blank=True)

    #个人简介字段 max_length最大长度 blank设置允许为空
    desc = models.TextField(max_length=200,blank=True)

    # 修改认证的字段
    USERNAME_FIELD = 'mobile'

    # 创建超级管理员的需要必须输入的字段
    REQUIRED_FIELDS = ['username', 'email']

    #内部类 class Meta 用于给 model 定义元数据
    class Meta:
        db_table='tb_users'          #修改默认的表名
        verbose_name = '用户信息管理'   # Admin后台显示
        verbose_name_plural = verbose_name  # Admin后台显示

    def __str__(self):
        return self.mobile