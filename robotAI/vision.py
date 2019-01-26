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
    cv2.imshow('stuff', frame)
    for index, x in numpy.ndenumerate(smallmask):
        if x > threshold:
            result = result + index[1] - width/2
    
    return result
            
