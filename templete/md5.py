import hashlib
import os

data_dir = ""
md5_data = []

for filename in os.listdir(data_dir):
    deleted = False
    f = open(data_dir + filename,"rb")
    md5 = hashlib.md5(f.read()).hexdigest()
    for geted_md5 in md5_data:
        if geted_md5 == md5:
            f.close()
            os.remove(data_dir + filename)
            print("deleted : " + filename)
            deleted = True
            break
    if deleted == False:
        md5_data.append(md5)
        f.close()