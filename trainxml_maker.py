import os
import cv2

def out_header(xml):
    print("<?xml version='1.0' encoding='ISO-8859-1'?>", file=xml)
    print("<?xml-stylesheet type='text/xsl' href='image_metadata_stylesheet.xsl'?>", file=xml)
    print("<dataset>", file=xml)
    print("<name>imglab dataset</name>", file=xml)
    print("<images>", file=xml)
    return

def out_list(xml,path):
    cascade = cv2.CascadeClassifier("./lbpcascade_animeface.xml")
    for temp in os.listdir(path):
        filename = path + temp
        image = cv2.imread(filename)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        facerect = cascade.detectMultiScale(gray,\
                                                scaleFactor=1.11,\
                                                minNeighbors=2,\
                                                minSize=(64, 64))
        if len(facerect) > 0:
            print("<image file='" + filename + "'>", file=xml)
            for i, rect in enumerate(facerect):
                #顔だけ切り出して保存
                left, top, width, height = tuple(rect[0:4])
                print("<box top='" + str(top) + "' left='" + str(left) + "' width='" + str(width) + "' height='" + str(height) + "'/>", file=xml)
            print("</image>", file=xml)
    return

def out_footer(xml):
    print("</images>", file=xml)
    print("</dataset>", file=xml)
    return

if __name__ == "__main__":
    filename = "./all.xml"
    basepath = "./base/"
    xmlfile = open(filename,"w")
    out_header(xmlfile)
    out_list(xmlfile, basepath)
    out_footer(xmlfile)
    exit()