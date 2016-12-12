import os
import cv2

cascade_path = "./lbpcascade_animeface.xml"
movie_path = "./movie/"
face_base_path = "./face/"
faceframenum = 0

def detectFace(image):
    image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image_gray = cv2.equalizeHist(image_gray)
    cascade = cv2.CascadeClassifier(cascade_path)
    facerect = cascade.detectMultiScale(image_gray, scaleFactor=1.1, minNeighbors=3, minSize=(128, 128))
    return facerect

### main ###
for movie in os.listdir(movie_path):
    filename = movie_path + movie
    cap = cv2.VideoCapture(filename)
    name, ext = os.path.splitext(movie)
    os.mkdir(face_base_path + name + "/")
    framenum = 0
    while(1):
        framenum += 1
        ret, image = cap.read()
        if not ret: break
        if framenum%30 == 0:
            facerect = detectFace(image)
            if len(facerect) == 0: continue
            for rect in facerect:
                croped = image[rect[1]:rect[1]+rect[3],rect[0]:rect[0]+rect[2]]
                cv2.imwrite(face_base_path + name + "/" + str(faceframenum).zfill(10) + ".jpg", croped)
                print(face_base_path + name + "/" + str(faceframenum).zfill(10) + ".jpg")
                faceframenum += 1
    cap.release()