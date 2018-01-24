# Quick code to capture video, courtesy of opencv documentation
# This is becoming more of a platform, worth cleaning up 
# 
# Todo: 
# Synch up audio and video - This is a problem...possibly unsurmountable? 
# Clean up UI
# Add debugging
# Add Menu? - Set parameters, devices, bounding box, etc 
# Specify Audio output device - x
# Play sound from file - x
# Order sound playback (random? Set? Maybe based on date? 

import numpy as np
import cv2
import subprocess
import sys,os
from subprocess import Popen, PIPE
from PIL import Image
import time, datetime 
import threading
import pyaudio, wave

RECORDING = False
    
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

## Wait some set amount and says a string
def speak(phrase = "Hi there", wait = 2):
    time.sleep(wait)
    subprocess.call(["say",phrase])
    return

## Play some .wav from a file using a specified output device
def play_wav(p_audio = pyaudio.PyAudio, wav_file = "test.wav", out_index = 1):
    CHUNK = 1024
    p = p_audio
    wf = wave.open(wav_file, 'rb')
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True, 
                    output_device_index = out_index)
    data = wf.readframes(CHUNK)
    while len(data) > 0:
        stream.write(data)
        data = wf.readframes(CHUNK)

    stream.stop_stream()
    stream.close()
    return

def record_AV(cap, mic = None):
    # Start Audio & Video, then play the sound
    #print 'booting up threads'
    t = threading.Thread(target=speak)
    #t = threading.Thread(target=play_wav,args(out_index=mic,) 
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
    #a.join()
    #v.join()
    #t.join()
    
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
    print "monitoring..."
    return

# Combine audio & video with calculated offset
def splice_AV(a_file,v_file,offset):
    outfile = 'av_' + v_file
    
    # quickly convert offset to time

    p = Popen(['ffmpeg','-i',v_file, '-itsoffset', str(offset), 
           '-i', a_file, '-vcodec', 'copy', '-acodec', 'copy', outfile])
    p.wait()
    #Popen(['rm',a_file,v_file])
    return
    
if __name__ == '__main__':
    monitor_cam()
