 
# coding: utf-8

# In[21]:

## Simplified Script to run playback experiments: 
## Made by Ammon Perkes for use in Marc Schmidt's Lab
## For questions, contact perkes.ammon@gmail.com

## Plays song in each box.
## The idea is to be booted by Schedule Tasks in windows: SchTasks /Create /SC DAILY /TN “My Task” /TR “C:RunMe.bat” /ST 09:00

import numpy as np
import subprocess
import sys,os,shutil
import time, datetime 
import pyaudio, wave

RECORDING = False
LOG_PATH = './Logs/'
LOGS = {}
LOGS[0] = 'BOX0.csv'
LOGS[1] = 'BOX1.csv'
LOGS[2] = 'BOX2.csv'
LOGS[3] = 'BOX3.csv'

OUTPUTS = {}
OUTPUTS[0] = 1
OUTPUTS[1] = 1
OUTPUTS[2] = 2
OUTPUTS[3] = 2

CHUNK = 1024
SONGS = './Songs/'

## Little function to speak. Handy for sound tests, or for freaking out your friends
def speak(phrase = "Hi there", wait = 2):
    time.sleep(wait)
    subprocess.call(["say",phrase])
    return

## More advanced function which plays a specific sound to a specific output device. 
def play_sound_py(cam_id, song_name = 'BDY.wav', output_device = 1):
    global OUTPUTS, SONGS
    song_path = SONGS
    
    CHUNK = 1024

    wf = wave.open(song_path + song_name, 'rb')
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
def play_song_py(cam_id, output_device = 1, wait = 10):
    global OUTPUTS, CHUNK, SONGS
    if output_device == 0:
        output_device = OUTPUTS[cam_id]
    time.sleep(wait)
    song_name = get_song(cam_id)
    CHUNK = 1024
    song_path = SONGS
    wf = wave.open(song_path + song_name, 'rb')

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
    
    #print song_name
    return 

## Function for finding the correct song for the cam_id, based on a somewhat involved .csv
def get_song(cam_id):
    global LOGS, LOG_PATH
    log_path = LOG_PATH
    logs = LOGS
    bird_name = 0
    log_name = log_path + logs[cam_id]
    tmp_name = log_path + 'tmp_' + logs[cam_id]
    r_log = open(log_name,'r')
    tmp_log = open(tmp_name,'w')
    #NOTE: this could be cleaner
    unplayed = 1
    for line in r_log:
        split_line = line.strip().split(',')
        if split_line[-1] != '0':
            tmp_log.write(line)
        elif split_line[-1] == '0' and unplayed:
            #print 'I found a line!'
            bird_name = split_line[1]
            split_line[-1] = str(datetime.datetime.now())
            tmp_log.write(",".join(split_line) + '\n')
            unplayed = 0
        else:
            tmp_log.write(line)
    #print 'No more unplayed songs found'
    r_log.close()
    tmp_log.close()
    # Save tmp_log as r_log
    shutil.move(tmp_name,log_name)
    #os.remove(tmp_name)
    if cam_id % 2 == 0:
        side = '_right.wav'
    else:
        side = '_left.wav'
    song_name = bird_name + side  
    return song_name

def play_each_song(n_cams):
    global OUTPUTS, LOGS 
    for n in range(n_cams):
        play_song_py(n, output_device=0)
# Combine audio & video with calculated offset
# NOTE: this is tricky, and does not work well on apple, as far as I can tell. 
# There seems to be a better function for windows. 



if __name__ == '__main__':
    #monitor_cam()
    #record_blind()
    #play_song_py(0)
    play_each_song(4)
    pass           


# In[ ]:



