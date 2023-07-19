import os
import pickle
import cv2
import face_recognition
import firebase_admin
from firebase_admin import credentials, firestore, storage, db
import numpy as np
from datetime import datetime
import time

# <-------------- Accessing database -------------->
if not firebase_admin._apps:
    cred = credentials.Certificate("static/server-assistivepro-firebase-adminsdk-mpb8d-f8b5a22e4e.json")
    app = firebase_admin.initialize_app(cred,{
        'databaseURL': "https://server-assistivepro-default-rtdb.firebaseio.com/",
	    'storageBucket': "server-assistivepro.appspot.com"
	})
bucket = storage.bucket()
db_1 = firestore.client()
db = firestore.client()
font = cv2.FONT_HERSHEY_COMPLEX

class attendance(object):

    #<---------------- Function ---------------->
    def __init__(self):
        self.encodeListKnown = []
        self.studentIds = []
        

    def load_encode_file(self, myuser):
        # Load the encoding file
        print("Loading Encode File ...")
        with open(f"Encodings/{myuser}/EncodedFace.p", "rb") as file:
            encodeListKnownWithIds = pickle.load(file)
            self.encodeListKnown, self.studentIds = encodeListKnownWithIds
        print("Loaded")

    #<---------------- Function ---------------->
    def process_frame(self, img):
        prev_frame_time = 0
        counter = 0
        id = -1
        imgStudent = []

        print("Processing faces")

        imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

        faceCurFrame = face_recognition.face_locations(imgS)
        encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

        if faceCurFrame:
            for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
                matches = face_recognition.compare_faces(self.encodeListKnown, encodeFace)
                faceDis = face_recognition.face_distance(self.encodeListKnown, encodeFace)
                print("FaceDIs is ",faceDis)

                if matches and faceDis.any():
                    matchIndex = np.argmin(faceDis)

                    if matches[matchIndex]:
                        y1, x2, y2, x1 = faceLoc
                        y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4

                        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        id = self.studentIds[matchIndex]
                        print("Id is ", id)
                        if counter == 0:
                            cv2.waitKey(1)
                            counter = 1

                if counter != 0:

                    if counter == 1:
                        # studentInfo = db.reference(f'Students/{id}').get()
                        users_ref = db.collection(u'Students').document(id)
                        # Get data from the document
                        doc = users_ref.get()

                        if doc.exists:
                            data = doc.to_dict()
                            print("Document data:", data)
                        else:
                            print("Document does not exist.")

                        new_ref = db_1.collection(u'recent_att').document(id)

                        new_ref.set(data, merge=True)
        
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        return img
