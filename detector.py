import numpy as np
import cv2
try:
    import dlib
except ImportError:
    print("Please install dlib")
    exit()

# 検出に必要なファイル
face_detector = dlib.simple_object_detector("detector_face.svm")
eye_detector = dlib.simple_object_detector("detector_eye.svm")

def face_2d(temp_file, userid, filename):
    # 最終検出結果
    get = False
    # 顔の位置
    facex = []
    facey = []
    facew = []
    faceh = []
    # 画像をメモリー上にデコード
    image = cv2.imdecode(np.asarray(bytearray(temp_file), dtype=np.uint8), 1)
    # 画像から顔を検出
    try:
        faces = face_detector(image)
    except:
        faces = 0
        print("Image type unsupported")
    # 二次元の顔が検出できた場合
    if len(faces) > 0:
        # 顔だけ切り出して目の検索
        for i, area in enumerate(faces):
            # 最小サイズの指定
            if area.bottom()-area.top() < image.shape[0]*0.075 or area.right()-area.left() < image.shape[1]*0.075:
                print("SMALL  : " + userid + "-" + filename + "_" + str(i))
                #print("DEBUG  : " + str(area.bottom()-area.top()) + "x" + str(area.right()-area.left()) + " - " + str(image.shape[0]) + "x" + str(image.shape[1]))
                continue
            face = image[area.top():area.bottom(), area.left():area.right()]
            # 出来た画像から目を検出
            eyes = eye_detector(face)
            if len(eyes) > 0:
                facex.append(area.left())
                facey.append(area.top())
                facew.append(area.right()-area.left())
                faceh.append(area.bottom()-area.top())
                get = True
            else:
                print("NOEYE  : " + userid + "-" + filename + "_" + str(i))
    
    if get:
        return (dhash_calc(image), facex, facey, facew, faceh)
    else:
        print("skiped : " + userid + "-" + filename)
        return (None, facex, facey, facew, faceh)


def dhash_calc(image, hash_size = 7):
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