from django import template

register = template.Library()

#urlreplaceというテンプレートタグを作り、引数としてrequestオブジェクト、クエリストリングのキー、クエリストリングの値
#https://docs.djangoproject.com/ja/4.0/howto/custom-template-tags/
#https://docs.djangoproject.com/ja/4.0/howto/custom-template-tags/#writing-custom-template-tags


#この@register.simple_tag()はデコレータ。下記関数にテンプレートタグとしての機能を追加している。クラスの継承みたいなものと考えると良い
#https://qiita.com/mtb_beta/items/d257519b018b8cd0cc2e
#simple_tag() は文字列を返却するテンプレートタグ。HTMLそのものを返却したい場合は別のタグを使う。

@register.simple_tag()
def url_replace(request, name, value):

    #request.GETの内容をコピーする
    copied           = request.GET.copy()

    print(copied) #いまアクセスしているページのパラメータ。例えばsearch="test" {"search":"test","page":1}

    #指定されたキーに対応する値をvalueにする。(nameがpageでvalueが3であれば、page=3に書き換える)
    copied[name]    = value

    #クエリストリングで返却する。
    return copied.urlencode()

