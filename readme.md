# Timeline Picture Tagging System  
Twitterのタイムラインに流れてきた画像のうち、二次元画像のみを取得し、自動的にタグ付けします(多分)。

## 使用方法(簡易版)  
一応、開発者はWindows10とmacOS Sierraでの動作を確認しています。  
まず、最新版のPython3をインストールします。  
その後、pipを使ってtweepyとopencvをインストールします。  
次に、templete内にあるoauth.pyにTwitterのAPI情報を入力し、TL.pyと同じ位置に置きます。  
これでTL.pyは動かせます。  
TL_dlib.pyを使う場合はdlibが別途必要となります。特にWindowsの場合は非常にインストールが面倒です。