import os
import sys
import dlib
import cv2

detector = dlib.simple_object_detector("detector.svm")
file_dir = "./face/"
eye_dir = "./eye_face_test/"
color_dir = ""
# 目検出枠の色
rect_color = (255, 0, 0)
# 変数
skip = 0
check = 0

for temp in os.listdir(file_dir):
    filename = file_dir + temp
    try:
        image = cv2.imread(filename)
        img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        color = cv2.cvtColor(image, cv2.COLOR_BGR2HSV_FULL)
    except:
        continue
    dets = detector(img)
    if len(dets) <= 0:
        print("skiped : " + temp)
        skip += 1
    else:
        for i,d in enumerate(dets):
            cv2.rectangle(image, (d.left(), d.top()), (d.right(), d.bottom()), rect_color, 2)
            if i == 0:
                # 中心の割り出し
                width_center = (d.left()+d.right()) / 2
                height_center = (d.top()+d.bottom()) / 2
                # 少し下にずらす
                #height_center += 5
                # 色検出
                h = color[width_center,height_center,0]
                s = color[width_center,height_center,1]
                v = color[width_center,height_center,2]
                # 色範囲を全体に拡大
                h = h * (360 / 256)
                # 色分岐
                if v > 40:
                    if s < 40:
                        color_dir = "white/"
                    else:
                        if h == 0 or h == 360:
                            color_dir = "red/"
                        elif 0 < h < 60:
                            color_dir = "orange/"
                        elif h == 60:
                            color_dir = "yellow/"
                        elif 60 < h < 120:
                            color_dir = "yellowgreen/"
                        elif h == 120:
                            color_dir = "green/"
                        elif 120 < h < 180:
                            color_dir = "bluegreen/"
                        elif h == 180:
                            color_dir = "waterblue/"
                        elif 180 < h < 240:
                            color_dir = "lightblue/"
                        elif h == 240:
                            color_dir = "blue/"
                        elif 240 < h < 300:
                            color_dir = "purple/"
                        elif h == 300:
                            color_dir = "pink/"
                        elif 300 < h < 360:
                            color_dir = "vividpink/"
                        else:
                            color_dir = ""
                else:
                    color_dir = "black/"
        cv2.imwrite(eye_dir + color_dir + temp, image)
        print("checked : " + temp)
        check += 1
print("OK:%d,NG:%d" % (check,skip))