from django.urls import path
from . import views

app_name    = "share"
urlpatterns = [ 
    path('', views.index, name="index"),

    #TODO:引数ありのURL。例えば、127.0.0.1:8000/3/とアクセスすると、ビューにpk=3の引数が渡される。
    path("<int:pk>/", views.single, name="single"),
]

#ここに複数ページ(個別ページも実装)
