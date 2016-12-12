import os
import cv2

file_dir = "./pos/"
raw_dir = "./raw/"
if os.path.exists(raw_dir) == False:
    os.mkdir(raw_dir)
face_dir = "./face/"
if os.path.exists(face_dir) == False:
    os.mkdir(face_dir)
# サンプル目認識特徴量ファイル
cascade_path = "./haarcascade_eye.xml"
# 目検出枠の色
color = (255, 0, 0)
cascade = cv2.CascadeClassifier(cascade_path)
# 変数
skip = 0
check = 0

for temp in os.listdir(file_dir):
    filename = file_dir + temp
    image = cv2.imread(filename)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    facerect = cascade.detectMultiScale(gray,\
                                            scaleFactor=1.11,\
                                            minNeighbors=2,\
                                            minSize=(16, 16))
    # 目が検出できない場合
    if len(facerect) <= 0:
        print("skiped : " + temp)
        skip += 1
    else:
        for i, rect in enumerate(facerect):
            #目だけ切り出して保存
            x, y, width, height = tuple(rect[0:4])
            dst = image[y:y+height, x:x+width]
            new_image_path = face_dir + temp
            cv2.imwrite(new_image_path, dst)
        for rect in facerect:
            cv2.rectangle(image, tuple(rect[0:2]),
                        tuple(rect[0:2] + rect[2:4]),
                        color, thickness=2)
        cv2.imwrite(raw_dir + temp, image)
        print("checked : " + temp)
        check += 1

print("check:%d,skip:%d" % (check,skip))