import cv2
import numpy
import vision

active = True
camera = cv2.VideoCapture(0)

while active:
    if cv2.waitKey(1) == ord('q'):
        active = False
    
    print(vision.reflectorFinder(camera))

camera.release()
cv2.destroyAllWindows()