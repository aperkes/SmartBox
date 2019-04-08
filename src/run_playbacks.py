#! /usr/bin/env python

## Code to run playback experiments 
## For use it Marc Schmidt's lab
## Made April, 2019 by Ammon Perkes
## Contact perkes.ammon@gmail.com for questions

import numpy as np
import cv2
import cv2.aruco as aruco
import os, glob
import time, datetime
import pdb
import threading, queue 
import pyaudio, wave
from subprocess import Popen
import pandas as pd

motion_threshold = 10
cage_motion = 10
frame_motion = 12

bird_threshold = 7
codec = 'MJPG'
out_type = '.avi'
monitor_duration = 60
record_duration = 10
song_delay = 2
n_cameras = 4
n_cages = 4
PLAYING = False

log_dict = {
    'Playback':False}
parent_dir = '/home/ammon/Documents/Scripts/SmartBox/'
video_dir = parent_dir + 'Recordings/'
log_dir = parent_dir + 'Logs/'
song_directory = parent_dir + 'Songs/'
log_file = log_dir + 'current_log.txt'
song_log = log_dir + 'playback_log.csv'
## Dictionary of the locations of cages in each camera. This will actually be procedurally generated using tags

## Default window dict, basically each camera tracks the entire camera
MONITOR_CAGES = False
default_window_dict = {
    0: [0,(slice(0,-1),slice(0,-1))],
    1: [1,(slice(0,-1),slice(0,-1))],
    2: [2,(slice(0,-1),slice(0,-1))],
    3: [3,(slice(0,-1),slice(0,-1))]}
window_dict = dict(default_window_dict)
## Indexed array relating actual cages to their location within cameras. 

cage_indices = np.array([[0],[1],[2],[3]])

## Dictionary of identities of each camera. This will also be set using tags, might be unnecessary
camera_dict = {
    0: 'cam0',
    1: 'cam1',
    2: 'cam2',
    3: 'cam3'}

def load_cameras():
## Make sure they get the correct cameras in the correct order, and that they're all there...
## The best way to assign cameras to specific places might be to use the markers...
    global h,w, fps
    caps = [0] * n_cameras
    rets = [0] * n_cameras
    for c in range(n_cameras):
        caps[c] = cv2.VideoCapture(c)

    ret,frame = caps[0].read()
    fps = caps[0].get(cv2.CAP_PROP_FPS)
    fshape = frame.shape
    h,w = fshape[0],fshape[1]
    return caps

def check_cameras(caps):
## Check fps, consistency, etc
    global h, w, fps
    cap = caps[0]
    fps = cap.get(cv2.CAP_PROP_FPS)
    ret,frame = cap.read()
    fshape = frame.shape
    h,w = fshape[0],fshape[1]
    return h,w,fps

## Find markers, and define cameras (eventually...)
def locate_markers(caps, visual = False):
    global MONITOR_CAGES, n_cages
    success_array = np.array([
        [1,1,1,0, 1,0,1,0, 0,0,0,0],
        [0,1,1,1, 0,1,0,1, 0,0,0,0],
        [0,0,0,0, 1,0,1,0, 1,1,1,0],
        [0,0,0,0, 0,1,0,1, 0,1,1,1]])

    complete = False
    n_markers = 12
    corner_array = np.zeros([n_cameras,n_markers,2])
    aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_250)
    parameters = aruco.DetectorParameters_create()
    count = 0
    cutoff = 100
    while complete == False and count < cutoff:
        for c in range(len(caps)):
            ret, frame = caps[c].read()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)
            if len(corners) == 0:
                if visual:
                    cv2.imshow(str(c),frame)
                    if cv2.waitKey(100) & 0xFF == ord('q'):
                        break
                continue
            frame_markers = aruco.drawDetectedMarkers(frame.copy(), corners, ids)
            if visual:
                cv2.imshow(str(c),frame_markers)
                if cv2.waitKey(100) & 0xFF == ord('q'):
                    break
            for i in ids:
                tag_id = i[0] - 1
                if tag_id > 11:
                    ## incorrect tag found...
                    continue
                corner_index = np.where(ids == i)[0][0]
                first_corner = tuple(corners[corner_index][0][0])
                camera = c
                if corner_array[c,tag_id,0] != 0:
                    continue
                else:
                    corner_array[c,tag_id] = first_corner
## Once you have a value for every expected marker for each camera, you're done.
        if count == cutoff // 2:
            camera_order, corner_array = get_order(corner_array)
            #pdb.set_trace()
            caps = [caps[int(x)] for x in camera_order] 
        test_array = (corner_array[:,:,0] != 0)
        if np.array_equal(test_array,success_array):
            complete = True 
            MONITOR_CAGES = True
            n_cages = 9
            print('Success!!')

        else:
            count +=1
    log_dict['Markers'] = complete
    return complete, caps, corner_array

def get_order(corner_array):
    global n_cages, MONITOR_CAGES
## Find which camera has unique indices so that I can have everything ordered nicely
## This might be a bit overkill...and I'll need to make sure all this works. 
    #camera 0 : where corner_array[?,0] != 00 
    #camera 1: where corner_array[?,3] != 00
    #camera 2: where corner_array[?,8] != 00
    #camera 3: where corner_array[?,11] != 00
    cam0_index = np.where(corner_array[:,0,0] != 0)[0]
    cam1_index = np.where(corner_array[:,3,0] != 0)[0]
    cam2_index = np.where(corner_array[:,8,0] != 0)[0]
    cam3_index = np.where(corner_array[:,11,0] != 0)[0]
    camera_order = [cam0_index,cam1_index,cam2_index,cam3_index]
    for c in camera_order:
        if len(c) > 1 or len(c) == 0:
            print(camera_order)
            MONITOR_CAGES = False
            camera_order = np.array([0,1,2,3])
            n_cages == 4

            return camera_order, corner_array
        else:
            continue
    camera_order = np.array([int(cam0_index),int(cam1_index),int(cam2_index),int(cam3_index)])
    #MONITOR_CAGES = True
    #pdb.set_trace()
    corner_array = corner_array[camera_order]
## If this works, set n_cages to 9. 
    #n_cages = 9
    return camera_order, corner_array
     
## Based on markers, figure out which cage is which
def define_cages(corner_array):
    global default_window_dict, window_dict, camera_dict, n_cages
## If it hasn't found all the tags correctly this will break
    if MONITOR_CAGES == False:
        print('Setting to default monitors (monitor all)')
        window_dict = default_window_dict
        n_cages = 4
        return window_dict
    else:
        pass
    camera_order,corner_array = get_order(corner_array)

## Buckle up, things are about to get notation heavy
## It might be better to just use the corner array notation, but I this was a little easier to wrap my head around. 
## Check out 'corner_notation.png' for a handy reference for all this. 
    cam0_x0,cam0_y0 = corner_array[0,0]
    cam0_x1,cam0_x2 = corner_array[0,1,0],corner_array[0,2,0]
    cam0_y4 = corner_array[0,4,1]

    cam1_x2 = corner_array[1,2,0]
    cam1_x3,cam1_y3 = corner_array[1,3]
    cam1_y5 = corner_array[1,5,1]

    cam2_x8,cam2_y8 = corner_array[2,8]
    cam2_x9,cam2_x10 = corner_array[2,9,0], corner_array[2,10,0]
    cam2_y4, cam2_y6 = corner_array[2,4,1], corner_array[2,6,1]

    cam3_x10 = corner_array[3,10,0]
    cam3_x11, cam3_y11 = corner_array[3,11]
    cam3_y5, cam3_y7 = corner_array[3,5,1],corner_array[3,7,1]
    
    cam0_col0, cam0_col1 = slice(int(cam0_x0),int(cam0_x1)), slice(int(cam0_x1),int(cam0_x2))
    cam0_row0 = slice(int(cam0_y0),int(cam0_y4))

    cam1_col2 = slice(int(cam1_x2),int(cam1_x3))
    cam1_row0 = slice(int(cam1_y3),int(cam1_y5))

    cam2_col0,cam2_col1 = slice(int(cam2_x8),int(cam2_x9)),slice(int(cam2_x9),int(cam2_x10))
    cam2_row1, cam2_row2 = slice(int(cam2_y4),int(cam2_y6)),slice(int(cam2_y6),int(cam2_y8))

    cam3_col2 = slice(int(cam3_x10),int(cam3_x11))
    cam3_row1,cam3_row2 = slice(int(cam3_y5),int(cam3_y7)),slice(int(cam3_y7),int(cam3_y11))

    window_dict = {
        0: [0, (cam0_row0, cam0_col0)],
        1: [0, (cam0_row0, cam0_col1)],
        2: [1, (cam1_row0, cam1_col2)],
        3: [2, (cam2_row1, cam2_col0)],
        4: [2, (cam2_row1, cam2_col1)],
        5: [3, (cam3_row1, cam3_col2)],
        6: [2, (cam2_row2, cam2_col0)],
        7: [2, (cam2_row2, cam2_col1)],
        8: [3, (cam3_row2, cam3_col2)]}
    return window_dict

def diagnostics(caps):
## Function that should check the cameras and return where
# Cameras are all working
# Whether the tags have been located successfully
# Related to that, what the threshold should be
    pass
    """ 
The two big conditions I imagine here are: 
a) cameras are all working, tags have all been found and everything looks great
b) cameras are all working, tags are found, but there's some overlap, so I'm not sure which camera is which
....b) I could get a sense based on which is further over, but that's probably not worth it.
c) cameras are all working, but tags weren't found successfully
d) cameras aren't working

In the case of b/c, I should be looking for total movement, 
in the case of d, I should probably shut down and send some sort of a warning message.
    return condition
    """

## Wait until cowbirds are calm, once it is, return True
# If they never calm down, return false, and decide what to do. 
def monitor_cameras(caps,visual = False):
    global n_cameras, n_cages, window_dict, cage_indices, monitor_duration, h, w, log_dict
    global motion_threshold, bird_threshold
## This is a little hacky, but if there are only 4 "cages" bird_threshold has to change accordingly. 
    if not MONITOR_CAGES:
        motion_threshold = frame_motion 
        bird_threshold = 3
## Currently, how long they must be quiet is determined by counts 
## as well as the sleep time between each count. 
## If they should be still for 1 minutes, you want counts * wait == 60,000
    counts = 100
    wait_time = 60
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
    #end_time = time.time() + monitor_duration
    end_time = time.time() + 60
    count = 0
    while time.time() < end_time and success == False:
    #while True:
# first read each camera, then compare
        for c in range(n_cameras):
            rets[c], color_frame = caps[c].read()
        #for c in range(n_cameras):
            if rets[c] == False:
                continue
            current_frames[c] = cv2.cvtColor(color_frame,cv2.COLOR_BGR2GRAY)
## I could use window_dict as a fail safe, and just convert it in the case that the cages aren't found. 
##NOTE: This means I need to set n_cages to 4 if I can't locate the cages
            for cage_index in range(n_cages):
                win = window_dict[cage_index]
                if win[0] != c:
                    #print('skipped ' + str(c))
                    continue
                w_pixels = win[1]
                #pdb.set_trace()
                dif = cv2.absdiff(current_frames[c][w_pixels],previous_frames[c][w_pixels])
                
                dif[dif < 10] = 0
## Save both the amount of motion, and a boolean of whether it's above the threshold. 
                log_sum = np.log(np.sum(dif))
                cage_motion[count,cage_index] = log_sum
                if log_sum < motion_threshold:
                    bool_motion[count,cage_index] = False
                if visual:
                    cv2.putText(dif,str(np.round(log_sum,2)),(5,15),cv2.FONT_HERSHEY_SIMPLEX,.5,255)
                    cv2.imshow('cam:' + str(c) + 'cage:' + str(cage_index),dif)
                    #cv2.imshow('cam:' + str(c) + 'cage:' + str(cage_index),current_frames[c][w_pixels])
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
        sum_bools = np.sum(bool_motion,1)
        cv2.waitKey(wait_time)
        if max(sum_bools) <= n_cages - bird_threshold:
            pass
            print('success!!!')
            success = True 
            print(sum_bools)
        count = (count + 1) % counts
        previous_frames = np.copy(current_frames)
    required_time = monitor_duration - time.time() - end_time ## probably should have just tracked start time...
    cv2.destroyAllWindows()
    #pdb.set_trace()
    print(bool_motion)
    log_dict['BoolMotion'] = np.sum(bool_motion,0)
    log_dict['Motion'] = np.sum(cage_motion,0)
    return success, cage_motion, required_time         

def record_AV(caps, mic = None, stimulus = True):
    q = queue.Queue()
    playing = False
    q.put(playing)

    a = threading.Thread(target=record_audio, args=(record_duration,))
    v = threading.Thread(target=record_video, args=(caps,q))
    if stimulus:
        song = select_song()
        s = threading.Thread(target=play_wav, args=(song,q))

    print('starting audio')
    a.start()

    print('starting video')
    v.start()

    if stimulus:
        print('playing sound')
        s.start()
        s.join()
    a.join()
    v.join()
       

def record_video(caps,q):
    global codec, camera_dict, n_cameras, record_duration, fps, w,h 
    global v_tmpfiles, v_start, log_dict
    #h,w,fps = check_cameras(caps)
    currentDT = datetime.datetime.now()
    log_dict['DT'] = currentDT
    v_outroot = 'tmp_' + currentDT.strftime("%Y-%m-%d-%H:%M:%S")
    v_tmpfiles = []
    writers = [0] * n_cameras
    fourcc = cv2.VideoWriter_fourcc(*codec)
    song = log_dict['Song'].split('.')[0]
    for c in range(n_cameras):
        v_out = v_outroot + '_' + camera_dict[c] + '_' + song + '.avi'
        writers[c] = cv2.VideoWriter(parent_dir + v_out,fourcc,fps, (w,h))
        v_tmpfiles.append(v_out)

    v_start = time.time()
    v_end = v_start + record_duration

    while time.time() < v_end:
        if not q.empty():
            playing = q.get()
        for c in range(n_cameras):
            ret, frame = caps[c].read()
            if playing:
                frame = add_marker(frame,c)
            writers[c].write(frame)

    ## Also, check fps
    print('Finished video recording!')
    return v_tmpfiles

def add_marker(frame, c):
    frame[0:50,0:50] = [0,255,0]
    return frame

def record_audio(length = 10):
    global A_START, A_STOP, A_TMP
    a_start = time.time()
    a_outfile = parent_dir + 'tmp_audio.wav'
    r_proc = Popen(['arecord','-d',str(length),'-t','wav',a_outfile])
    r_proc.wait()
    a_stop = time.time()
    A_START, A_STOP, A_TMP = a_start, a_stop, a_outfile
    return a_start, a_stop, a_outfile
        
def splice_AV(v_files = None,a_file = None,offset = None):
    global A_START, v_start, v_tmpfiles, A_TMP
    
    if v_files == None:
        v_files = v_tmpfiles
    if a_file == None:
        a_file = A_TMP
    if offset == None:
        offset = 0
        print('Audio/video=',A_START,v_start)
        if offset < 0:
            offset = 0

    av_outfiles = []
    for v_file in v_files:
        av_outfile = video_dir + v_file.replace('tmp_','')
        proc = Popen(['ffmpeg','-i',parent_dir + v_file,'-itsoffset',str(offset),'-i',a_file, 
            '-vcodec','copy', '-acodec','copy',av_outfile])
        proc.wait()
        av_outfiles.append(av_outfile)
    return av_outfiles

def play_wav(wav_file,q):
    time.sleep(1)
    playing = True
    q.put(playing)
    p_proc = Popen(['aplay',wav_file])
    p_proc.wait()
    playing = False
    q.put(playing)

def select_song():
    global log_dict
    song_df = pd.read_csv(song_log)
## Find the next row to be played
    next_row_index = song_df[song_df['Played'] == 0].index[0]
    next_row = song_df.iloc[next_row_index]
    song = next_row['SongFile']
    next_row['Played'] = 1
## Edit the df to show that has been played and save as a tmp file
    song_df.iloc[next_row_index] = next_row
    song_df.to_csv(parent_dir + 'tmp_log.csv', sep=',', index=False)
    log_dict['Playback'] = True
    log_dict['Song'] = song
    song = song_directory + song
    return song

def unload_cameras(caps):
    for cap in caps:
        cap.release()
    cv2.destroyAllWindows()

def check_outcome():
    real_fps = frame_count / record_time

def update_log(log_notes):
## Add a line with 
#"Date/Time Song Played Info (cams missing, motion, etc) "
    out_file = open(log_file,'a')
    for k in log_notes.keys():
        out_string = k + ': ' + str(log_notes[k]) + '; '
        out_file.write(out_string)
    out_file.write('\n')
    out_file.close()

def tidy_up(success):
    if success:
        os.rename(parent_dir + 'tmp_log.csv',log_dir + 'playback_log.csv')
    tmp_files = glob.glob(parent_dir + 'tmp*')
    for f in tmp_files:
        os.remove(f)
# Delete tmp files
# Copy tmp to full log

if __name__ == "__main__":
    caps = load_cameras()
    h,w,fps = check_cameras(caps)
    complete, caps, corner_array = locate_markers(caps, visual=True)
    print(complete, corner_array)
    if complete:
        camera_order, corner_array = get_order(corner_array)
        define_cages(corner_array)
        #print(window_dict)
    success, cage_motion,monitor_time = monitor_cameras(caps,visual=True)
    print(success,cage_motion, monitor_time)
    #unload_cameras(caps)
    #caps = load_cameras()
    if success:
        record_AV(caps)
        unload_cameras(caps)
        outfiles = splice_AV()
    update_log(log_dict)
    tidy_up(success)
