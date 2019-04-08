
import cv2
import cv2.aruco as aruco
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import cm
import sys
import time


if len(sys.argv) == 1:
    out_type = 'avi'
    codec = 'MJPG'
else:
    out_type = sys.argv[1]
    codec = sys.argv[2]

screen_cap = cv2.VideoCapture(0)

ret0, frame0 = screen_cap.read()
gray0 = cv2.cvtColor(frame0, cv2.COLOR_BGR2GRAY)

kernel = np.ones((5,5),np.float32)/25

fshape = frame0.shape
h,w = fshape[0],fshape[1]

fps = screen_cap.get(cv2.CAP_PROP_FPS)
print(fps)

fourcc = cv2.VideoWriter_fourcc(*codec)
out = cv2.VideoWriter('output.'+ out_type,fourcc, fps, (w,h))
#out = cv2.VideoWriter('output.'+ out_type,-1, 20.0, (640,480))

time_start = time.time()
current_time = time.time()
record_time = 5
count = 0
while current_time - time_start < record_time:
    ret1, frame1 = screen_cap.read()
    #frame = cv2.imread('tags.png')
    if ret1 == True:
        gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    else:
        continue
    dst = cv2.filter2D(gray1,-1,kernel)

    dif = cv2.absdiff(gray1,gray0)
    #dif = gray1 - gray0
    #pdb.set_trace()
    dif = np.abs(dif)
    dif[dif < 5] = 0
    
    dif_color = cv2.cvtColor(dif,cv2.COLOR_GRAY2BGR)
    out.write(dif_color)
    motion = str(np.round(np.log(np.sum(dif)),2))
    cv2.putText(dif,motion,(10,450),cv2.FONT_HERSHEY_SIMPLEX,1,255)
    #cv2.imshow('Motion',dif)
    #cv2.imshow('Original',frame1)
    if cv2.waitKey(100) & 0xFF == ord('q'):
        break
    gray0 = np.copy(gray1)
    count += 1
    current_time = time.time()

real_fps = count / record_time
print(real_fps)

screen_cap.release()
out.release()
cv2.destroyAllWindows()

print('Did I do it?')
