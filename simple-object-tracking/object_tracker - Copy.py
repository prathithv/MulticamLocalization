# Main object tracket including GUI

# Last edit : @prathithv, 17/04/2020, 18:45


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

# stop variable to staop the whole program
stop_variable = 0

# socket multi-thread methods and variables
NUMBER_OF_THREADS = 2
JOB_NUMBER = [1, 2]
queue = Queue()
# hold the list of client objects of all the connections and addresses
all_connections = []
all_address = []
#data queue to handle data from all the clients and process in the main thread
in_data = Queue()
in_data_classes = Queue()

# socket variables
a=10 
# header size of the incoming packet from client
# this value should be same as in client program
host = "" 
# keep host IP blank for reverse-shell
# server IP needs to be mentioned in client program
port = 9999 
# port is user defined can take values between 1025-65500
# port should match with the client program configuration

def create_socket():
    try:
        global host
        global port
        global s
        host = ""
        port = 9999
        s = socket.socket()

    except socket.error as msg:
        print("Socket creation error: " + str(msg))
        
# Binding the socket and listening for connections
def bind_socket():
    try:
        global host
        global port
        global s
        print("Binding the Port: " + str(port))

        s.bind((host, port))
        s.listen(2)

    except socket.error as msg:
        print("Socket Binding error" + str(msg) + "\n" + "Retrying...")
        bind_socket()


# variable for differentiating class data and location data
count_recv=0

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
    [40,320,217,420],
    # camera 1
    [200,300,400,500],
    # camera 2
    [200,300,400,500],
]

# initialize our centroid tracker and frame dimensions
# initializing the centroid tracker class (constructor)
ct = CentroidTracker()
(H, W) = (None, None)


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
focal = 260.0 # camera focal width, a constant from formula
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
def data_pre_process(client_num, classes, rects):
    dist = []
    for i in range(0,len(rects)):
        #print(len(rects))
        deltaX = camera_field_of_view[0][2] - camera_field_of_view[0][0]
        deltaY = camera_field_of_view[0][3] - camera_field_of_view[0][1]
        rects[i][0] = rects[i][0]*deltaX + camera_field_of_view[0][0]
        rects[i][1] = rects[i][1]*deltaY + camera_field_of_view[0][1]
        rects[i][2] = rects[i][2]*deltaX + camera_field_of_view[0][0]
        rects[i][3] = rects[i][3]*deltaY + camera_field_of_view[0][1] 
        
        pixel_width = rects[i][2] - rects[i][0]
        print(f"pixel_width = {pixel_width}")
        if pixel_width != 0:
            dis = find_distance(pixel_width, classes)
            dis = dis + camera_field_of_view[0][1]
        else:
            dis = 0
            dis = dis + camera_field_of_view[0][1] 
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

def get_data_from_server(rects):
    global count_recv
    complete_info = b''
    rec_msg = True
    break_var = False
    while True:
        mymsg = clt.recv(16)
        if rec_msg:
            #print(f"The length of message = {mymsg[:a]}")
            x=int(mymsg[:a])
            #x = pickle.loads(mymsg)
            rec_msg = False
        complete_info += mymsg
        #print(f"\ncomplete_info : {len(complete_info)}")
        #print(f"\nx : {x}")
        #print(f"\na : {a}")
        if len(complete_info) - a == x:
            m = pickle.loads(complete_info[a:])
            if count_recv==0:
                print("object:")
                if m==1:
                    print("bag detected")
                elif m==2:
                    print("Person With Bag")
                else:
                    print("Person Without Bag")
                count_recv=count_recv+1
            else:
                print("location")
                print(m)
                rects.append(m)
                count_recv=0
                break_var = True
            #print(complete_info[a:])
            #m = pickle.loads(complete_info[a:])
            #print(m)
            rec_msg = True
            complete_info = b''
            #count=count+1
        if break_var == True:
            break
        #complete_info = b''


# loop over the frames from the video stream
def main_work():
    while True:
        
        # creating rects for storing current detected locations
        rects = []
        if in_data.empty() == False:
            current_data = in_data.get()
            dist = data_pre_process(current_data[0],current_data[1],current_data[2:])
            objects = ct.update(rects, dist)
            # get_data_from_server(rects)
            
            # print(f"main rects = {rects}")
        
            # data pre processing and finding distance
            # dist = data_pre_process(rects,)
            
            # print(f"dist = {dist}")
        
            # objects = ct.update(rects, dist)
        
            # print(f"objects = {objects}")
        
            if len(objects) != len(prev_objects):
                for key in objects.keys():
                    if not key in prev_objects:
                        # create new tracks
                        create_track(key,objects[key],current_data[1])
        
                for key in prev_objects.keys():
                    if not key in objects:
                        # delete the old tracks
                        delete_track(key)
            
            # loop over the tracked objects
            for (objectID, centroid) in objects.items():
                update_tracks(objects)
        
            # noting down the previous points to compare with the next points
            # global prev_objects
            prev_objects = copy.deepcopy(objects)


#############################################################################
#                   BASE THREAD                                             #
#############################################################################
# flush previous data and get ready
for c in all_connections:
        c.close()
del all_connections[:]
del all_address[:]
print("flush complete")

# starting the main thread for handling UI operations
start_main_thread()

# create and bind the socket
create_socket()
bind_socket()

# change stop_variable in main thread by cheking an input from keyboard
while stop_variable == 0:
    pass
# do a bit of cleanup
win.close()
cv2.destroyAllWindows()
vs.stop()