# Camera Calibration program

# Last edited : @prathithv 06/04/2020, 13:14

# Run this program before setting the camera field of view in the object_tracker.py program
# this program asks to click on the GUI to get the coordinates for the camera field of view
# to be used only when calibration
# Parameters Changeable:
# img               : background map image (should be of .gif type only)
# WINDOW_WIDTH      : Width the main GUI window
# WINDOW HEIGHT     : Height of the main GUI window

# Make sure graphics.py is present in the same floder as this file
from graphics import *
import time

# UI Window creation and adding map (should only be of .gif type)
# width and height of GUI Window
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

win = GraphWin("My Window", WINDOW_WIDTH, WINDOW_HEIGHT)
win.setBackground('black')
img = Image(Point(WINDOW_WIDTH/2, WINDOW_HEIGHT/2), "bengaluru_airport.gif")
img.draw(win)

pointCount = 0
coordinates_needed = 4


while pointCount < coordinates_needed:
    print(f"click on the GUI for point  {pointCount+1} :")
    clickPoint = win.getMouse()
    print(clickPoint)
    pointCount += 1
    keyString = win.checkKey()
    if keyString == "q":
        break

win.close()