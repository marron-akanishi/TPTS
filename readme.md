# Timeline Picture Tagging System  
Twitterのタイムラインに流れてきた画像のうち、二次元画像を判定して保存します。     
このリポジトリは参考程度に使用し、動作させる場合は[TPTS_Web](https://github.com/marron-akanishi/TPTS_web)を使用してください。  
特にTPTS_WebのPersonalブランチは単一ユーザーでの使用を目的に作られています。  

# TPTS_Webとの違い
基本的にTPTSの技術を多くの人に使ってもらうためにWeb版が開発されました。  
ですが、向こうはデータベースにURLを保存するだけですが、こちらは画像本体も保存します。  
画像自体が欲しい(特にデータセット目的)場合はこちらをおすすめします。

# 今後の予定

- 写真とイラストの判定  
- いわゆる18禁画像かどうかの判定 
- 髪の色の判定？？ 

つまり、写真・全年齢イラスト・18禁イラストかの3種類に分類をしようと考えています。  
これ以外の分類が思いつきません。(キャラの判定はデータ数が膨大すぎて難しい)

# これより下は非常に説明が曖昧です

## 必要なファイル  
TL_twitter.py -> スクリプト本体  
detector.py -> 顔検出用スクリプト  
oauth.py -> API認証用スクリプト(使用方法参照)  
detector_face.svm -> 顔検出用ファイル  
detector_eye.svm -> 目検出用ファイル  

## 使用方法(簡易版)  
開発者はWindows10での動作を確認しています。  
ですが、非常に導入が面倒なのでローカルで走らせる場合は、  
Linux上で[TPTS_Web](https://github.com/marron-akanishi/TPTS_web)のReadmeを参照にして環境を構築してください。  
環境が構築できたら、templete内にあるoauth_empty.pyにTwitterのAPI情報を入力し、oauth.pyという名前でTL_twitter.pyと同じ位置に置きます。  
TL_twitter.pyを開き、`# 自分のツイートは飛ばす`と書かれた行の下にある`marron_general`を自分のIDに変更して保存します。  
その後、Python3でTL_twitter.pyを実行します。  
実行が成功すると、収集できた画像が日付の付いたフォルダーに保存されていきます。  
また、日付フォルダー内のlist.dbに画像に関する情報が保存されていきます。  
このlist.dbは[TPTSViewer](https://github.com/marron-akanishi/TPTSViewer)で確認可能ですが、このツールはWindowsでしか動作しません。  

## メモ  
### oldフォルダー内  
このフォルダーには昔OpenCVを使用して検出をしていた頃のデータがあります。  
現在のdlibを使用しているものより精度が低いので注意してください。  
また、中にあるlbpcascade_animeface.xmlは[lbpcascade_animeface](https://github.com/nagadomi/lbpcascade_animeface)からお借りしました。

### templeteフォルダー内  
- oauth_empty.py -> TwitterAPIの認証情報を生成するスクリプトのテンプレート
- TL_nocheck.py -> タイムラインに流れてきた画像を全て回収します。(oauth.py必須)

### TL_pawoo.py
このスクリプトはPawooのローカルタイムラインで画像を収集するためのものです。  
PawooのAPIキーが必要となります。キーを取ったあとは中の`key`に記載してください。  

# 参考にしたサイト
ほとんど忘れてしまっているので、覚えている範囲で記載しておきます。  
[PythonでTwitterを使う 〜Tweepyの紹介〜 - kivantium活動日記](https://goo.gl/aE1Yi6)  
[OpenCVによるアニメ顔検出ならlbpcascade_animeface.xml - デー](https://goo.gl/TLg4wK)  
[dlibのSimple_Object_detectorを用いたPythonでの物体検出器の学習 - Stimulator](https://goo.gl/qWn92M)  
[PythonのrequestsでmastodonのStreamingAPIを叩く - Qiita](https://goo.gl/xOzB5V)