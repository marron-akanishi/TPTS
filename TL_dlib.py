import os
import time
import datetime
import hashlib
import urllib
import sqlite3
import tweepy as tp
import numpy as np
import cv2
import oauth  # oauthの認証キー
try:
    import dlib
    use_dlib = True
except ImportError:
    use_dlib = False

class StreamListener(tp.StreamListener):
    def __init__(self, api):
        """コンストラクタ"""
        self.api = api
        # 保存先
        self.old_date = datetime.date.today()
        self.mkdir()
        # 検出に必要なファイル
        self.cascade = cv2.CascadeClassifier("lbpcascade_animeface.xml")
        if use_dlib:
            self.eye_detector = dlib.simple_object_detector("detector.svm")

    def on_status(self, status):
        """UserStreamから飛んできたStatusを処理する"""
        # Tweetに画像がついているか
        is_media = False
        # 日付の確認
        now = datetime.date.today()
        if now != self.old_date:
            self.old_date = now
            self.dbfile.commit()
            self.dbfile.close()
            self.mkdir()
        # TweetがRTかどうか
        if hasattr(status, "retweeted_status"):
            status = status.retweeted_status
        # Tweetが引用ツイートかどうか
        if hasattr(status, "quoted_status"):
            status = status.quoted_status
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
            if status.user.screen_name != "marron_general" and status.user.screen_name != "marron_recbot":
                for image in status_media['media']:
                    if image['type'] != 'photo':
                        break
                    # URL, ファイル名
                    media_url = image['media_url']
                    root, ext = os.path.splitext(media_url)
                    filename = str(self.fileno).zfill(5)
                    # ダウンロード
                    try:
                        temp_file = urllib.request.urlopen(media_url + ":large").read()
                    except:
                        print("Download Error")
                        continue
                    # md5の取得
                    current_md5 = hashlib.md5(temp_file).hexdigest()
                    # すでに取得済みの画像は飛ばす
                    if current_md5 in self.file_md5:
                        print("geted  : " + status.user.screen_name +"-" + filename + ext)
                        continue
                    image = cv2.imdecode(np.asarray(bytearray(temp_file), dtype=np.uint8), 1)
                    faces = self.cascade.detectMultiScale(image,\
                                                        scaleFactor=1.11,\
                                                        minNeighbors=2,\
                                                        minSize=(128, 128))
                    # 二次元の顔が検出できない場合
                    if len(faces) <= 0:
                        print("skiped : " + status.user.screen_name + "-" + filename + ext)
                    else:
                        eye = False #目の状態
                        if use_dlib:
                            # 顔だけ切り出して目の検索
                            for i, area in enumerate(faces):
                                x, y, width, height = tuple(area[0:4])
                                face = image[y:y+height, x:x+width]
                                # 出来た画像から目を検出
                                eyes = self.eye_detector(face)
                                if len(eyes) > 0:
                                    eye = True
                        # 目があったなら画像本体を保存
                        if use_dlib == False or eye:
                            # 保存
                            out = open(self.base_path + filename + ext, "wb")
                            out.write(temp_file)
                            out.close()
                            # 取得済みとしてMD5を保存
                            self.file_md5.append(current_md5)
                            # ハッシュタグがあれば保存する
                            text_split = status.text.split(" ")
                            tags = []
                            for tag_text in text_split:
                                if tag_text.startswith('#'):
                                    tags.append(tag_text.lstrip("#").split("\n")[0].split("　")[0])
                            # データベースに保存
                            url = "https://twitter.com/" + status.user.screen_name + "/status/" + status.id_str
                            self.dbfile.execute("insert into list values('" + filename + ext + "','" + \
                                status.user.screen_name + "','" + url + "'," + str(status.favorite_count) + "," + \
                                str(status.retweet_count) + ",'" + str(tags).replace("'","") + "','" + str(datetime.datetime.now()) +"')")
                            self.dbfile.commit()
                            print("saved  : " + status.user.screen_name + "-" + filename + ext)
                            if tags != []:
                                print("  tags : " + str(tags))
                            self.fileno += 1
                        else:
                            print("noEye  : " + status.user.screen_name + "-" + filename + ext)
        
    def mkdir(self):
        """保存用のフォルダーを生成し、必要な変数を初期化する"""
        self.base_path = "./" + self.old_date.isoformat() + "/"
        if os.path.exists(self.base_path) == False:
            os.mkdir(self.base_path)
        self.fileno = 0
        self.file_md5 = []
        self.dbfile = sqlite3.connect(self.base_path + "list.db")
        try:
            self.dbfile.execute("create table list (filename, username, url, fav, retweet, tags, time)")
        except:
            None


def main():
    """メイン関数"""
    auth = oauth.get_oauth()
    stream = tp.Stream(auth, StreamListener(tp.API(auth)), secure=True)
    print('Start Streaming!')
    while True:
        try:
            stream.userstream()
        except KeyboardInterrupt:
            exit()
        except:
            print('UserStream Error')
            time.sleep(60)

if __name__ == '__main__':
    main()
