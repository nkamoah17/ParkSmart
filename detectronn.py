# -*- coding: utf-8 -*-
"""
Created on Wed Feb 12 23:41:04 2020

@author: jeren
"""


import os
os.chdir("Mask_RCNN/")

import numpy as np
import cv2
import Mask_RCNN.mrcnn.config
import Mask_RCNN.mrcnn.utils
from Mask_RCNN.mrcnn.model import MaskRCNN
from pathlib import Path
#import cv2_imshow
import pickle

from shapely.geometry import box
from shapely.geometry import Polygon as shapely_poly
from IPython.display import clear_output, Image, display, HTML
import io
import base64
#%matplotlib inline
class Config(Mask_RCNN.mrcnn.config.Config):
    NAME = "coco_pretrained_model_config"
    IMAGES_PER_GPU = 1
    GPU_COUNT = 1
    NUM_CLASSES = 81

config = Config()
config.display()
ROOT_DIR = Path("/Mask_RCNN")
MODEL_DIR = os.path.join(ROOT_DIR, "logs")
COCO_MODEL_PATH = os.path.join(ROOT_DIR, "/mask_rcnn_coco.h5")
if not os.path.exists(COCO_MODEL_PATH):
    Mask_RCNN.mrcnn.utils.download_trained_weights(COCO_MODEL_PATH)

model = MaskRCNN(mode="inference", model_dir=MODEL_DIR, config=Config())
model.load_weights(COCO_MODEL_PATH, by_name=True)
VIDEO_SOURCE = "/home/quenny/Desktop/park/parking/vid3.mp4"
PARKING_REGIONS = "/home/quenny/Desktop/park/parking/regions.p"
class my_dictionary(dict):  
  
    # __init__ function  
    def __init__(self):  
        self = dict()  
          
    # Function to add key:value  
    def add(self, key, value):  
        self[key] = value  
        
with open(PARKING_REGIONS, 'rb') as f:
    parked_car_boxes = pickle.load(f)
    spot_dict = my_dictionary()
    spot_id = 0
    for spot in parked_car_boxes:
        spot_dict.add(spot_id, 'Unknown')
        spot_id += 1
    print(spot_dict)
    
    def get_car_boxes(boxes, class_ids):
        car_boxes = []

        for i, box in enumerate(boxes):
        # If the detected object isn't a car / truck, skip it
            if class_ids[i] in [3, 8, 6]:
                car_boxes.append(box)

        return np.array(car_boxes)

    def compute_overlaps(parked_car_boxes, car_boxes):
    
        new_car_boxes = []
        for box in car_boxes:
            y1 = box[0]
            x1 = box[1]
            y2 = box[2]
            x2 = box[3]
        
            p1 = (x1, y1)
            p2 = (x2, y1)
            p3 = (x2, y2)
            p4 = (x1, y2)
            new_car_boxes.append([p1, p2, p3, p4])
    
        overlaps = np.zeros((len(parked_car_boxes), len(new_car_boxes)))
        for i in range(len(parked_car_boxes)):
            for j in range(car_boxes.shape[0]):
                pol1_xy = parked_car_boxes[i]
                pol2_xy = new_car_boxes[j]
                polygon1_shape = shapely_poly(pol1_xy)
                polygon2_shape = shapely_poly(pol2_xy)

                polygon_intersection = polygon1_shape.intersection(polygon2_shape).area
                polygon_union = polygon1_shape.union(polygon2_shape).area
                IOU = polygon_intersection / polygon_union
                overlaps[i][j] = IOU

        return overlaps

    def arrayShow (imageArray):
        ret, png = cv2.imencode('.png', imageArray)
        encoded = base64.b64encode(png)
        return Image(data=encoded.decode('ascii'))

alpha = 0.6
video_capture = cv2.VideoCapture(VIDEO_SOURCE)
cnt=0

video_FourCC    = cv2.VideoWriter_fourcc('M','J','P','G')
video_fps       = video_capture.get(cv2.CAP_PROP_FPS)
video_size      = (int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH)),
                    int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT)))
out = cv2.VideoWriter("output3.avi", video_FourCC, video_fps, video_size)

while True:
    ret, frame = video_capture.read()
    if ret:
      overlay = frame.copy()
    else:
    	break

    rgb_image = frame[:, :, ::-1]
    results = model.detect([rgb_image], verbose=0)

    car_boxes = get_car_boxes(results[0]['rois'], results[0]['class_ids'])
    overlaps = compute_overlaps(parked_car_boxes, car_boxes)
    counter = 0


    for parking_area, overlap_areas in zip(parked_car_boxes, overlaps):
        max_IoU_overlap = np.max(overlap_areas)
        if max_IoU_overlap < 0.15:
            cv2.fillPoly(overlay, [np.array(parking_area)], (71, 27, 92))
            free_space = True
            spot_dict[counter] = 'Empty'
            cv2.putText(frame, "Spot " + str(counter) + " is empty", (50,50), cv2.FONT_HERSHEY_SIMPLEX, 1,2)
        else:
            spot_dict[counter] = 'Occupied'
        counter += 1
        
    print(spot_dict)
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

    out.write(frame)

    clear_output(wait=True)
    img = arrayShow(frame)
    display(img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video_capture.release()
out.release()
cv2.destroyAllWindows()
