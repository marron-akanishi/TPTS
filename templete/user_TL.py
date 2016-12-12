import os
import hashlib
import urllib
import tweepy as tp
import cv2
import oauth

# サンプル顔認識特徴量ファイル
cascade_path = "./lbpcascade_animeface.xml"
# 顔検出枠の色
cascade = cv2.CascadeClassifier(cascade_path)
# いろいろ足りないもの
fileno = 0
file_md5 = []

def get_media_tweet(status):
    # Tweetに画像がついているか
    is_media = False
    raw_dir = "raw/"
    face_dir = "face/"
    color = (255, 255, 255)
    global cascade
    global fileno
    global file_md5
    
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
        is_geted = False
        for image in status_media['media']:
            if image['type'] != 'photo':
                break
            # URL, ファイル名を取得
            media_url = image['media_url']
            root, ext = os.path.splitext(media_url)
            filename = str(fileno).zfill(10)
            # スクレイピングと顔検出
            try:
                urllib.request.urlretrieve(media_url, filename + ext)
                # md5の取得
                f = open(filename + ext,"rb")
                current_md5 = hashlib.md5(f.read()).hexdigest()
                f.close()
                # すでに取得済みの画像は飛ばす
                for geted_md5 in file_md5:
                    if current_md5 == geted_md5:
                        is_geted = True
                        break
                if is_geted:
                    print("geted : " + str(status.id) + "-" + filename + ext)
                    os.remove(filename + ext)
                    continue
                image = cv2.imread(filename + ext)
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                facerect = cascade.detectMultiScale(gray,\
                                                        scaleFactor=1.11,\
                                                        minNeighbors=2,\
                                                        minSize=(128, 128))
                # 二次元の顔が検出できない場合
                if len(facerect) <= 0:
                    print("skiped : " + str(status.id) +"-" + filename + ext)
                    os.remove(filename + ext)
                else:
                    # 顔だけ切り出して保存
                    for i, rect in enumerate(facerect):
                        x, y, width, height = tuple(rect[0:4])
                        dst = image[y:y+height, x:x+width]
                        new_image_path = face_dir + filename + '_' + str(i) + ext
                        cv2.imwrite(new_image_path, dst)
                    cv2.imwrite(raw_dir + filename + ext, image)
                    # 取得済みとしてMD5を保存
                    file_md5.append(current_md5)
                    print("saved : " + str(status.id) + "-" + filename + ext)
                    os.remove(filename + ext)
                    fileno += 1
            except IOError:
                print("Error")

def get_oauth():
    """oauth.pyのoauth_keysから各種キーを取得し、OAUTH認証を行う"""
    consumer_key, consumer_secret = \
        oauth.oauth_keys['CONSUMMER_KEY'], oauth.oauth_keys['CONSUMMER_SECRET']
    access_key, access_secret = \
        oauth.oauth_keys['ACCESS_TOKEN_KEY'], oauth.oauth_keys['ACCESS_TOKEN_SECRET']
    auth = tp.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    return auth               

api = tp.API(get_oauth())
end_id = 0
for i in range(1,50):
    try:
        temp = api.user_timeline(screen_name="",page=i)
        for status in temp:
            get_media_tweet(status)
            end_id = str(status.id)
    except:
        print("API Error")