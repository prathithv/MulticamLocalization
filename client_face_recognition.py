# -*- coding: utf-8 -*-
"""
Created on Wed May 27 15:01:38 2020

@author: PRATHITH
"""

# simualtions for client with face recognition
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

# client number
client_number = 2

data_none = "None"
data_face = "Prathith"

current_data = [client_number, data_none]

crook = 0

while True:
    if crook >= 10:
        current_data = [client_number, data_face]
        print(current_data)
        mymsg = pickle.dumps(current_data)
        mymsg = bytes(f'{len(mymsg):<{a}}', "utf-8")+mymsg
        s.send(mymsg)
        mymsg = None
        time.sleep(3)
        crook = crook + 1
        if crook >= 20:
            crook = 0
    else:
        current_data = [client_number, data_none]
        print(current_data)
        mymsg = pickle.dumps(current_data)
        mymsg = bytes(f'{len(mymsg):<{a}}', "utf-8")+mymsg
        s.send(mymsg)
        mymsg = None
        time.sleep(3)
        crook = crook + 1