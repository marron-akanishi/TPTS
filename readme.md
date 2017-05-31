# Timeline Picture Tagging System  
Twitterのタイムラインに流れてきた画像のうち、二次元画像を判定して保存します。  
また、ハッシュタグをタグとして画像に結びつけます。   
このリポジトリは参考程度に使用し、動作させる場合は[TPTS_Web](https://github.com/marron-akanishi/TPTS_web)を使用してください。  

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
Linux上で[TPTS_Web](https://github.com/marron-akanishi/TPTS_web)のReadmeを参照にしてライブラリーを入れてください。    
ライブラリーの導入が終わったら、templete内にあるoauth_empty.pyにTwitterのAPI情報を入力し、oauth.pyという名前でTL_twitter.pyと同じ位置に置きます。  
TL_dlib.pyを開き、`# 自分のツイートは飛ばす`と書かれた行の下にある`marron_general`を自分のIDに変更して保存します。  
これで実行が可能になります。  

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