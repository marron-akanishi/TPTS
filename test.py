import os
import sys
import dlib
import cv2

detector = dlib.simple_object_detector("detector.svm")
file_dir = "./face/"
eye_dir = "./eye_face_test/"
color_dir = ""
# 目検出枠の色
color = (255, 0, 0)
# 変数
skip = 0
check = 0

for temp in os.listdir(file_dir):
    filename = file_dir + temp
    try:
        image = cv2.imread(filename)
        img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    except:
        break
    dets = detector(img)
    if len(dets) <= 0:
        print("skiped : " + temp)
        skip += 1
    else:
        for i,d in enumerate(dets):
            cv2.rectangle(image, (d.left(), d.top()), (d.right(), d.bottom()), color, 2)
            if i == 0:
                # 中心の割り出し
                width_center = (d.left()+d.right()) / 2
                height_center = (d.top()+d.bottom()) / 2
                # 色検出
                r = img[width_center,height_center,0]
                g = img[width_center,height_center,1]
                b = img[width_center,height_center,2]
                # どの色味が一番強いかを判定
                if r > g:
                    if r > b:
                        color_dir = "r/"
                    elif b > r:
                        color_dir = "b/"
                elif b > g:
                    color_dir = "b/"
                else:
                    color_dir = "g/"
        cv2.imwrite(eye_dir + color_dir + temp, image)
        print("checked : " + temp)
        check += 1
print("OK:%d,NG:%d" % (check,skip))