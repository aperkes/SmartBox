#! /usr/bin/env python

## Code to run playback experiments 
## For use it Marc Schmidt's lab
## Made April, 2019 by Ammon Perkes
## Contact perkes.ammon@gmail.com for questions

import numpy as np
import cv2
import time
import pdb

#web_cam_ids = 
motion_threshold = 12
bird_threshold = 3
codec = 'MJPG'
out_type = '.avi'
duration = 60
n_cameras = 4
n_cages = 4

## Dictionary of the locations of cages in each camera. This will actually be procedurally generated using tags
window_dict = {
    0: [(slice(0,100),slice(0,100))],
    1: [(slice(100,200),slice(0,100))],
    2: [(slice(0,100),slice(100,200))],
    3: [(slice(100,200),slice(100,200))]}
## Indexed array relating actual cages to their location within cameras. 
cage_indices = np.array([[0],[1],[2],[3]])

def load_cameras():
## Make sure they get the correct cameras in the correct order, and that they're all there...
## The best way to assign cameras to specific places might be to use the markers...
    global h,w
    caps = [0] * n_cameras
    rets = [0] * n_cameras
    for c in range(n_cameras):
        caps[c] = cv2.VideoCapture(c)

    ret,frame = caps[0].read()
    fshape = frame.shape
    h,w = fshape[0],fshape[1]
    return caps

def check_cameras():
## Check fps, consistency, etc
    global h, w, fps
    cap = caps[0]
    fps = cap.get(cv2.CAP_PROP_FPS)
    ret,frame = cap.read()
    fshape = frame0.shape
    h,w = fshape[0],fshape[1]
    return h,w,fps


def locate_markers():
    pass
    return locations

## Based on markers, figure out which cage is which
def define_cages():
    return cage_indices


## Wait until cowbirds are calm, once it is, return True
# If they never calm down, return false, and decide what to do. 
def monitor_cameras(caps,visual = False):
    global n_cameras, window_dict, cage_indices, h, w
    counts = 100
    success = False
    current_frames = np.empty([n_cameras,h,w])
    previous_frames = np.empty_like(current_frames)
    rets = [0] * n_cameras
    cage_motion = np.empty([counts,n_cages])
    bool_motion = np.ones([counts,n_cages])
## Make sure you get a good starting frame
    for c in range(n_cameras):
        while rets[c] == False:
            rets[c], color_frame = caps[c].read()
            current_frames[c] = cv2.cvtColor(color_frame,cv2.COLOR_BGR2GRAY)
    previous_frames = np.copy(current_frames)
## Until it exhausts its check time or is successful, within each camera, within each designated cage, check for motion
    end_time = time.time() + duration
    count = 0
    while time.time() < end_time and success == False:
# first read each camera, then compare
        for c in range(n_cameras):
            rets[c], color_frame = caps[c].read()
        for c in range(n_cameras):
            if rets[c] == False:
                continue
            current_frames[c] = cv2.cvtColor(color_frame,cv2.COLOR_BGR2GRAY)
            windows = window_dict[c]
            for w in range(len(windows)):
                w_pixels = windows[w]
                dif = cv2.absdiff(current_frames[c][w_pixels],previous_frames[c][w_pixels])
                dif[dif < 10] = 0
                cage_index = cage_indices[c,w]
## Save both the amount of motion, and a boolean of whether it's above the threshold. 
                log_sum = np.log(np.sum(dif))
                cage_motion[count,cage_index] = log_sum
                if log_sum < motion_threshold:
                    bool_motion[count,cage_index] = False
                if visual:
                    cv2.putText(dif,str(np.round(log_sum,2)),(5,5),cv2.FONT_HERSHEY_SIMPLEX,.5,255)
                    cv2.imshow(str(cage_index),dif)
        sum_bools = np.sum(bool_motion,1)
        if max(sum_bools) <= n_cages - bird_threshold:
            success = True 
        if cv2.waitKey(100) & 0xFF == ord('q'):
            break
        count = (count + 1) % counts
        previous_frames = np.copy(current_frames)
    monitor_time = duration - time.time() - end_time ## probably should have just tracked start time...
    #pdb.set_trace()
    return success, cage_motion, monitor_time         


def select_song():
    pass

def record_clip():
    global codec, cam_dict, n_cameras, fps, w,h
    fourcc = cv2.VideoWriter_fourcc(*codec)
    for c in range(n_cameras):
        out_file = out_root + cam_dict[c]
        writers[c] = cv2.VideoWriter(out_file,fourcc,fps, (w,h))

    start_time = time.time()
    end_time = start_time + duration

    while time.time() < end_time:
        for c in range(n_cameras):
            ret, frame = caps[c].read()
            if STIMULUS:
                frame = add_marker(frame,c)
            writers[c].write(frame)

def record_sound():
    pass

def play_song():
    #while playing, add visual annotation of the signal to the phrames. (a box in corners) 
    pass

def add_marker():
    pass
    return marked_frame

def save_clip(): 
    ## Only needed if record_clip can't function properly
    pass

def unload_cameras(caps):
    for cap in caps:
        cap.release()
    cv2.destroyAllWindows()

def check_outcome():
    real_fps = frame_count / record_time

def update_log():
    pass

if __name__ == "__main__":
    caps = load_cameras()
    success, cage_motion,monitor_time = monitor_cameras(caps,visual=True)
    unload_cameras(caps)
    print(success)
