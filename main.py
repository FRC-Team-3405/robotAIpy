#!/usr/bin/env python3
import numpy 
import time 
import threading
import cv2
from networktables import NetworkTables
import cscore 

active = True
camera1 = cv2.VideoCapture(0)
camera2 = cv2.VideoCapture("http://axis-camera.local")
ballx, bally, ballw, ballh, ballarea = 0,0,0,0
reflectorx, reflectory, reflectorw, relfectorh, reflectorarea = 0,0,0,0
ballfound = False
reflectorfound = False
NetworkTables.initialize(server='roborio-3405-frc.local')
table = NetworkTables.getTable('SmartDashboard')
cs = cscore.CameraServer.getInstance()
videoout1 = cs.putVideo('camera1', 640, 480)
videoout2 = cs.putVideo('camera2', 640, 480)

def outputvideo():
    ret1, frame1 = camera1.read()
    ret2, frame2 = camera2.read()
    if ret1:
        videoout1.putFrame(frame1)
    if ret2:
        videoout2.putFrame(frame2)  

#listner for network table
def updater():
    while active:
        #if table.getBoolean('tick', False) == True:
        table.putBoolean('tick', False)
        table.putNumber('ballx', ballx)
        table.putNumber('bally', bally)
        table.putNumber('ballw', ballw)
        table.putNumber('ballh', ballh)
        table.putNumber('ballarea', ballarea)
        table.putBoolean('ballfound', ballfound)
        table.putNumber('reflectorx', reflectorx)
        table.putNumber('reflectory', reflectory)
        table.putNumber('reflectorw', reflectorw)
        table.putNumber('reflectorh', reflectorh)
        table.putNumber('reflectorarea', reflectorarea)
        table.putBoolean('reflectorfound', reflectorfound)
        outputvideo()
        time.sleep(.05)

#game piece offset
def gamePieceOffset(camera, type):
    upmask = numpy.array([20, 125, 255])
    downmask = numpy.array([0, 50, 150])
    
    ret, frame = camera.read()

    if ret == False:
        return False
    
    mask = cv2.inRange(frame, downmask, upmask)

    None, countours, None = cv2.findContours(mask, mode=cv2.RETR_LIST, method=cv2.CHAIN_APPROX_SIMPLE)

    if not contours == None:
        contours.sort(key=lambda contour: cv2.contourArea(contour))
        ballx, bally, ballw, ballh = cv2.boundingRect(countours[0])
        ballarea = cv2.contourArea
        return True
    else:
        return False

#hatch panel tape offset
def reflectorFinder(camera):
    upmask = numpy.array([102, 255, 255])
    downmask = numpy.array([73, 161, 138])
    
    ret, frame = camera.read()
    
    if ret == False:
        return False
    
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(hsv, downmask, upmask)

    None, contours, None = cv2.findContours(mask, mode=cv2.RETR_LIST, method=cv2.CHAIN_APPROX_SIMPLE)
    
    goodcontours = []
    for contour in contours:
        #variables
        x, y, w, h = cv2.boundingRect(contour)
        area = cv2.contourArea(contour)
        ratio = float(w/h)
        #test
        if (area > 20 and ratio < .7):
            goodcontours.append([x, y, w, h, area])
        
    goodcontours.sort(key=lambda contour: contour[5])
`   
    if len(goodcontours) > 0:
        reflectorx, reflectory, reflectorw, reflectorh, reflectorarea = goodcontours[0]
        return True
    else:
        return False

#init

updaterthread = threading.Thread(target=updater, name="updater")
updaterthread.start()

while active:
    ballfound = gamePieceOffset(camera)
    reflectorfound = reflectorFinder(camera)
    time.sleep(.05)


camera.release()
cv2.destroyAllWindows()