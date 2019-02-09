#!/usr/bin/env python3
import numpy 
import time 
import threading
import cv2
from networktables import NetworkTables
import cscore 

active = True
camera = cv2.VideoCapture(0)
setupframe = camera.read()
balloffset = 0
balldistance = 0
paneloffset = 0
paneldistance = 0
NetworkTables.initialize(server='roborio-3405-frc.local')
table = NetworkTables.getTable('SmartDashboard')
cameraserver = cscore.CameraServer.putVideo('camera1', len(setupframe[1]), len(setupframe))

#listner for network table
def listener():
    while active:
        if table.getBoolean('tick', False) == True:
            table.putBoolean('tick', False)
            table.putNumber('balloffset', balloffset)
            table.putNumber('balldistance', balldistance)
            table.putNumber('paneloffset', paneloffset)
            table.putNumber('paneldistance', paneldistance)
        time.sleep(.05)

#game piece offset
def gamePieceOffset(camera, type):
    result = 0
    if type == "ball":
        upmask = numpy.array([20, 125, 255])
        downmask = numpy.array([0, 50, 150])
    elif type == "panel":
        upmask = numpy.array([100 ,255, 255])
        downmask = numpy.array([0 ,150 ,150])
    else:
        return False
    
    ret, frame = camera.read()
    if ret == False:
        return False
    
    mask = cv2.inRange(frame, downmask, upmask)
    smallmask = cv2.resize(mask, (0,0), fx=.1, fy=.1, interpolation=cv2.INTER_LINEAR)
    width = len(smallmask[0])

    for index, x in numpy.ndenumerate(smallmask):
        if x > 120:
            result = result + index[1] - width/2
    
    return result

#hatch panel tape offset
def reflectorFinder(camera):
    upmask = numpy.array([102, 255, 255])
    downmask = numpy.array([73, 161, 138])
    
    ret, frame = camera.read()
    if ret == False:
        return False
    bgr = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(bgr, downmask, upmask)

    stuff, contours, hirearchy = cv2.findContours(mask, mode=cv2.RETR_LIST, method=cv2.CHAIN_APPROX_SIMPLE)

    goodContours = []
    specs = []
    offset = 0
    for contour in contours:
        #variables
        x, y, w, h = cv2.boundingRect(contour)
        area = cv2.contourArea(contour)
        ratio = float(w/h)
        #test
        if (area > 20 and ratio < .7):
            goodContours.append(cv2.convexHull(contour))
            specs.append([x, y, w, h])
            offset = offset + (contour[0] - len(mask[1]))
    
    return offset

#init

listenerthread = threading.Thread(target=listener, name="listner")
listenerthread.start()

while active:
    balloffset = gamePieceOffset(camera, "ball")
    paneloffset = reflectorFinder(camera)
    cameraserver.putFrame(camera.read())
    time.sleep(.05)


camera.release()
cv2.destroyAllWindows()