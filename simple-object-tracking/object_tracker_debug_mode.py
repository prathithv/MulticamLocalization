# Main object tracket including GUI

# Last edit : @prathithv, 14/04/2020, 18:31


# File Description


# import the necessary packages
from graphics import *
from pyimagesearch.centroidtracker import CentroidTracker
import imutils
import numpy as np
from imutils.video import VideoStream
import time
import cv2
from collections import OrderedDict
import copy
import socket
import pickle


# Global Variables
# by the way.... all the dictionaries are ordered from python 3.6
# simply using OrderDict() for no reason
objectCount = OrderedDict()
classes = OrderedDict()
prev_objects = OrderedDict()


# defining macros or constants for multi-camera system
# camera field of view
# in the format Xmin,Ymin,Xmax,Ymax
# it is a 2-D matrix representing each row with each unique camera ID
# ** IMPORTANT ** : Get these values from calibration.py
camera_field_of_view = [
    # camera 0
    [200,300,400,500],
    # camera 1
    [200,300,400,500],
    # camera 2
    [200,300,400,500],
]


# only for debugging
args = {'prototxt': 'deploy.prototxt','model': 'res10_300x300_ssd_iter_140000.caffemodel', 'confidence': 0.5}

# initialize our centroid tracker and frame dimensions
# initializing the centroid tracker class (constructor)
ct = CentroidTracker()
(H, W) = (None, None)

# only for debugging
net = cv2.dnn.readNetFromCaffe(args["prototxt"], args["model"])
vs = VideoStream(src=1).start()


# UI Window creation and adding map (should only be of .gif type)
# width and height of GUI Window
WINDOW_WIDTH = 700
WINDOW_HEIGHT = 500
win = GraphWin("My Window", WINDOW_WIDTH, WINDOW_HEIGHT)
win.setBackground('black')
img = Image(Point(350, 250), "bengaluru_airport.gif")
img.draw(win)

# distance integration
# pre processing the received data

# constants for finding the distance of the object from camera
# F = (P x D) / W
# where F = Focal length of camera (in m)
#       P = width of object in pixels
#       D = Distance of object from camera (in m)
#       W = actual width of the objects (in m)
focal = 399.0 # camera focal width, a constant from formula
object_width_bag = 9 # average width of a bag
object_width_personWithBag = 9 # average width of person with bag
object_width_personWithoutBag = 9 # average width of person without bag

# function to find distance of the object from camera
def find_distance(pixel_width, classes):
    if classes == 0:
        return (focal * object_width_bag) / pixel_width
    elif classes == 1:
        return (focal * object_width_personWithBag) / pixel_width
    else:
        return (focal * object_width_personWithoutBag) / pixel_width

# classes should be changed to a list
# should take care of narmal FoV and inverted FoV
def data_pre_process(rects, classes):
    dist = []
    for i in range(0,len(rects)):
        pixel_width = rects[i][3] - rects[i][1]
        dis = find_distance(pixel_width, classes)
        dist.append(dis)
    return dist


# create tracks if new tracks are added
def create_track(objectID, centroid):
    pt = Point(centroid[0], centroid[1])
    cir = Circle(pt, 5)
    cir.setFill(color_rgb(0, 255, objectID*10))
    cir.draw(win)
    objectCount[key] = cir

def delete_track(key):
    objectCount[key].undraw()
    del objectCount[key]

# this function is only for updating UI dot not for actual track update
def update_tracks(objects):
    for key in objects.keys():
        if key in prev_objects.keys():
            x = prev_objects.get(key)
            y = objects.get(key)
            # print(f"x  :{x}  y  :{y}  \n\n")
            dx = x[0] - y[0]
            dy = x[1] - y[1]
            # print(f"dx  :{dx}   dy  :{dy}  ")
        else:
            dx = 0
            dy = 0
        if len(objectCount):
            objectCount[key].move(dx, dy)


# loop over the frames from the video stream
while True:

    # only for debugging
    frame = vs.read()
    frame = imutils.resize(frame, width=400)

    # if the frame dimensions are None, grab them
    if W is None or H is None:
        (H, W) = frame.shape[:2]

    # only for debugging
    blob = cv2.dnn.blobFromImage(frame, 1.0, (W, H),(104.0, 177.0, 123.0))
    net.setInput(blob)
    detections = net.forward()

    # creating rects for storing current detected locations
    rects = []

    for i in range(0, detections.shape[2]):
        if detections[0, 0, i, 2] > args["confidence"]:
            # compute the (x, y)-coordinates of the bounding box for
            # the object, then update the bounding box rectangles list
            box = detections[0, 0, i, 3:7] * np.array([W, H, W, H])
            rects.append(box.astype("int"))

            (startX, startY, endX, endY) = box.astype("int")
            cv2.rectangle(frame, (startX, startY), (endX, endY),
                          (100, 125, 0), 2)

    # data pre processing and finding distance
    dist = data_pre_process(rects,1)
    
    #print(rects)

    objects = ct.update(rects, dist)

    if len(objects) != len(prev_objects):
        for key in objects.keys():
            if not key in prev_objects:
                # create new tracks
                create_track(key,objects[key])

        for key in prev_objects.keys():
            if not key in objects:
                # delete the old tracks
                delete_track(key)
    
    # loop over the tracked objects
    for (objectID, centroid) in objects.items():
        text = "ID {}".format(objectID)
        cv2.putText(frame, text, (centroid[0] - 10, centroid[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
        cv2.circle(frame, (centroid[0], centroid[1]), 4, (255, 0, 0), -1)
        update_tracks(objects)
    # show the output frame

    # noting down the previous points to compare with the next points
    # global prev_objects
    prev_objects = copy.deepcopy(objects)

    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF

    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        ct.endAll()
        break

# do a bit of cleanup
win.close()
cv2.destroyAllWindows()
vs.stop()