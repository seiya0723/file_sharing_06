from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.contrib import messages

#TODO:filterに使用するクエリビルダ
from django.db.models import Q

#TODO:ページネーションを実装させる
from django.core.paginator import Paginator


from .models import Document,Review
from .forms import DocumentForm,ReviewForm,YearMonthForm

import magic,datetime


ALLOWED_MIME = ["image/jpeg", "application/zip", "video/mp4", "application/pdf"]
PAGE_CONTENTS = 10

#CHECK:LoginRequiredMixinをViewと一緒に継承する(多重継承)することで、未認証のユーザーをログインページにリダイレクトすることができる。
class IndexView(LoginRequiredMixin,View):

    def get(self, request, *args, **kwargs):

        context                 = {}

        #TODO:ここでクエリを作る
        # (3)クエリを作る
        query = Q()

        #TODO:年月検索をする時、year,monthの3つを受け取る、この2つは数値じゃないと、月は1から12の値じゃないとダメ。日付は存在しない日付を指定してもOK
        #TODO:モデルを継承しないフォームクラスを作り、ここでバリデーションをする

        #?year=2022&month=12 の形式であればバリデーションOK(yearに数値が、monthに1~12の数値が入っている状態)
        form = YearMonthForm(request.GET)

        if form.is_valid():
            print("年月のバリデーションOK")
            #年月のパラメータの値に問題はないのでqueryに検索条件を追加加算する

            #この値は文字列型
            print(request.GET["year"])
            print(type(request.GET["year"]))

            #フォームクラスで指定した型に変換して辞書型にしてくれるメソッド。
            cleaned = form.clean()

            #これでフォームクラスで指定した数値型になる。
            print(cleaned["year"])
            print(type(cleaned["year"]))

            #年月検索を行う。日付型、日時型には__yearなどと年月日を指定しての検索ができる。Qの中で,で区切っても良い(その場合はAND検索になる。)
            query &= Q(dt__year=cleaned["year"], dt__month=cleaned["month"])



        #ページネーションと検索機能
        if "search" in request.GET:

            #(1)キーワードが空欄もしくはスペースのみの場合、ページにリダイレクト
            if request.GET["search"] == "" or request.GET["search"].isspace():
                return redirect("share:index")

            #(2)キーワードをリスト化させる(複数指定の場合に対応させるため)
            search      = request.GET["search"].replace("　"," ")
            search_list = search.split(" ")


            for word in search_list:

                #空欄の場合は次のループへ(OR検索する時、この部分がないと全部出てくる)
                if word == "":
                    continue

                #TIPS:AND検索の場合は&を、OR検索の場合は|を使用する。
                query &= Q(name__contains=word)

            #documents = Document.objects.filter(query).order_by("-dt")
            #documents    = Document.objects.filter(name__contains=request.GET["search"]).order_by("-dt")

        """
        else:
            documents = Document.objects.order_by("-dt")
        """

        documents = Document.objects.filter(query).order_by("-dt")

        #1ページに表示させる個数はviews.pyの冒頭に定義しておき、ここで呼び出す
        paginator   = Paginator(documents,PAGE_CONTENTS)

        if "page" in request.GET:
            context["documents"]    = paginator.get_page(request.GET["page"])
        else:
            context["documents"]    = paginator.get_page(1)


        #TODO:ここでDB内にある最古と最新のDocumentを呼び出す。その上で選択肢として表示させる年を作る
        newest  = Document.objects.order_by("-dt").first()
        oldest  = Document.objects.order_by("dt").first()

        if newest and oldest:
            new_year    = newest.dt.year
            old_year    = oldest.dt.year

            year_list   = []
            for i in range(new_year,old_year-1,-1):
                year_list.append(i)

            context["year_list"]    = year_list
        else:
            context["year_list"]    = [ datetime.datetime.now().year ]

        #内包表記
        context["month_list"]       = [ str(i) for i in range(1,13) ]


        return render(request,"share/index.html", context)

    def post(self, request, *args, **kwargs):

        #アップロードファイルが存在しない場合、リダイレクト。
        #想定外の処理をされた場合、return文を実行する。これをアーリーリターン(early return)。
        #メリット:ネストが深くなるのを防ぐ、処理速度が若干速くなる。

        if "content" not in request.FILES:
            messages.error(request, "ファイルがありません")
            return redirect("dojo:index")

        #mimeの取得、mimeをセットしたリクエストをバリデーションする。
        mime    = magic.from_buffer(request.FILES["content"].read(1024), mime=True)

        #TIPS:クライアントから受け取ったリクエストを直接書き換えすることはできない。そのためcopyメソッドでリクエストのコピーを作る。
        copied          = request.POST.copy()
        copied["mime"]  = mime

        #TODO:ユーザーIDをコピーしたリクエストに格納する。その上でバリデーション。
        copied["user"]  = request.user.id


        form = DocumentForm(copied, request.FILES)

        if not form.is_valid():
            messages.error(request, form.errors)
            print("バリデーションNG")
            return redirect("share:index")

        print("バリデーションOK")

        if mime not in ALLOWED_MIME:
            messages.error(request, "このファイルは許可されていません")
            print("このファイルは許可されていません")
            return redirect("share:index")


        #form.save()の返り値として、保存したデータのモデルオブジェクトが手に入る
        document    = form.save()
        print(document.id)
        print(document.content)

        messages.success(request, "保存に成功しました")


        if "application/pdf" == document.mime:
            #TODO:ここにPDFの場合サムネイルを生成してセットする。詳細は下記ブログ(コードが古いDjango2.x系のため、一部書き換えている)
            #https://noauto-nolife.com/post/django-aips-thumbnail-autocreate/

            from pdf2image import convert_from_path
            from django.conf import settings

            #サムネイルフィールドのアップロード先を取得
            path            = Document.thumbnail.field.upload_to
            thumbnail_path  = path + "/" + str(document.id) + ".png"
            full_path       = settings.MEDIA_ROOT + "/" + thumbnail_path

            #PDFを画像化させ、保存する。
            images = convert_from_path(settings.MEDIA_ROOT + "/" + str(document.content))
            images[0].save(full_path)

            #サムネイルのファイルパスをセットして保存し直す
            document.thumbnail = thumbnail_path
            document.save()

        return redirect("share:index")

index   = IndexView.as_view()



#投稿されたファイルの個別ページ
class SingleView(LoginRequiredMixin,View):

    #urls.pyに書かれたpkを引数として受け取り、ファイルを特定する。
    def get(self, request, pk, *args, **kwargs):

        context             = {}
        context["document"] = Document.objects.filter(id=pk).first()
        context["reviews"]  = Review.objects.filter(document=pk).order_by("-dt")

        return render(request,"share/single.html", context)

    def post(self, request, pk, *args, **kwargs):

        #TODO:ここで投稿されたファイルに対するレビューを受け付ける。
        copied  = request.POST.copy()
        copied["user"]      = request.user.id
        copied["document"]  = pk

        form = ReviewForm(copied)

        if form.is_valid():
            print("バリデーションOK")

        else:
            print("バリデーションNG")

        return redirect("share:single", pk)

single  = SingleView.as_view()

