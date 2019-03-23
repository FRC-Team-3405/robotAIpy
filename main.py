#!/usr/bin/env python3
import numpy 
import time 
import threading, multiprocessing
import cv2
from networktables import NetworkTables
import cscore 

active = True
camera1 = cv2.VideoCapture(0)
#camera2 = cv2.VideoCapture("http://axis-camera.local")
ballx, bally, ballw, ballh, ballarea = 0,0,0,0,0
reflectorx, reflectory, reflectorw, reflectorh, reflectorarea = 0,0,0,0,0
ballfound = False
reflectorfound = False
NetworkTables.initialize(server='roborio-3405-frc.local')
table = NetworkTables.getTable('SmartDashboard')
cs = cscore.CameraServer.getInstance()
videoout1 = cs.putVideo('camera1', 640, 480)
videoout2 = cs.putVideo('camera2', 640, 480)
shadeout1 = cs.putVideo('mask1', 180, 135)
shadeout1 = cs.putVideo('mask2', 180, 135)
size = (1920, 1080)
def getkey(item):
    item[4]

def outputvideo():
    while active:
        ret1, frame1 = camera1.read()
        ret2=False
        #ret2, frame2 = camera2.read()
        if ret1:
            frame1 = cv2.resize(frame1, (320, 240))
            videoout1.putFrame(frame1)
        if ret2:
            frame2 = cv2.resize(frame2, (320, 240))
            videoout2.putFrame(frame2)  

    time.sleep(.03)
def updater():
    while active:
        table.putNumber('ballx', ballx - size[0]/2)
        table.putNumber('bally', bally - size[1]/2)
        table.putNumber('ballw', ballw)
        table.putNumber('ballh', ballh)
        table.putNumber('ballarea', ballarea)
        table.putBoolean('ballfound', ballfound)
        table.putNumber('reflectorx', reflectorx - size[0]/2)
        table.putNumber('reflectory', reflectory - size[1]/2)
        table.putNumber('reflectorw', reflectorw)
        table.putNumber('reflectorh', reflectorh)
        table.putNumber('reflectorarea', reflectorarea)
        table.putBoolean('reflectorfound', reflectorfound)
    time.sleep(.03)
#game piece offset
def gamePieceOffset(camera):
    upmask = numpy.array([20, 125, 255])
    downmask = numpy.array([0, 50, 150])
    
    ret, frame = camera.read()

    if ret == False:
        return [False]
    
    frame = cv2.resize(frame, size)
    
    mask = cv2.inRange(frame, downmask, upmask)
    mask1 = cv2.resize(mask, (180, 135))
    shadeout1.putFrame(mask1)
    
    rand1, contours, rand2 = cv2.findContours(mask, mode=cv2.RETR_LIST, method=cv2.CHAIN_APPROX_SIMPLE)

    if len(contours) > 0:
        contours.sort(key=lambda contour: cv2.contourArea(contour))
        ballx, bally, ballw, ballh = cv2.boundingRect(contours[0])
        ballarea = cv2.contourArea(contours[0])
        return [True, ballx, bally, ballw, ballh, ballarea]
    else:
        return [False]

#hatch panel tape offset
def reflectorFinder(camera):
    upmask = numpy.array([102, 255, 255])
    downmask = numpy.array([73, 161, 138])
    
    ret, frame = camera.read()
    
    if ret == False:
        return [False]
    
    frame = cv2.resize(frame, size)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(hsv, downmask, upmask)
    mask1 = cv2.resize(mask, (180, 135))
    shadeout2.putFrame(mask1)
    rand3, contours, rand4 = cv2.findContours(mask, mode=cv2.RETR_LIST, method=cv2.CHAIN_APPROX_SIMPLE)
    
    goodcontours = []
    for contour in contours:
        #variables
        x, y, w, h = cv2.boundingRect(contour)
        area = cv2.contourArea(contour)
        ratio = float(w/h)
        #test
        if (area > 20 and ratio < .7):
            goodcontours.append([x, y, w, h, area])
        
    goodcontours.sort(key=getkey)

    if len(goodcontours) > 1:
        reflectorx = (goodcontours[0][0] + goodcontours[1][0])/2
        reflectory = (goodcontours[0][1] + goodcontours[1][1]) 
        reflectorw, reflectorh, reflectorarea = goodcontours[0][2:]
        return [True, reflectorx, reflectory, reflectorw, reflectorh, reflectorarea]
    else:
        return [False]

#init

updaterthread = threading.Thread(target=updater, name="updater")
updaterthread.start()

outputvideothread = threading.Thread(target=outputvideo, name="outputvideo")
outputvideothread.start()

while active:
    ball = gamePieceOffset(camera1)
    #reflector = reflectorFinder(camera2)

    if ball[0] == True:
        ballx, bally, ballw, ballh, ballarea = ball[1:]
        ballfound = True
    else:
        ballfound = False

    '''if reflector[0] == True:
        reflectorx, reflectory, reflectorw, reflectorh, reflectorarea = reflector[1:]
        reflectorfound = True
    else:
        reflectorfound = False'''
    time.sleep(1)
