#! /usr/bin/env python

## Code to run playback experiments 
## For use it Marc Schmidt's lab
## Made April, 2019 by Ammon Perkes
## Contact perkes.ammon@gmail.com for questions

import numpy as np
import cv2
import time
import pdb
import threading, Queue 
import pyaudio, wave
from subprocess import Popen

#web_cam_ids = 
motion_threshold = 12
bird_threshold = 3
codec = 'MJPG'
out_type = '.avi'
monitor_duration = 60
record_duration = 10
n_cameras = 4
n_cages = 4
PLAYING = False

## Dictionary of the locations of cages in each camera. This will actually be procedurally generated using tags
window_dict = {
    0: [(slice(0,100),slice(0,100))],
    1: [(slice(100,200),slice(0,100))],
    2: [(slice(0,100),slice(100,200))],
    3: [(slice(100,200),slice(100,200))]}
## Indexed array relating actual cages to their location within cameras. 
cage_indices = np.array([[0],[1],[2],[3]])

## Dictionary of identities of each camera. This will also be set using tags
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


def locate_markers():
    pass
    return locations

## Based on markers, figure out which cage is which
def define_cages():
    return cage_indices


## Wait until cowbirds are calm, once it is, return True
# If they never calm down, return false, and decide what to do. 
def monitor_cameras(caps,visual = False):
    global n_cameras, window_dict, cage_indices, monitor_duration, h, w
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
    end_time = time.time() + monitor_duration
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
            for win in range(len(windows)):
                w_pixels = windows[win]
                dif = cv2.absdiff(current_frames[c][w_pixels],previous_frames[c][w_pixels])
                dif[dif < 10] = 0
                cage_index = cage_indices[c,win]
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
    required_time = monitor_duration - time.time() - end_time ## probably should have just tracked start time...
    cv2.destroyAllWindows()
    #pdb.set_trace()
    return success, cage_motion, required_time         

def record_AV(caps, mic = None, stimulus = True):
    q = Queue.Queue()
    playing = False
    q.put(playing)
    if stimulus:
        song = select_song()
        s = threading.Thread(target=play_wav, args=(song,q))
    a = threading.Thread(target=record_audio, args=(record_duration,))
    v = threading.Thread(target=record_video, args=(caps,q))

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
    global v_tmpfiles, v_start
    #h,w,fps = check_cameras(caps)
    v_outroot = 'AV-test'
    v_tmpfiles = []
    writers = [0] * n_cameras
    fourcc = cv2.VideoWriter_fourcc(*codec)
    for c in range(n_cameras):
        v_out = v_outroot + camera_dict[c] + '.avi'
        writers[c] = cv2.VideoWriter(v_out,fourcc,fps, (w,h))
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

## This works, but isn't necessary. If we need to record from a specific mic we can use it. 
def record_audio_complex(length = 10, mic = None):
    p = pyaudio.PyAudio()

    if mic == None:
        dev_index = 0
    else:
        dev_index = mic
    device_info = p.get_device_info_by_index(dev_index)

# Set Parameters
    FRAMES_PERBUFF = 2048
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    FRAME_RATE = int(device_info['defaultSampleRate'])

# Boot up stream and populate data
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=FRAME_RATE, input=True, 
    input_device_index=mic, frames_per_buffer=FRAMES_PERBUFF)
    frames = []

    REC_SECONDS = length
    n_chunks = int(REC_SECONDS * FRAME_RATE / FRAMES_PERBUFF)
    a_start = time.time()
    for i in range(0, n_chunks):
        data = stream.read(FRAMES_PERBUFF)
        frames.append(data)
    a_stop = time.time()
    stream.stop_stream()
    stream.close()
    p.terminate()

    date_string = time.strftime("%Y-%m-%d-%H:%M")
    a_outfile = 'test_audio_' + date_string + '.wav'

    wf = wave.open(a_outfile, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(FRAME_RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

    global A_START,A_FINISH, A_TMP
    A_START = a_start
    A_FINISH = a_stop
    A_TMP = a_outfile
    print('finished audio recording!')
    return a_start, a_stop, a_outfile

def record_audio(length = 10):
    global A_START, A_STOP, A_TMP
    a_start = time.time()
    a_outfile = 'tmp_audio.wav'
    r_proc = Popen(['arecord','-d',str(length),'-t','wav','tmp_audio.wav'])
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
        av_outfile = 'av_' + v_file
        proc = Popen(['ffmpeg','-i',v_file,'-itsoffset',str(offset),'-i',a_file, 
            '-vcodec','copy', '-acodec','copy',av_outfile])
        proc.wait()
        av_outfiles.append(av_outfile)
    return av_outfiles

## This isn't needed, and doesn't work. If we ever want to play from a specific speaker, we can revisit it
def play_wav_complex(p_audio = None, wav_file = 'ND_right.wav', out_index = 2):
    CHUNK = 1024
    if p_audio == None:
        p = pyaudio.PyAudio()
    else:
        p = p_audio
    wf = wave.open(wav_file, 'rb')
    dev_count = p.get_device_count()
    for x in range(dev_count):
        print(p.get_device_info_by_index(x))

    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True,
                    output_device_index = out_index)
    data = wf.readframes(CHUNK)
    global PLAYING
    PLAYING = True
    print(len(data))
    while len(data) > 0:
        stream.write(data)
        data = wf.readframes(CHUNK)

    stream.stop_stream()
    stream.close()
    PLAYING = False
    print('finished playing sound!')

def play_wav(wav_file,q):
    playing = True
    q.put(playing)
    p_proc = Popen(['aplay','./ND_left.wav'])
    p_proc.wait()
    playing = False
    q.put(playing)

def select_song():
    song = './ND_right.wav'
    return song

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
    success, cage_motion,monitor_time = monitor_cameras(caps,visual=False)
    #unload_cameras(caps)
    #caps = load_cameras()
    if success:
        record_AV(caps)
        unload_cameras(caps)
        outfiles = splice_AV()
