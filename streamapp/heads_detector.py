import sys
import time
import numpy as np
# import tensorflow as tf
import mediapipe as mp
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_face_mesh = mp.solutions.face_mesh
import tensorflow._api.v2.compat.v1 as tf
from .head_pose_pred import detect_head_turns
from django.contrib.auth.models import User
tf.disable_v2_behavior()

import cv2
# Set the compression quality in which you are saving image(0 - lowest, 100 - highest)
compression_quality = 20

import firebase_admin
from firebase_admin import credentials, firestore, storage, db
from datetime import datetime
from .models import settings_model

# -- set logging
import logging
# -- Configure logging
logger = logging.getLogger('head_pose')
logging.basicConfig(filename='log/head_pose.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')


# <-------------- Accessing database -------------->
if not firebase_admin._apps:
    cred = credentials.Certificate("static/server-assistivepro-firebase-adminsdk-mpb8d-f8b5a22e4e.json")
    app = firebase_admin.initialize_app(cred,{
        'databaseURL': "https://server-assistivepro-default-rtdb.firebaseio.com/",
	    'storageBucket': "server-assistivepro.appspot.com"
	})
bucket = storage.bucket()
db = firestore.client()


class FROZEN_GRAPH_HEAD():
    
    def __init__(self, PATH_TO_CKPT):
        self.inference_list = []
        self.count = 0
        self.countL = 0
        self.countR = 0
        self.state = "Center"
        self.angle_face = 0
        self.start_time = time.time()

        self.detection_graph = tf.Graph()
        with self.detection_graph.as_default():
            od_graph_def = tf.GraphDef()
            with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name='')


        with self.detection_graph.as_default():
            config = tf.ConfigProto()
            config.gpu_options.allow_growth = True
            self.sess = tf.Session(graph=self.detection_graph, config=config)
            self.windowNotSet = True

    
    def draw_bounding_box(self, image, scores, boxes, classes, im_width, im_height, username):
        boxes = np.squeeze(boxes)
        scores = np.squeeze(scores)
        classes = np.squeeze(classes).astype(np.int32)

        # -- get user for "count"
        user = User.objects.get(username=username)
        user_settings_pre = settings_model.objects.get(user=user).id_settings

        # -- Counts allowed are given to function
        req_count_turns = settings_model.objects.get(id_settings = user_settings_pre).head_turn_count
        # req_count_turns = settings_model.objects.get(id_settings = 1).head_turn_count
        print("req data is", req_count_turns)

        heads = list()
        idx = 1

        for score, box, name in zip(scores, boxes, classes):
            if name == 1 and score > 0.9:
                left = int((box[1])*im_width)
                top = int((box[0])*im_height)
                right = int((box[3])*im_width)
                bottom = int((box[2])*im_height)
                i = 0

                cropped_head = np.array(image[top:bottom, left:right])

                self.countL, self.countR, self.state, self.start_time, processed_frame, self.angle_face = detect_head_turns(cropped_head, self.countL, self.countR, self.state, self.start_time, self.angle_face, username)
                # print("angle face is ", self.angle_face)
                width = right - left
                height = bottom - top
                bottom_mid = (left + int(width / 2), top + height)
                confidence = score
                label = name

                mydict = {
                    "head_id": idx,
                    "width": width,
                    "height": height,
                    "cropped": cropped_head,
                    "left": left,
                    "right": right,
                    "top": top,
                    "bottom": bottom,
                    "confidence": confidence,
                    "label": None,
                    "bottom_mid": bottom_mid,
                    "face_angle" : self.angle_face,
                    "model_type": 'FROZEN_GRAPH',
                    "count_left": self.countL,
                    "count_right": self.countR,
                    "state": self.state,
                }
                heads.append(mydict)
                idx += 1

                cv2.putText(image, f'Left: {self.countL} || Right: {self.countR}', (left, top-4), 0, 0.55, (0, 255, 255), 2)
                cv2.putText(image, f'ID: {idx}', (left, bottom+18), 0, 0.55, (0, 255, 255), 2)
                cv2.rectangle(image, (left, top), (right, bottom), (0, 255, 0), 2, 8)
                # cv2.putText(image, 'score: {:.2f}%'.format(score), (left, bottom+35), 0, 0.55, (0, 255, 255), 2)
                cv2.putText(image, 'Angle: {:.2f}%'.format(self.angle_face), (left, bottom+35), 0, 0.55, (0, 255, 255), 2)

                if (self.countL == req_count_turns or self.countR == req_count_turns):
                    print("Photo Being Sent")
                    logger.critical("Photo Being Saved")

                    cv2.rectangle(image, (left, top), (right, bottom), (0, 0, 225), 2, 8)
                    timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
                    # -- naming image
                    file_name = f'capture_{timestamp}.jpg'
                    source_address = f"media/alerts/{file_name}"
                    
                    # -- saving image 
                    cv2.imwrite(source_address, image, [cv2.IMWRITE_JPEG_QUALITY, compression_quality])
                    logger.critical("Photo saved -> %s", source_address)

                    # -- Uplaoding file
                    bucket = storage.bucket()
                    blob = bucket.blob(f'Alerts/{file_name}')
                    logger.critical("Blob being uploaded")
                    blob.upload_from_filename(source_address)
                    logger.critical("Blob uploaded")

                    # -- uploading alert in firestore
                    name_for_upload = {
                        u'name': file_name,
                    }
                    alert_ref = db.collection(u'Alerts').add(name_for_upload)
                    logger.critical("data store updated")
                    self.countL = 0
                    self.countR = 0
                    logger.critical("Photo Just Sent")
                    print("Photo processed")

        return image, heads


    # function for procesing input image
    def run(self, image, im_width, im_height, username):
        """image: bgr image
        return (boxes, scores, classes, num_detections)
        """
        image_np = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # the array based representation of the image will be used later in order to prepare the
        # result image with boxes and labels on it.
        # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
        image_np_expanded = np.expand_dims(image_np, axis=0)
        image_tensor = self.detection_graph.get_tensor_by_name('image_tensor:0')
        # Each box represents a part of the image where a particular object was detected.
        boxes = self.detection_graph.get_tensor_by_name('detection_boxes:0')
        # Each score represent how level of confidence for each of the objects.
        # Score is shown on the result image, together with the class label.
        scores = self.detection_graph.get_tensor_by_name('detection_scores:0')
        classes = self.detection_graph.get_tensor_by_name('detection_classes:0')
        num_detections = self.detection_graph.get_tensor_by_name('num_detections:0')
        
        # Actual detection.
        start_time = time.time()
        
        (boxes, scores, classes, num_detections) = self.sess.run(
            [boxes, scores, classes, num_detections],
            feed_dict={image_tensor: image_np_expanded})
        
        elapsed_time = time.time() - start_time
        self.inference_list.append(elapsed_time)
        self.count = self.count + 1
        average_inference = sum(self.inference_list)/self.count
        # print('Average inference time: {}'.format(average_inference))

        # return (boxes, scores, classes, num_detections)

        # Draw bounding boxes on the image
        image, heads = self.draw_bounding_box(image, scores, boxes, classes, im_width, im_height, username)
        # print("heads has ", heads)
        
        

        return image, heads