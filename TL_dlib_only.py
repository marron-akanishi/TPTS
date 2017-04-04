# printで表示する状態情報は半角6文字以内にすること

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
    print("Please install dlib")
    exit()

class StreamListener(tp.StreamListener):
    def __init__(self, api):
        """コンストラクタ"""
        self.api = api
        # 保存先
        self.old_date = datetime.date.today()
        self.mkdir()
        # 検出に必要なファイル
        self.face_detector = dlib.simple_object_detector("detector_face.svm")
        self.eye_detector = dlib.simple_object_detector("detector_eye.svm")

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
                    faces = self.face_detector(image)
                    # 二次元の顔が検出できない場合
                    if len(faces) <= 0:
                        print("skiped : " + status.user.screen_name + "-" + filename + ext)
                    else:
                        eye = False #目の状態
                        facex = []
                        facey = []
                        facew = []
                        faceh = []
                        # 顔だけ切り出して目の検索
                        for i, area in enumerate(faces):
                            # 最小サイズの指定(100x100以下)
                            if area.bottom()-area.top() < 100 or area.right()-area.left() < 100:
                                print("SMALL  : " + status.user.screen_name + "-" + filename + ext + "_" + str(i))
                                continue
                            face = image[area.top():area.bottom(), area.left():area.right()]
                            # 出来た画像から目を検出
                            eyes = self.eye_detector(face)
                            if len(eyes) > 0:
                                facex.append(area.left())
                                facey.append(area.top())
                                facew.append(area.right()-area.left())
                                faceh.append(area.bottom()-area.top())
                                eye = True
                            else:
                                print("NOEYE  : " + status.user.screen_name + "-" + filename + ext + "_" + str(i))
                        # 目があったなら画像本体を保存
                        if eye:
                            # 保存
                            out = open(self.base_path + filename + ext, "wb")
                            out.write(temp_file)
                            out.close()
                            # 取得済みとしてMD5を保存
                            self.file_md5.append(current_md5)
                            # ハッシュタグがあれば保存する
                            tags = []
                            if hasattr(status, "entities"):
                                if "hashtags" in status.entities:
                                    for hashtag in status.entities['hashtags']:
                                        tags.append(hashtag['text'])
                            # データベースに保存
                            url = "https://twitter.com/" + status.user.screen_name + "/status/" + status.id_str
                            # 1行書きは汚い
                            '''
                            self.dbfile.execute("insert into list values('" + filename + ext + "','" + \
                                status.user.screen_name + "','" + url + "'," + str(status.favorite_count) + "," + \
                                str(status.retweet_count) + ",'" + str(tags).replace("'","") + "','" + str(datetime.datetime.now()) + \
                                "','" + str(facex) + "','" + str(facey) + "','" + str(facew) + "','" + str(faceh) +"')")
                            '''
                            # 1つずつに分けてみる
                            self.dbfile.execute("insert into list(filename) values('" + filename + ext + "')")
                            self.dbfile.execute("update list set username = '" + status.user.screen_name + "' where filename = '" + filename + ext + "'")
                            self.dbfile.execute("update list set url = '" + url + "' where filename = '" + filename + ext + "'")
                            self.dbfile.execute("update list set fav = '" + str(status.favorite_count) + "' where filename = '" + filename + ext + "'")
                            self.dbfile.execute("update list set retweet = '" + str(status.retweet_count) + "' where filename = '" + filename + ext + "'")
                            self.dbfile.execute("update list set tags = '" + str(tags).replace("'","") + "' where filename = '" + filename + ext + "'")
                            self.dbfile.execute("update list set time = '" + str(datetime.datetime.now()) + "' where filename = '" + filename + ext + "'")
                            self.dbfile.execute("update list set facex = '" + str(facex) + "' where filename = '" + filename + ext + "'")
                            self.dbfile.execute("update list set facey = '" + str(facey) + "' where filename = '" + filename + ext + "'")
                            self.dbfile.execute("update list set facew = '" + str(facew) + "' where filename = '" + filename + ext + "'")
                            self.dbfile.execute("update list set faceh = '" + str(faceh) + "' where filename = '" + filename + ext + "'")
                            self.dbfile.commit()
                            print("saved  : " + status.user.screen_name + "-" + filename + ext)
                            if tags != []:
                                print("  tags : " + str(tags))
                            self.fileno += 1
                        else:
                            print("skiped : " + status.user.screen_name + "-" + filename + ext)
        
    def mkdir(self):
        """保存用のフォルダーを生成し、必要な変数を初期化する"""
        self.base_path = "./" + self.old_date.isoformat() + "/"
        if os.path.exists(self.base_path) == False:
            os.mkdir(self.base_path)
        self.fileno = 0
        self.file_md5 = []
        self.dbfile = sqlite3.connect(self.base_path + "list.db")
        try:
            self.dbfile.execute("create table list (filename, username, url, fav, retweet, tags, time, facex, facey, facew, faceh)")
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
