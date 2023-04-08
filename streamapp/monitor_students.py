import sys
import time
import numpy as np
import tensorflow as tf
import cv2
from django.views import View
from django.http import HttpResponse
from .heads_detector import FROZEN_GRAPH_HEAD

# class HeadDetectionView(object):
#     def __init__(self):
#         self.video = cv2.VideoCapture(0)
#         PATH_TO_CKPT_HEAD = 'static/HEAD_DETECTION_300x300_ssd_mobilenetv2.pb'
#         self.head_detector = FROZEN_GRAPH_HEAD(PATH_TO_CKPT_HEAD)


#     #<---------------- Function ---------------->
#     def __del__(self):
#         self.video.release()


#     def get_frame(self):

#         ret, image = self.video.read()
            

#         im_height, im_width, im_channel = image.shape
#         image = cv2.flip(image, 1)

#         # -- Head-detection run model
#         image, heads = self.head_detector.run(image, im_width, im_height)
        
#         ret, jpeg = cv2.imencode('.jpg', image)
#         return jpeg.tobytes()
        

class HeadDetectionView(object):
    def __init__(self):
        # self.video = cv2.VideoCapture(0)
        PATH_TO_CKPT_HEAD = 'static/HEAD_DETECTION_300x300_ssd_mobilenetv2.pb'
        self.head_detector = FROZEN_GRAPH_HEAD(PATH_TO_CKPT_HEAD)

    def get_frame(self, inputframe):
        im_height, im_width, im_channel = inputframe.shape
        inputframe = cv2.flip(inputframe, 1)

        # -- Head-detection run model
        image, heads = self.head_detector.run(inputframe, im_width, im_height)
        mimage = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # ret, jpeg = cv2.imencode('.jpg', image)
        # return jpeg.tobytes()
        return mimage