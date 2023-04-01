import cv2
import face_recognition
import pickle
import os
from .models import profile_image
# from firebase_setup import firestart
from firebase_admin import credentials, firestore, storage


def encode_process():

    #importing faces of students
    folderModePath = 'media/encode_images'
    traindatalist = os.listdir(folderModePath)
    dataList = []
    student_id = []

    for path in traindatalist:
        dataList.append(cv2.imread(os.path.join(folderModePath,path)))
        # print(path)
        # print(os.path.splitext(path)[0])
        student_id.append(os.path.splitext(path)[0])
    print(student_id)
    print(len(dataList))
    # print(len(imgModeList[0]))


    print("Encoding faces....")
    def findencodings(data_list):
        encodeList = []
        p = 0
        For_percentage = len(data_list)
        print("Length of list ",For_percentage)

        for i, image in enumerate(data_list):
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            encode = face_recognition.face_encodings(image)[0]
            encodeList.append(encode)
            p = (((i+1)/For_percentage)*100)
            print((((i+1)/For_percentage)*100), "% Done")
            percent = p
        return encodeList

    encodeListKnown = findencodings(dataList)
    print("Encoding Complete")
    print("Length Encode list known:", len(encodeListKnown))
    # print("Encod list known", encodeListKnown)
    encodeListKnown_WithIds = [encodeListKnown, student_id]

    file = open("static/EncodedFace.p", "wb")
    pickle.dump(encodeListKnown_WithIds,file)
    file.close()

    print("File saved")


encode_process()