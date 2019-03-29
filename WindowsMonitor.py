
# coding: utf-8

# In[1]:

## Script to run playback experiments: 
## Made by Ammon Perkes for use in Marc Schmidt's Lab
## For questions, contact perkes.ammon@gmail.com

## Plays and records from each camera in turn, and then closes. 
## The idea is to be booted by Schedule Tasks in windows: SchTasks /Create /SC DAILY /TN “My Task” /TR “C:RunMe.bat” /ST 09:00

import numpy as np
import cv2
import subprocess
import sys,os,shutil
from subprocess import Popen, PIPE
from PIL import Image
import time, datetime 
import threading
import pyaudio, wave

RECORDING = False
LOGS = {}
LOGS[0] = 'BOX0.csv'
LOGS[1] = 'BOX1.csv'
LOGS[2] = 'BOX2.csv'
LOGS[3] = 'BOX3.csv'

OUTPUTS = {}
OUTPUTS[0] = '1'
OUTPUTS[1] = '2'
OUTPUTS[2] = '3'
OUTPUTS[3] = '4'

## Advanced function which actually monitors the camera
def monitor_cam(cam_count = 1):
    caps = [0] * cam_count
    counts = [0] * cam_count
    clips = [[]] * cam_count
    rets = [0] * cam_count
    frames = [0] * cam_count
    grays = [0] * cam_count
    subgrays = [0] * cam_count
    for n in range(cam_count):
        cam_name = 'Cam' + str(n)
        cv2.namedWindow(cam_name)
        caps[n] = cv2.VideoCapture(n)
    
    CONT = True
    while(CONT):
        for n in range(cam_count):
            rets[n],frames[n] = caps[n].read()
            grays[n] = cv2.cvtColor(frames[n], cv2.COLOR_BGR2GRAY)
            
            # Mark the bounding box
            grays[n][99,1000:1100] = 0
            grays[n][201,1000:1100] = 0
            grays[n][100:200,999] = 0
            grays[n][100:200,1101] = 0
            
            subgrays[n] = grays[n][100:200,1000:1100]
            if subgrays[n].mean() < 100:
                counts[n] += 1
                grays[n][99,1000:1100] = 255
                grays[n][201,1000:1100] = 255
                grays[n][100:200,999] = 255
                grays[n][100:200,1101] = 255
                if counts[n] >= 50 and RECORDING == False:     
                    #Add a ten second record function
                    RECORDING == True
                    record_AV(caps[n])
                    counts[n] = 0
                elif RECORDING == True:
                    counts[n] = 0
            else:
                count = 0
            cv2.imshow('Cam'+ str(n),grays[n])
            if cv2.waitKey(100) & 0xFF == ord('q'):
                CONT = False
                
    for n in range(cam_count):
        caps[n].release()
    cv2.destroyAllWindows()
    return

## Simpler function which simply records blindly, checks every camera, and then exits
def record_blind(cam_count = 1):
    caps = [0] * cam_count
    BLIND = True
    counts = [0] * cam_count
    clips = [[]] * cam_count
    rets = [0] * cam_count
    frames = [0] * cam_count
    grays = [0] * cam_count
    subgrays = [0] * cam_count
    for n in range(cam_count):
        cam_name = 'Cam' + str(n)
        cv2.namedWindow(cam_name)
        caps[n] = cv2.VideoCapture(n)
    
    CONT = True
    while(CONT):
        for n in range(cam_count):
            rets[n],frames[n] = caps[n].read()
            ## If Blind is set to True, just record and skip forward
            if BLIND == True:
                record_AV(caps[n],cam_id = n)
                CONT = False
                continue
            
            grays[n] = cv2.cvtColor(frames[n], cv2.COLOR_BGR2GRAY)
            

            # Mark the bounding box
            grays[n][99,1000:1100] = 0
            grays[n][201,1000:1100] = 0
            grays[n][100:200,999] = 0
            grays[n][100:200,1101] = 0
            
            subgrays[n] = grays[n][100:200,1000:1100]
            if subgrays[n].mean() < 100:
                counts[n] += 1
                grays[n][99,1000:1100] = 255
                grays[n][201,1000:1100] = 255
                grays[n][100:200,999] = 255
                grays[n][100:200,1101] = 255
                if counts[n] >= 50 and RECORDING == False:     
                    #Add a ten second record function
                    RECORDING == True
                    record_AV(caps[n],cam_id = n)
                    counts[n] = 0
                elif RECORDING == True:
                    counts[n] = 0
            else:
                count = 0
            cv2.imshow('Cam'+ str(n),grays[n])
            if cv2.waitKey(100) & 0xFF == ord('q'):
                CONT = False
                
    for n in range(cam_count):
        caps[n].release()
    cv2.destroyAllWindows()
    return    

## Little function to speak. Handy for sound tests, or for freaking out your friends
def speak(phrase = "Hi there", wait = 2):
    time.sleep(wait)
    subprocess.call(["say",phrase])
    return

## More advanced function which plays a specific sound to a specific output device. 
def play_sound_py(cam_id, song_name = 'BDY.wav', output_device = 1):
    global OUTPUTS
    
    CHUNK = 1024

    wf = wave.open(song_name, 'rb')
    if output_device == 0:
        output_devie = OUTPUTS[cam_id]
    # instantiate PyAudio (1)
    p = pyaudio.PyAudio()

    # open stream (2)
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output_device_index = output_device,
                    output=True)
    # read data
    data = wf.readframes(CHUNK)

    # play stream (3)
    while len(data) > 0:
        stream.write(data)
        data = wf.readframes(CHUNK)

    # stop stream (4)
    stream.stop_stream()
    stream.close()

    # close PyAudio (5)
    p.terminate()
    return 0

## As above, but finds a specific song (I could probably roll these two into one, but whatever.)
def play_song_py(cam_id, output_device = 1, wait = 2):
    global OUTPUTS
    if output_device == 0:
        output_device = OUTPUTS[cam_id]
    time.sleep(wait)
    song_name = get_song(cam_id)
    CHUNK = 1024

    wf = wave.open('BDY_right.wav', 'rb')

    # instantiate PyAudio (1)
    p = pyaudio.PyAudio()

    # open stream (2)
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output_device_index = output_device,
                    output=True)
    # read data
    data = wf.readframes(CHUNK)

    # play stream (3)
    while len(data) > 0:
        stream.write(data)
        data = wf.readframes(CHUNK)

    # stop stream (4)
    stream.stop_stream()
    stream.close()

    # close PyAudio (5)
    p.terminate()
    return 0

## Simple function which plays a song out of the default output device
def play_song(cam_id, wait = 2):
    time.sleep(wait)
    song_name = get_song(cam_id)

    #winsound.PlaySound(song_name, winsound.SND_FILENAME)
    return_code = subprocess.call(["afplay", song_name])
    
    print song_name
    return 

## Function for finding the correct song for the cam_id, based on a somewhat involved .csv
def get_song(cam_id):
    global LOGS
    logs = LOGS
    bird_name = 0
    log_name = logs[cam_id]
    r_log = open(log_name,'r')
    tmp_log = open('tmp.csv','w')
    #NOTE: this could be cleaner
    unplayed = 1
    for line in r_log:
        split_line = line.strip().split(',')
        if split_line[-1] != '0':
            tmp_log.write(line + '\n')
        elif split_line[-1] == '0' and unplayed:
            print 'I found a line!'
            bird_name = split_line[1]
            split_line[-1] = str(datetime.datetime.now())
            tmp_log.write(",".join(split_line) + '\n')
            unplayed = 0
        else:
            tmp_log.write(line + '\n')
    print 'No more unplayed songs found'
    r_log.close()
    tmp_log.close()
    # Save tmp_log as r_log
    shutil.move('tmp.csv',log_name)
    if cam_id % 2 == 0:
        side = '_right.wav'
    else:
        side = '_left.wav'
    song_name = bird_name + side  
    return song_name

## Runs the AV recording, including playing a song. 
def record_AV(cap, mic = None, cam_id = 0):
    # Start Audio & Video, then play the sound
    #print 'booting up threads'
    #t = threading.Thread(target=speak)
    t = threading.Thread(target=play_song,args=(cam_id,))
    #record_audio()
    a = threading.Thread(target=record_audio, args=(10,mic,))
    #record_video()
    v = threading.Thread(target=record_video, args=(cap,))
    
    print 'starting audio'
    a.start()
   
    #print 'starting video'
    v.start() 
    
    #print 'playing sound'
    t.start()
    """
    count = 0
    # Add a ~10s monitor so you see the posture
    while(count<100):
        ret0,frame0 = cap0.read()
        ret1,frame1 = cap1.read()
        
        gray0 = cv2.cvtColor(frame0,cv2.COLOR_BGR2GRAY)
        gray1 = cv2.cvtColor(frame1,cv2.COLOR_BGR2GRAY)
        cv2.imshow('cam0',gray0)
        cv2.imshow('cam1',gray1)
        count += 1
        cv2.waitKey(5)
    """
    #The join stops it from continueing until it's done..
    a.join()
    v.join()
    t.join()
    
    return 

# Record and save audio
# Defaults to default microphone, you'll need to know the specific index otherwise
# There could be a way to automate it...
def record_audio(length = 10,mic = None):
    
    #print 'recording audio...'
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

    # Boot up stream and populate data then close stream (I'll know the amount of time recording)
    stream = p.open(format=FORMAT,channels=CHANNELS,rate=FRAME_RATE,input=True, input_device_index=mic,frames_per_buffer=FRAMES_PERBUFF)
    frames = []

    REC_SECONDS = length
    nchunks = int(REC_SECONDS * FRAME_RATE / FRAMES_PERBUFF)
    a_start = time.time()
    for i in range(0, nchunks):
        data = stream.read(FRAMES_PERBUFF)
        frames.append(data)
    a_stop = time.time()
    stream.stop_stream()
    stream.close()

    #print 'saving audio...'
    date_string = time.strftime("%Y-%m-%d-%H:%M")
    outfile = 'test_audio_' + date_string + ".wav"
    
    wf = wave.open(outfile,'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(FRAME_RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    
    global A_START
    global A_FINISH
    global A_TMP
    A_START = a_start
    A_FINISH = a_stop
    A_TMP = outfile
    return

def record_video(cap):
    print 'recording video...'
    clip = []
    """
    v_0 = time.time()
    ret,frame = cap.read()
    clip.append(frame)
    v_start = time.time()
    cv2.waitKey(40)
    v_wait = time.time()
    ret,frame = cap.read()
    clip.append(frame)
    v_2 = time.time()
    
    print 'time series:'
    print v_0
    print v_start
    print v_wait
    print v_2"""
    
    v_start = time.time()
    
    vid_time = 10
    while time.time() <= v_start + vid_time:
        ret, frame = cap.read()
        clip.append(frame)
        cv2.waitKey(40)
    """    
    while(len(clip) <= 300):
        ret, frame = cap.read()
        clip.append(frame)  
        cv2.waitKey(40)
    """    
    v_stop = time.time()
    vid_length = v_stop - v_start
    num_frames = len(clip)
    fps = num_frames / vid_length
    print fps
    round_fps = int(round(fps))
    global V_START
    global V_FINISH
    
    V_START = v_start
    V_FINISH = v_stop
    
    save_clip(clip,fps)

    return

def save_clip(clip,fps):
    global RECORDING
    print 'saving clip....'
    date_string = time.strftime("%Y-%m-%d-%H:%M:%S")
    outfile = 'test_vid' + date_string + ".avi"
    framerate = str(fps)
    p = Popen(['ffmpeg', '-y', '-f', 'image2pipe', '-vcodec', 'mjpeg', 
               '-r', framerate, '-i', '-', '-vcodec', 'mpeg4', '-qscale', 
               '5', '-r', framerate, outfile], stdin=PIPE)
    fps, duration = 20, len(clip) / 20.
    for i in range(len(clip)):
        col_im = cv2.cvtColor(clip[i],cv2.COLOR_BGR2RGB)
        rot_im = np.rot90(col_im,3)
        im = Image.fromarray(rot_im)
        im.save(p.stdin, 'JPEG')
    #print clip[i]
    p.stdin.close()
    p.wait()
    
    global A_START,V_START, A_TMP
    offset = V_START - A_START
    print V_START
    print A_START
    a_file = A_TMP
    splice_AV(a_file,outfile,offset)
    RECORDING = False
    #print "monitoring..."
    return

# Combine audio & video with calculated offset
# NOTE: this is tricky, and does not work well on apple, as far as I can tell. 
# There seems to be a better function for windows. 

def splice_AV(a_file,v_file,offset):
    outfile = 'av_' + v_file
    
    # quickly convert offset to time

    p = Popen(['ffmpeg','-i',v_file, '-itsoffset', str(offset), 
           '-i', a_file, '-vcodec', 'copy', '-acodec', 'copy', outfile])
    p.wait()
    #Popen(['rm',a_file,v_file])
    return

## A little function to test cameras and microphones, since those id's are hard coded.
def AV_test(cam_id = 0, output_id = 1):
    #stream camera
    cam_name = 'Cam' + str(cam_id)
    cv2.namedWindow(cam_name)
    cap = cv2.VideoCapture(cam_id)
    CONT = True
    while(CONT):
        ret,frame = cap.read()
        grayscale = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        
        cv2.imshow(cam_name,grayscale)
        if cv2.waitKey(100) & 0xFF == ord('q'):
            CONT = False
        if cv2.waitKey(100) & 0xFF == ord('p'):
            play_sound_py(output_id)
            #t = threading.Thread(target=speak)
            #t.start()
    #wait for keypress space : speak
    #wait for keypress q : quit

if __name__ == '__main__':
    #monitor_cam()
    #record_blind()
    #play_song_py(0)
    AV_test()
    pass           


# In[ ]:



