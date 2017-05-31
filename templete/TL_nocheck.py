import urllib
import os
import datetime
import hashlib
import tweepy as tp
import cv2
import oauth  # oauthの認証キー

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

    def __init__(self, api):
        self.api = api
        # 保存先
        self.old_date = datetime.date.today()
        self.mkdir()

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
            if status.user.screen_name != "marron_general":
                for image in status_media['media']:
                    is_geted = False
                    if image['type'] != 'photo':
                        break
                    # URL, ファイル名を取得
                    media_url = image['media_url']
                    root, ext = os.path.splitext(media_url)
                    filename = str(self.fileno).zfill(5)
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
    auth = oauth.get_oauth()
    print('Start Streaming!')
    stream = tp.Stream(auth, StreamListener(tp.API(auth)), secure=True)
    stream.userstream()

if __name__ == '__main__':
    main()
