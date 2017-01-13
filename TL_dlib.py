import os
import datetime
import time
import hashlib
import tweepy as tp
import urllib
import cv2
import dlib
import oauth  # oauthの認証キー

class StreamListener(tp.StreamListener):
    def mkdir(self):
        """保存用のフォルダーを生成し、必要な変数を初期化する"""
        self.base_path = "./" + self.old_date.isoformat() + "/"
        if os.path.exists(self.base_path) == False:
            os.mkdir(self.base_path)
        self.fileno = 0
        self.file_md5 = []

    def __init__(self, api=None):
        """コンストラクタ"""
        self.api = api or tp.API()
        # 保存先
        self.old_date = datetime.date.today()
        self.mkdir()
        # 検出に必要なファイル
        self.cascade = cv2.CascadeClassifier("lbpcascade_animeface.xml")
        self.eye_detector = dlib.simple_object_detector("detector.svm")

    def on_status(self, status):
        """UserStreamから飛んできたStatusを処理する"""
        # Tweetに画像がついているか
        is_media = False
        # Tweetを保存するか
        is_get = True
        # 日付の確認
        now = datetime.date.today()
        if now != self.old_date:
            self.old_date = now
            self.mkdir()
        # 複数枚の画像ツイートのとき
        if hasattr(status, "extended_entities"):
            if 'media' in status.extended_entities:
                status_media = status.extended_entities
                is_media = True
        # 一枚の画像ツイートのとき
        elif hasattr(status, "entities"):
            if 'media' in status.entities:
                status_media = status.entities
                is_media = True

        # 画像がついていたとき
        if is_media:
            # 自分のツイートは飛ばす
            if status.user.screen_name == "marron_general":
                is_get = False
            # 取得開始
            if is_get:
                for image in status_media['media']:
                    is_geted = False
                    if image['type'] != 'photo':
                        break
                    # URL, ファイル名を取得
                    media_url = image['media_url']
                    root, ext = os.path.splitext(media_url)
                    filename = str(self.fileno).zfill(10)
                    # スクレイピングと顔検出
                    try:
                        urllib.request.urlretrieve(media_url, filename + ext)
                        # md5の取得
                        temp = open(filename + ext, "rb")
                        current_md5 = hashlib.md5(temp.read()).hexdigest()
                        temp.close()
                        # すでに取得済みの画像は飛ばす
                        for geted_md5 in self.file_md5:
                            if current_md5 == geted_md5:
                                is_geted = True
                                break
                        if is_geted:
                            print("geted : " + status.user.screen_name +"-" + filename + ext)
                            os.remove(filename + ext)
                            continue
                        image = cv2.imread(filename + ext)
                        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                        faces = self.cascade.detectMultiScale(gray,\
                                                            scaleFactor=1.11,\
                                                            minNeighbors=2,\
                                                            minSize=(128, 128))
                        # 二次元の顔が検出できない場合
                        if len(faces) <= 0:
                            print("skiped : " + status.user.screen_name +"-" + filename + ext)
                            os.remove(filename + ext)
                        else:
                            eye = False #目の状態
                            # 顔だけ切り出して保存
                            for i, area in enumerate(faces):
                                x, y, width, height = tuple(area[0:4])
                                face = image[y:y+height, x:x+width]
                                rgb = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
                                # 出来た画像から目を検出
                                eyes = self.eye_detector(rgb)
                                if len(eyes) > 0:
                                    eye = True
                            # 目があったなら画像本体を保存
                            if eye:
                                # ユーザーフォルダーの確認と作成
                                user_dir = status.user.screen_name + "/"
                                if os.path.exists(self.base_path + user_dir) == False:
                                    os.mkdir(self.base_path + user_dir)
                                cv2.imwrite(self.base_path + user_dir + filename + ext, image)
                                # 取得済みとしてMD5を保存
                                self.file_md5.append(current_md5)
                                print("saved : " + status.user.screen_name + "-" + filename + ext)
                            else:
                                print("noEye : " + status.user.screen_name + "-" + filename + ext)
                            os.remove(filename + ext)
                            self.fileno += 1
                    except IOError:
                        print("Error")


def main():
    """メイン関数"""
    auth = oauth.get_oauth()
    tp.API(auth)
    print('Start Streaming!')
    stream = tp.Stream(auth, StreamListener(), secure=True)
    while True:
        try:
            stream.userstream()
        except:
            print('UserStream Error')
            time.sleep(60)

if __name__ == '__main__':
    main()
