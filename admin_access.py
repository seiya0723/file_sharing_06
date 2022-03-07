import requests,sys

ID      = "asahina"
PASS    = "nobunaga0723"

URL     = "http://127.0.0.1:8000/"
LOGIN   = URL + "admin/login/"
TIMEOUT = 10
HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:63.0) Gecko/20100101 Firefox/63.0'}


#TIPS:Djangoに対してrequestsライブラリからPOST文を送信する方法
#参照元:https://www.it-swarm-ja.com/ja/python/python-requests%e3%81%a7csrftoken%e3%82%92%e6%b8%a1%e3%81%99/1070253083/

#(1) セッションを維持する(セッションメソッドからオブジェクトを作る)
client = requests.session()
client.get(LOGIN,timeout=TIMEOUT,headers=HEADERS)

#(2) CSRFトークンを手に入れ、投稿するデータを辞書型で生成
if 'csrftoken' in client.cookies:
    csrftoken = client.cookies['csrftoken']

login_data   = { "csrfmiddlewaretoken":csrftoken,
                 "username":ID,
                 "password":PASS
                 }

#(3) ログインする
r   = client.post(LOGIN,data=login_data,headers={"Referer":LOGIN})
print(r)

USER_ADD    = "http://127.0.0.1:8000/admin/auth/user/add/"
client.get(USER_ADD)

if 'csrftoken' in client.cookies:
    csrftoken = client.cookies['csrftoken']

args = sys.argv
if len(args) >= 3:
    user_data = { "csrfmiddlewaretoken":csrftoken,
                  "username":args[1],
                  "password1":args[2],
                  "password2":args[2],
    }
    r = client.post(USER_ADD,data=user_data,headers={"Referer":USER_ADD})
    print(r)
    print("ユーザー作成")