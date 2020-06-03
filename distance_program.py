import cv2
import cv2
import time
import numpy as np
import imutils
cascPath = "C:/Users/PRATHITH/Anaconda3/Library/etc/haarcascades/haarcascade_frontalface_default.xml"
faceCascade = cv2.CascadeClassifier(cascPath)
focal=399.0
face_width = 9
runLoop = True;
numPts = 0;
frameCount = 0
frameCount1=0
#start the camera
video_capture = cv2.VideoCapture(1)
time.sleep(0.1)
ret, frame = video_capture.read()
def distance (face_width,focalLength,mark):
    frameCount=0
    while frameCount<20 :
	# load the image, find the marker in the image, then compute the
	# distance to the marker from the camera
        frameCount=frameCount+1
        return (face_width* focalLength*2.54)/ mark
while runLoop & frameCount1<20:
    frameCount1=frameCount1+1
    ret, frame = video_capture.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    if int(cv2.__version__.split('.')[0]) >= 3:
            cv_flag = cv2.CASCADE_SCALE_IMAGE
    else:
            cv_flag = cv2.cv.CV_HAAR_SCALE_IMAGE

    faces = faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            flags=cv_flag
        )
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5,5), 0)
        edged = cv2.Canny(gray,100,200)
        cnts = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        c = max(cnts, key = cv2.contourArea)
	# compute the bounding box of the of the paper region and return it
        marker= cv2.minAreaRect(c)
        #print(marker)
        #focalLength = (  marker[1][0] * focal) /  face_width
        inches=distance(face_width,focal,marker[1][0]);
            
       
        cv2.putText(frame, "distance: {}".format(inches), (20,20), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0,255,255), 1, cv2.LINE_AA)

    cv2.imshow('Video', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
     
    
video_capture.release()
cv2.destroyAllWindows()
