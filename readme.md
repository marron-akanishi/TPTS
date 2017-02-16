# Timeline Picture Tagging System  
Twitterのタイムラインに流れてきた画像のうち、二次元画像のみを取得し、自動的にタグ付けします(多分)。

## 必要なファイル  
TL_dlib.py -> スクリプト本体  
oauth.py -> Twitter認証用スクリプト(templete内にあります)  
lbpcascade_animeface.xml -> 顔検出用ファイル([lbpcascade_animeface](https://github.com/nagadomi/lbpcascade_animeface)からお借りしました)  
detector.svm -> 目検出用ファイル  

## 使用方法(簡易版)  
一応、開発者はWindows10での動作を確認しています。  
まず、最新版のPython3をインストールします。  
その後、pipを使ってtweepyとopencv-pythonをインストールします。  
次に、templete内にあるoauth_empty.pyにTwitterのAPI情報を入力し、oauth.pyという名前でTL_dlib.pyと同じ位置に置きます。  
TL_dlib.pyを開き、`# 自分のツイートは飛ばす`と書かれた行の下にある`marron_general`を自分のIDに変更して保存します。  
これで実行が可能になります。  
また、dlibを導入することによって目を検出し精度を上げることが出来ます。

### メモ  
local.py -> ローカルファイルから顔を検出(フォルダー等はスクリプト参照)  
movie_face.py -> 動画ファイルから顔を検出(フォルダー等はスクリプト参照)  
TL.py, test.py -> 残骸  
templete/md5.py -> 重複検索  
templete/user_TL.py -> 特定ユーザーの画像をダウンロード  
bot.py -> リプで指定したファイルを返信する(ほとんど個人向け)
