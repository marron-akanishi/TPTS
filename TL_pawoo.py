import os
import time
import datetime
import hashlib
import urllib
from urllib.parse import urljoin
import sqlite3
import json
import operator
import requests
import numpy as np
import cv2
try:
    import dlib
    use_dlib = True
except ImportError:
    print("Please install dlib")
    exit()

key = ''

class MstdnStream:
    """Mastodon Steam Class

    Usage::

        >>> from mstdn import MstdnStream, MstdnStreamListner
        >>> listener = MstdnStreamListner()
        >>> stream = MstdnStream('https://pawoo.net', 'your-access-token', listener)
        >>> stream.local()

    """
    def __init__(self, base_url, access_token, listener):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({'Authorization': 'Bearer ' + access_token})
        self.listener = listener

    def local(self):
        url = urljoin(self.base_url, '/api/v1/streaming/public/local')
        resp = self.session.get(url, stream=True)
        resp.raise_for_status()
        event = {}
        for line in resp.iter_lines():
            line = line.decode('utf-8')

            if not line:
                # End of content.
                method_name = "on_{event}".format(event=event['event'])
                f = operator.methodcaller(method_name, event['data'])
                f(self.listener)
                # refreash
                event = {}
                continue

            if line.startswith(':'):
                # TODO: Handle heatbeat
                #print('startwith ":" {line}'.format(line=line))
                None
            else:
                key, value = line.split(': ', 1)
                if key in event:
                    event[key] += value
                else:
                    event[key] = value


class MstdnStreamListner:
    def __init__(self):
        """コンストラクタ"""
        # 保存先
        self.old_date = datetime.date.today()
        self.mkdir()
        # 検出に必要なファイル
        self.face_detector = dlib.simple_object_detector("detector_face.svm")
        self.eye_detector = dlib.simple_object_detector("detector_eye.svm")

    def on_update(self, data):
        """UserStreamから飛んできたStatusを処理する"""
        status = json.loads(data)
        # 日付の確認
        now = datetime.date.today()
        if now != self.old_date:
            self.old_date = now
            self.dbfile.commit()
            self.dbfile.close()
            self.mkdir()
        for image in status['media_attachments']:
            if image['type'] != 'image':
                break
            # URL, ファイル名
            media_url = image['url']
            root, ext = os.path.splitext(media_url)
            filename = str(self.fileno).zfill(5)
            # ダウンロード
            try:
                temp_file = urllib.request.urlopen(media_url).read()
            except:
                print("Download Error")
                continue
            # md5の取得
            current_md5 = hashlib.md5(temp_file).hexdigest()
            # すでに取得済みの画像は飛ばす
            if current_md5 in self.file_md5:
                print("geted  : " + status['account']['acct'] +"-" + filename + ext)
                continue
            # 画像をメモリー上にデコード
            image = cv2.imdecode(np.asarray(bytearray(temp_file), dtype=np.uint8), 1)
            # 画像から顔を検出
            faces = self.face_detector(image)
            # 二次元の顔が検出できない場合
            if len(faces) <= 0:
                print("skiped : " + status['account']['acct'] + "-" + filename + ext)
            else:
                eye = False #目の状態
                facex = []
                facey = []
                facew = []
                faceh = []
                # CPU使用率低減のためにここでチェックをかける
                # 画像のハッシュを生成
                current_hash = dhash_calc(image)
                # すでに取得済みの画像は飛ばす
                overlaped = False
                for hash_key in self.file_hash:
                    check = int(hash_key,16) ^ int(current_hash,16)
                    count = bin(check).count('1')
                    if count < 7:
                        print("geted  : " + status['account']['acct'] +"-" + filename + ext)
                        overlaped = True
                        break
                if overlaped:
                    continue
                # 顔だけ切り出して目の検索
                for i, area in enumerate(faces):
                    # 最小サイズの指定
                    if area.bottom()-area.top() < image.shape[0]*0.075 or area.right()-area.left() < image.shape[1]*0.075:
                        print("SMALL  : " + status['account']['acct'] + "-" + filename + ext + "_" + str(i))
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
                        print("NOEYE  : " + status['account']['acct'] + "-" + filename + ext + "_" + str(i))
                # 目があったなら画像本体を保存
                if eye:
                    # 保存
                    out = open(self.base_path + filename + ext, "wb")
                    out.write(temp_file)
                    out.close()
                    # 取得済みとしてハッシュ値を保存
                    self.file_hash.append(current_hash)
                    self.file_md5.append(current_md5)
                    # ハッシュタグがあれば保存する
                    tags = []
                    if "tags" in status:
                        for hashtag in status['tags']:
                            tags.append(hashtag['name'])
                    # データベースに保存
                    self.dbfile.execute("insert into list(filename) values('" + filename + ext + "')")
                    self.dbfile.execute("update list set username = '" + status['account']['acct'] + "' where filename = '" + filename + ext + "'")
                    self.dbfile.execute("update list set url = '" + status['url'] + "' where filename = '" + filename + ext + "'")
                    self.dbfile.execute("update list set fav = " + str(status['favourites_count']) + " where filename = '" + filename + ext + "'")
                    self.dbfile.execute("update list set retweet = " + str(status['reblogs_count']) + " where filename = '" + filename + ext + "'")
                    self.dbfile.execute("update list set tags = '" + str(tags).replace("'","") + "' where filename = '" + filename + ext + "'")
                    self.dbfile.execute("update list set time = '" + str(datetime.datetime.now()) + "' where filename = '" + filename + ext + "'")
                    self.dbfile.execute("update list set facex = '" + str(facex) + "' where filename = '" + filename + ext + "'")
                    self.dbfile.execute("update list set facey = '" + str(facey) + "' where filename = '" + filename + ext + "'")
                    self.dbfile.execute("update list set facew = '" + str(facew) + "' where filename = '" + filename + ext + "'")
                    self.dbfile.execute("update list set faceh = '" + str(faceh) + "' where filename = '" + filename + ext + "'")
                    self.dbfile.commit()
                    print("saved  : " + status['account']['acct'] + "-" + filename + ext)
                    if tags != []:
                        print("  tags : " + str(tags))
                    self.fileno += 1
                else:
                    print("skiped : " + status['account']['acct'] + "-" + filename + ext)
        
    def mkdir(self):
        """保存用のフォルダーを生成し、必要な変数を初期化する"""
        self.base_path = "./" + self.old_date.isoformat() + "/"
        if os.path.exists(self.base_path) == False:
            os.mkdir(self.base_path)
        self.fileno = 0
        self.file_hash = []
        self.file_md5 = []
        self.dbfile = sqlite3.connect(self.base_path + "list.db")
        try:
            self.dbfile.execute("create table list (filename, username, url, fav, retweet, tags, time, facex, facey, facew, faceh)")
        except:
            None

    def on_notification(self, data):
        None

    def on_delete(self, data):
        None

def dhash_calc(image,hash_size = 7):
    check_image = cv2.resize(image,(hash_size,hash_size+1))
    check_image = cv2.cvtColor(check_image, cv2.COLOR_RGB2GRAY)
    # Compare adjacent pixels.
    difference = []
    for row in range(hash_size):
        for col in range(hash_size):
            pixel_left = check_image[col, row]
            pixel_right = check_image[col + 1, row]
            difference.append(pixel_left > pixel_right)
    # Convert the binary array to a hexadecimal string.
    decimal_value = 0
    hex_string = []
    for index, value in enumerate(difference):
        if value:
            decimal_value += 2**(index % 8)
        if (index % 8) == 7:
            hex_string.append(hex(decimal_value)[2:].rjust(2, '0'))
            decimal_value = 0
    return ''.join(hex_string)

def main():
    listener = MstdnStreamListner()
    stream = MstdnStream('https://pawoo.net', key, listener)
    print('Start Streaming!') 
    while True:
        try:
            stream.local()
        except KeyboardInterrupt:
            exit()

if __name__ == '__main__':
    main()
