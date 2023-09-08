import git
import os

if not os.path.exists("Mask_RCNN"):
    print("Cloning M-RCNN repository...")
    git.Git("./").clone("https://github.com/matterport/Mask_RCNN.git")

import numpy as np
import cv2
import Mask_RCNN.mrcnn.config
import Mask_RCNN.mrcnn.utils
from Mask_RCNN.mrcnn.model import MaskRCNN
from pathlib import Path
import pickle
import argparse

from shapely.geometry import box
from shapely.geometry import Polygon as shapely_poly
import io
import base64

# This class is a configuration for the Mask R-CNN model.
# It sets the name of the configuration, the number of images per GPU, the number of GPUs, and the number of classes.
# The number of classes is set to 81 to include the 80 COCO classes plus the background class.
class Config(Mask_RCNN.mrcnn.config.Config):
    NAME = "model_config"
    IMAGES_PER_GPU = 1
    GPU_COUNT = 1
    NUM_CLASSES = 81

# Create an instance of the Config class and display its properties.
# This is useful for debugging and ensuring that the configuration has been set up correctly.
config = Config()
config.display()

# Set the root directory, model directory, and path to the COCO model weights.
# These paths are used to load the model and its weights.
ROOT_DIR = os.getcwd()
MODEL_DIR = os.path.join(ROOT_DIR, "logs")
COCO_MODEL_PATH = os.path.join(ROOT_DIR, "mask_rcnn_coco.h5")

# Print the path to the COCO model weights and download the weights if they do not already exist.
# This ensures that the model has the necessary weights to make predictions.
print(COCO_MODEL_PATH)
if not os.path.exists(COCO_MODEL_PATH):
    Mask_RCNN.mrcnn.utils.download_trained_weights(COCO_MODEL_PATH)

# Create an instance of the Mask R-CNN model in inference mode with the specified configuration and load the weights.
# This model will be used to make predictions on new images.
model = MaskRCNN(mode="inference", model_dir=MODEL_DIR, config=Config())
model.load_weights(COCO_MODEL_PATH, by_name=True)
def get_cars(boxes, class_ids):
    """
    This function takes in bounding boxes and class IDs as input.
    It iterates over the boxes and checks if the class ID for each box is in the list [3, 8, 6].
    If the condition is met, the box is appended to the 'cars' list.
    The function returns the 'cars' list as a numpy array.
    """
    cars = []
    for i, box in enumerate(boxes):
        if class_ids[i] in [3, 8, 6]:
            cars.append(box)
    return np.array(cars)

def compute_overlaps(parked_car_boxes, car_boxes):
    """
    This function calculates the overlap between parked car boxes and other car boxes.
    It iterates over the car boxes and creates a new list of boxes with coordinates for each corner of the box.
    It then initializes an array of zeros with dimensions corresponding to the number of parked car boxes and new car boxes.
    For each parked car box, it calculates the Intersection over Union (IoU) with each new car box.
    The IoU is calculated as the area of intersection of the two boxes divided by the area of their union.
    The IoU for each pair of boxes is stored in the 'overlaps' array.
    The function returns the 'overlaps' array.
    """
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
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('video_path', help="Video file")
    parser.add_argument('regions_path', help="Regions file", default="regions.p")
    args = parser.parse_args()

    regions = args.regions_path
    with open(regions, 'rb') as f:
        parked_car_boxes = pickle.load(f)

    VIDEO_SOURCE = args.video_path
    alpha = 0.6
    video_capture = cv2.VideoCapture(VIDEO_SOURCE)
    video_FourCC    = cv2.VideoWriter_fourcc('M','J','P','G')
    video_fps       = video_capture.get(cv2.CAP_PROP_FPS)
    video_size      = (int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH)),
                        int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    out = cv2.VideoWriter("out.avi", video_FourCC, video_fps, video_size)

    while video_capture.isOpened():
        success, frame = video_capture.read()
        overlay = frame.copy()
        if not success:
            break

        rgb_image = frame[:, :, ::-1]
        results = model.detect([rgb_image], verbose=0)

        cars = get_cars(results[0]['rois'], results[0]['class_ids'])
        overlaps = compute_overlaps(parked_car_boxes, cars)

        for parking_area, overlap_areas in zip(parked_car_boxes, overlaps):
            max_IoU_overlap = np.max(overlap_areas)
            if max_IoU_overlap < 0.15:
                cv2.fillPoly(overlay, [np.array(parking_area)], (71, 27, 92))
                free_space = True      
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

        cv2.imshow('output', frame)
        out.write(frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    out.release()
    cv2.destroyAllWindows()
    print("output saved as out.avi")