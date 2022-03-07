from django.db import models
from django.utils import timezone


#TODO:Djangoの中にあるユーザーモデルを使用して1対多のリレーションを組む
# https://noauto-nolife.com/post/django-foreignkey-user/
from django.contrib.auth.models import User

#TODO:カスタムユーザーモデルの1対多を組む
#https://noauto-nolife.com/post/django-custom-user-model-foreignkey/
from django.conf import settings 

#下記を使用して1から5までの値を入れる。
#https://noauto-nolife.com/post/django-template-integer-for-loop/
from django.core.validators import MinValueValidator,MaxValueValidator

from django.db.models import Avg

class Document(models.Model):

    dt          = models.DateTimeField(verbose_name="投稿日", default=timezone.now)
    name        = models.CharField(verbose_name="ファイル名", max_length=500)
    content     = models.FileField(verbose_name="ファイル", upload_to="share/document/content")
    mime        = models.TextField(verbose_name="MIMEタイプ",null=True,blank=True)

    #user       = models.ForeignKey(User,verbose_name="投稿者",on_delete=models.SET_NULL,null=True,blank=True)

    #TODO:カスタムユーザーモデルを指定する。
    user        = models.ForeignKey(settings.AUTH_USER_MODEL,verbose_name="投稿者",on_delete=models.SET_NULL,null=True,blank=True)

    #ここでファイルのサムネイルを登録する。
    thumbnail   = models.ImageField(verbose_name="ファイルのサムネイル", upload_to="share/document/thumbnail",null=True,blank=True)
    

    #モデルの追加メソッドで簡単な計算処理を書いてreturnすれば、テンプレートで呼び出せる
    def avg_star(self):
        review  = Review.objects.filter(document=self.id).aggregate(Avg("star"))
        return review["star__avg"]

    def __str__(self):
        return self.name

#このモデルをマイグレーションする時、migrationsを全て消し、ユーザーモデルからマイグレーションをする。
#近年のバージョン(3.x以降)ではカスタムユーザーモデルのマイグレーションの順序を考慮しなくてもDjangoが自動的にユーザーモデル→一般アプリの順番でマイグレーションしてくれる模様。
#だが、念の為に、DBとmigrationsディレクトリを全て削除し、下記の順序でマイグレーションをする。

# python3 manage.py makemigrations users
# python3 manage.py makemigrations share
# python3 manage.py migrate

class Review(models.Model):

    dt          = models.DateTimeField(verbose_name="投稿日", default=timezone.now)
    document    = models.ForeignKey(Document, verbose_name="対象ファイル",on_delete=models.CASCADE)

    user        = models.ForeignKey(settings.AUTH_USER_MODEL,verbose_name="投稿者",on_delete=models.SET_NULL,null=True,blank=True)
    comment     = models.CharField(verbose_name="コメント",max_length=500)

    #ユーザーからのレビューを受け付ける
    star       = models.IntegerField(verbose_name="星",validators=[MinValueValidator(1),MaxValueValidator(5)])



