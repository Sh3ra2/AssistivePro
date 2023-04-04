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
font = cv2.FONT_HERSHEY_COMPLEX

class attendance(object):

    #<---------------- Function ---------------->
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        self.encodeListKnown = []
        # -- Load the encoding file
        print("Loading Encode File ...")
        file = open("static/EncodedFace.p", "rb")
        encodeListKnownWithIds = pickle.load(file)
        file.close()
        self.encodeListKnown, self.studentIds = encodeListKnownWithIds
        print("Loaded")

    #<---------------- Function ---------------->
    def __del__(self):
        self.video.release()

    #<---------------- Function ---------------->
    def get_frame(self):
        # print("Hello you are capturing frame")

        success, img = self.video.read()

        prev_frame_time = 0
  
        counter = 0
        id = -1
        imgStudent = []


        imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

        faceCurFrame = face_recognition.face_locations(imgS)
        encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

        if faceCurFrame:
            # print("Face are present")
            for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
                matches = face_recognition.compare_faces(self.encodeListKnown, encodeFace)
                faceDis = face_recognition.face_distance(self.encodeListKnown, encodeFace)
                print("matches", matches)
                print("faceDis", faceDis)

                if matches and faceDis:
                    matchIndex = np.argmin(faceDis)
                    # print("Match Index", matchIndex)

                    if matches[matchIndex]:
                        # Getting face locations and drawing rectangle
                        y1, x2, y2, x1 = faceLoc
                        y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4

                        cv2.rectangle(img, (x1, y1 ), (x2, y2), (0, 255, 0), 2)
                        #getting id of matched face
                        id = self.studentIds[matchIndex]
                        if counter == 0:
                            cv2.waitKey(1)
                            counter = 1
                        

                if counter != 0:

                    if counter == 1:
                        # Get the Data
                        studentInfo = db.reference(f'Students/{id}').get()
                        # print(studentInfo)
                        

                        new_ref = db_1.collection(u'recent_att').document(id)

                        new_ref.set({
                            u'id': id
                        }, merge=True)

                        # Update attendance
                        datetimeObject = datetime.strptime(studentInfo['Last_attendance'],
                                                        "%Y-%m-%d %H:%M:%S")
                        secondsElapsed = (datetime.now() - datetimeObject).total_seconds()
                        print(secondsElapsed)
                        if secondsElapsed > 30:
                            ref = db.reference(f'Students/{id}')
                            studentInfo['Total_attendance'] += 1
                            ref.child('Total_attendance').set(studentInfo['Total_attendance'])
                            ref.child('Last_attendance').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                
        frame_flip = cv2.flip(img,1)
        ret, jpeg = cv2.imencode('.jpg', frame_flip)
        return jpeg.tobytes()