import cv2
import numpy
def gamePieceOffset(camera, type, threshold):
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
        if x > threshold:
            result = result + index[1] - width/2
    
    return result
            
def reflectorFinder(camera):
    upmask = numpy.array([102, 255, 255])
    downmask = numpy.array([73, 161, 138])
    
    ret, frame = camera.read()
    if ret == False:
        return False
    bgr = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(bgr, downmask, upmask)

    contours, hirearchy = cv2.findContours(mask, mode=cv2.RETR_LIST, method=cv2.CHAIN_APPROX_SIMPLE)

    goodContours = []
    specs = []
    for contour in contours:
        #variables
        x, y, w, h = cv2.boundingRect(contour)
        area = cv2.contourArea(contour)
        ratio = float(w/h)
        #test
        if (area > 20 and ratio < .7):
            goodContours.append(cv2.convexHull(contour))
            specs.append([x, y, w, h])
    
    if goodContours == []:
        cv2.imshow('contour', frame)
        cv2.imshow('mask', mask)
        return False
    else:
        showimage = cv2.drawContours(frame, goodContours, -1, (0,0,255),3)
        cv2.imshow('contour', showimage)
        cv2.imshow('mask', mask)
        return goodContours, specs


