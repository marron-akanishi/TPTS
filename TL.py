import urllib
import os
import datetime
import hashlib
import tweepy as tp
import cv2
import oauth  # oauthの認証キー

def get_oauth():
    """oauth.pyのoauth_keysから各種キーを取得し、OAUTH認証を行う"""
    consumer_key, consumer_secret = \
        oauth.oauth_keys['CONSUMMER_KEY'], oauth.oauth_keys['CONSUMMER_SECRET']
    access_key, access_secret = \
        oauth.oauth_keys['ACCESS_TOKEN_KEY'], oauth.oauth_keys['ACCESS_TOKEN_SECRET']
    auth = tp.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    return auth

class StreamListener(tp.StreamListener):
    # フォルダー作成用
    def mkdir(self):
        self.base_path = "./" + self.old_date.isoformat() + "/"
        self.raw_dir = self.base_path + "raw/"
        self.face_dir = self.base_path + "face/"
        if os.path.exists(self.base_path) == False:
            os.mkdir(self.base_path)
        if os.path.exists(self.raw_dir) == False:
            os.mkdir(self.raw_dir)
        if os.path.exists(self.face_dir) == False:
            os.mkdir(self.face_dir)
        self.fileno = 0
        self.file_md5 = []

    def __init__(self, api=None):
        self.api = api or tp.API()
        # 保存先
        self.old_date = datetime.date.today()
        self.mkdir()
        # サンプル顔認識特徴量ファイル
        cascade_path = "./lbpcascade_animeface.xml"
        # 顔検出枠の色
        self.color = (255, 255, 255)
        self.cascade = cv2.CascadeClassifier(cascade_path)

    def on_status(self, status):
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
                        f = open(filename + ext,"rb")
                        current_md5 = hashlib.md5(f.read()).hexdigest()
                        f.close()
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
                        facerect = self.cascade.detectMultiScale(gray,\
                                                                scaleFactor=1.11,\
                                                                minNeighbors=2,\
                                                                minSize=(128, 128))
                        # 二次元の顔が検出できない場合
                        if len(facerect) <= 0:
                            print("skiped : " + status.user.screen_name +"-" + filename + ext)
                            os.remove(filename + ext)
                        else:
                            # 顔だけ切り出して保存
                            for i, rect in enumerate(facerect):
                                x, y, width, height = tuple(rect[0:4])
                                dst = image[y:y+height, x:x+width]
                                new_image_path = self.face_dir + filename + '_' + str(i) + ext
                                cv2.imwrite(new_image_path, dst)
                            # 画像本体を保存
                            cv2.imwrite(self.raw_dir + filename + ext, image)
                            # 取得済みとしてMD5を保存
                            self.file_md5.append(current_md5)
                            print("saved : " + status.user.screen_name + "-" + filename + ext)
                            os.remove(filename + ext)
                            self.fileno += 1
                    except IOError:
                        print("Error")


def main():
    auth = get_oauth()
    tp.API(auth)
    print('Start Streaming!')
    stream = tp.Stream(auth, StreamListener(), secure=True)
    stream.userstream()

if __name__ == '__main__':
    main()
