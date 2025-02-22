# -*- coding: utf-8 -*-
"""
Created on Wed May 27 13:32:31 2020

@author: PRATHITH
"""

# simualtions for client
import socket
import random
import time
import pickle

# establishing connection with server
a = 10
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_ip = "192.168.0.104"
server_port = 9999

print("Waiting for server")
s.connect((server_ip, server_port))


# print(random())
# start at some value and keep incrementing till end of frame
client_number = 1
classes_detected = 3
current_location = [client_number, classes_detected, 0.36, 0, 0.84, 0]


incremental_list = [0.05, 0.01, 0.06, 0.04, 0.02, 0.06]
while True:
    # transmit current location
    # mymsg_classes = pickle.dumps(classes_detected)
    # mymsg_classes = bytes(f'{len(mymsg_classes):<{a}}', "utf-8")+mymsg_classes
    # # print(f"len of mymsg_classes : {len(mymsg_classes)}")
    # s.send(mymsg_classes)
    # time.sleep(0.1)
    mymsg_boxes = pickle.dumps(current_location)
    mymsg_boxes = bytes(f'{len(mymsg_boxes):<{a}}', "utf-8")+mymsg_boxes
    # print(f" mymsg_boxes : {mymsg_boxes[:a]}")
    s.send(mymsg_boxes)
    mymsg_boxes = None
    # mymsg_classes = No    
    # processing delay
    time.sleep(2)    
    # update the current_location
    temp_number = random.randint(0,5)
    current_location[2] = current_location[2] + incremental_list[temp_number]
    current_location[4] = current_location[4] + incremental_list[temp_number]
    if (current_location[2] > 1) or (current_location[4] > 1):
        current_location = [client_number, classes_detected, 0.36, 0, 0.84, 0] 
        
    # print the current location
    print(current_location)