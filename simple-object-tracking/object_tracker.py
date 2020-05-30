# Main object tracket including GUI

# Last edit : @prathithv, 17/04/2020, 18:45


# File Description
# =============================================================================
# SERVER PROGRAM FOR MULTICAM LOCALIZATION AND TRACKING
# =============================================================================

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
from queue import Queue
import threading
from scipy.spatial import distance as dist
import math
# import file

# stop variable to stop the whole program
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
in_data_face = Queue()

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
textCount = OrderedDict()
classes = OrderedDict()
prev_objects = OrderedDict()
bagPersonRelation = OrderedDict()
live_count = 0

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

def initialize_UI():
    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 600
    global win 
    win = GraphWin("My Window", WINDOW_WIDTH, WINDOW_HEIGHT)
    win.setBackground('black')
    img = Image(Point(400, 300), "bengaluru_airport.gif")
    img.draw(win)
    titleRec = Rectangle(Point(0,0), Point(800,50))
    titleRec.setFill("yellow")
    titleRec.draw(win)
    Title = Text(Point(400, 25), "Multicam Localization")
    Title.setSize(24)
    Title.draw(win)
    liveCountRec = Rectangle(Point(0,50), Point(400,90))
    liveCountRec.setFill("purple")
    liveCountRec.draw(win)
    global LiveCount
    LiveCount = Text(Point(200, 70), f"Live Count : {len(objectCount)}")
    LiveCount.setSize(18)
    LiveCount.setStyle("bold")
    LiveCount.draw(win)
    cameraCountRec = Rectangle(Point(400,50), Point(800,90))
    cameraCountRec.setFill("purple")
    cameraCountRec.draw(win)
    global cameraCount
    cameraCount = Text(Point(600,70), f"No. of cameras online : {len(all_connections)}")
    cameraCount.setSize(18)
    cameraCount.setStyle("bold")
    cameraCount.draw(win)
    crookAlertRec = Rectangle(Point(0, 90), Point(400,120))
    crookAlertRec.setFill("orange")
    crookAlertRec.draw(win)
    bagAlertRec = Rectangle(Point(400, 90), Point(800,120))
    bagAlertRec.setFill("orange")
    bagAlertRec.draw(win)
    global crookAlert
    global bagAlert
    crookAlert = Text(Point(200, 105), "Crook  :  No Alert")
    crookAlert.setTextColor("black")
    crookAlert.draw(win)
    bagAlert = Text(Point(600, 105), "Bag  :  No Alert")
    bagAlert.draw(win)
    # Legend Creation
    legendRec = Rectangle(Point(0,510), Point(800,610))
    legendRec.setFill("grey")
    legendRec.draw(win)
    legendTitle = Text(Point(400, 520), "LEGEND")
    legendTitle.draw(win)
    bagDot = Circle(Point(30, 560), 5)
    bagDot.setFill(color_rgb(0, 255, 0))
    bagDot.draw(win)
    bagText = Text(Point(60, 560), "- Bag")
    bagText.draw(win)
    personWithBagDot = Circle(Point(300, 560), 5)
    personWithBagDot.setFill(color_rgb(0, 0, 255))
    personWithBagDot.draw(win)
    personWithBagText = Text(Point(375, 560), "- Person With Bag")
    personWithBagText.draw(win)
    personWithoutBagDot = Circle(Point(600, 560), 5)
    personWithoutBagDot.setFill(color_rgb(255, 0, 0))
    personWithoutBagDot.draw(win)
    personWithoutBagText = Text(Point(685, 560), "- Person Without Bag")
    personWithoutBagText.draw(win)
    
    
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
object_width_personWithBag = 17 # average width of person with bag
object_width_personWithoutBag = 15 # average width of person without bag

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
    # dis = 0
        #print(len(rects))
    client_num_int = int(client_num)
    deltaX = camera_field_of_view[client_num_int][2] - camera_field_of_view[client_num_int][0]
    deltaY = camera_field_of_view[client_num_int][3] - camera_field_of_view[client_num_int][1]
    rects[0] = rects[0]*deltaX + camera_field_of_view[client_num_int][0]
    rects[1] = rects[1]*deltaY + camera_field_of_view[client_num_int][1]
    rects[2] = rects[2]*deltaX + camera_field_of_view[client_num_int][0]
    rects[3] = rects[3]*deltaY + camera_field_of_view[client_num_int][1] 
    print(f"rects = {rects}")
    pixel_width = rects[2] - rects[0]
    # print(f"pixel_width = {pixel_width}")
    if pixel_width != 0:
        dis = find_distance(pixel_width, classes)
        dis = dis + camera_field_of_view[client_num_int][1]
    else:
        dis = 0
        dis = dis + camera_field_of_view[client_num_int][1]
    # dis.append(dis)
    rects[1] = dis
    rects[2] = dis
    return dis


# create tracks if new tracks are added
def create_track(key, centroid, classes_data):
    # print("creating tracks")
    #live_track = live_track + 1 # incrementing live count
    print(f"class : {classes_data}")
    pt = Point(centroid[0], centroid[1])
    cir = Circle(pt, 5)
    pt1 = Point(centroid[0], centroid[1]+15)
    objectText = Text(pt1, str(key))
    objectText.setSize(16)
    objectText.setStyle("bold")
    objectText.draw(win)
    textCount[key] = objectText
    if classes_data == 1:
        cir.setFill(color_rgb(0, 255, 0))
    elif classes_data == 2:
        cir.setFill(color_rgb(0, 0, 255))
    else:
        cir.setFill(color_rgb(255, 0, 0))
    cir.draw(win)
    objectCount[key] = cir

def delete_track(key):
    objectCount[key].undraw()
    textCount[key].undraw()
    del textCount[key]
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
            textCount[key].move(dx, dy)
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

def accepting_connections():
    # global s
    try:
        print("waiting for connection")
        conn, address = s.accept()
        s.setblocking(1)  # prevents timeout

        all_connections.append(conn)
        all_address.append(address)
        t = threading.Thread(target=work, args=(conn, ) )
        t.daemon = False
        t.start()
        print("Connection has been established :" + address[0])

    except:
        print("Error accepting connections")

def work(clt):
    while True:
        # count_recv = 0
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
                # if count_recv==0:
                #     in_data_classes.put(m)
                #     # print("\nobject:")
                #     # if m==1:
                #     #     print("bag detected")
                #     # elif m==2:
                #     #     print("Person With Bag")
                #     # else:
                #     #     print("Person Without Bag")
                #     count_recv=count_recv+1
                # else:
                #     # print("\nlocation")
                #     # print(m)
                in_data.put(m)
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

def accepting_connections_main_gate():
    try:
        print("waiting for connection from main gate camera")
        conn, address = s.accept()
        s.setblocking(1)  # prevents timeout

        all_connections.append(conn)
        all_address.append(address)
        t = threading.Thread(target=work_main_gate, args=(conn, ) )
        t.daemon = False
        t.start()
        print("Connection has been established :" + address[0])

    except:
        print("Error accepting connections")


def work_main_gate(clt):
    global in_data_face
    while True:
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
                # print(f"received data : {m}")
                # if count_recv==0:
                #     in_data_classes.put(m)
                #     # print("\nobject:")
                #     # if m==1:
                #     #     print("bag detected")
                #     # elif m==2:
                #     #     print("Person With Bag")
                #     # else:
                #     #     print("Person Without Bag")
                #     count_recv=count_recv+1
                # else:
                #     # print("\nlocation")
                #     # print(m)
                in_data_face.put(m)
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

def computeBagAlert(bagKey, clssStack):
    # bagKey is the objectID of bag detected
    distArray = dict()
    distIndex = []
    bagCentroid = objects[bagKey]
    for key in clssStack.keys():
        if clssStack[key] == 3 and key != bagKey:
            # otherCentroid.append(objects[key])
            currentLoc = objects[key]
            dist = math.sqrt(((currentLoc[0] - bagCentroid[0])**2) + ((currentLoc[1] - bagCentroid[1])**2))
            # print(f"distance = {dist}")
            distArray[key] = dist
    
    sortedArray = sorted(distArray.items(), key=lambda x:x[1], reverse = False)
    # print(f"sorted array = {sortedArray}")
    # if sortedArray[0][1] > 20:
    #     # bagAloneAlert
    bagPersonRelation[bagKey] = sortedArray[0][0]
    print(f"bag person relation : {bagPersonRelation}")
    
    # update the UI
    bagAlert.setText("bag + " + str(bagKey) + "mapped to " + str(bagPersonRelation[bagKey]))
    bagAlert.setStyle("bold")
    bagAlert.setFill("red")
    
    # relativeDistance = dist.cdist(np.array(bagCentroid), otherCentroid)
    
    # print(f"relative distance : {relativeDistance}")
    # pass

# loop over the frames from the video stream
crookDetected = 0
alertCounter = 0

def main_work():
    # prev_objects = OrderedDict() 
    global prev_objects
    global in_data_face
    global objects
    global crookDetected
    global alertCounter
    # alertCounter = 0
    # crookDetected = 0
    # creating rects for storing current detected locations
    # print(len(prev_objects))
    rects = []
    temp_classes = []
    if in_data.empty() == False:
        # if condition for checking the no. of elements in the queue is equal to no. of cameras
        # while in_data.qsize() != len(all_connections):
        #     pass
        # print(f"in_data.qsize  =  {in_data.qsize()}  and len of all connections = {len(all_connections)}")
        if in_data.qsize() >= len(all_connections):
            while in_data.empty() == False:    
                current_data = in_data.get()
                # print(f"current data  :  {current_data}")
                # dist has some problem
                # print(f"current location before processing :  {current_data[2:]}")
                temp_location = current_data[2:]
                dist = data_pre_process(current_data[0],current_data[1],temp_location)
                # print(f"current  :  {dist}")
                # print(f"current location after processing :  {temp_location}")
                temp_classes.append(current_data[1])
                rects.append(temp_location)
        
        objects = ct.update(rects, temp_classes)
        clssStack = ct.classes
        print(f"class stack : {clssStack}")
        # to compute distance between bag and nearest person
        for key in clssStack.keys():
            if clssStack[key] == 1:
                computeBagAlert(key, clssStack)
                
        # print(f"class stack : {clssStack}")
        # print(f"crook detected : {crookDetected}")
        if crookDetected == 1:
            alertCounter = alertCounter + 1
        # check crooks
        # print(f"alert counter : {alertCounter}")
        if alertCounter >= 500:
            crookAlert.setText("No Alert")
            crookAlert.setTextColor("black")
            crookAlert.setStyle("normal")
            alertCounter = 0
            crookDetected = 0
        # print(f"Face data : {in_data_face.qsize()}")
        while in_data_face.empty() == False:
            current_data_face = in_data_face.get()
            # print(f"face : {current_data_face[1]}")
            if current_data_face[1] != "None":
                crookAlert.setText(f"Crook : {current_data_face[1]}")
                crookAlert.setTextColor("red")
                crookAlert.setStyle("bold")
                crookDetected = 1
                # put the detected face on UI
                
        # print(f"\nObjects = {objects}")
        # get_data_from_server(rects)
        
        # print(f"main rects = {rects}")
    
        # data pre processing and finding distance
        # dist = data_pre_process(rects,)
        
        # print(f"dist = {dist}")
    
        # objects = ct.update(rects, dist)
    
        # print(f"objects = {objects}")
        # print(f"len(objects)  :  {len(objects)}")
        # print(f"len(prev_objects)  :  {len(prev_objects)}")
        if len(objects) != len(prev_objects):
            for key in objects.keys():
                if not key in prev_objects:
                    # create new tracks
                    # print(f"class : {clssStack[key]}")
                    create_track(key,objects[key],clssStack[key])
    
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
        
        LiveCount.setText(f"Live Count : {len(objectCount)}")
        cameraCount.setText(f"No. of cameras online : {len(all_connections)}")
            


def start_main_thread():
    print("starting main thread")
    t = threading.Thread(target=main_work)
    t.daemon = False
    t.start()

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
# start_main_thread()

# initialize the UI window
initialize_UI()


# create and bind the socket
create_socket()
bind_socket()

# accept client connections
accepting_connections()
accepting_connections()
# for main gate camera
accepting_connections_main_gate()

# change stop_variable in main thread by cheking an input from keyboard
while stop_variable == 0:
    main_work()
    endKey = win.checkKey()
    if endKey == "q":
        stop_variable = 1
    else:
        stop_variable = 0
    # pass
        
        
# do a bit of cleanup
win.close()
# cv2.destroyAllWindows()
# vs.stop()
exit(0)