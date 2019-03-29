
# coding: utf-8

# In[ ]:


## Quick script to queau up the next song for playback, play/record, and log the fact that it plays
## Thrown together by Ammon Perkes for work in Schmidt Lab
# contact perkes.ammon@gmail.com for questions

import subprocess
import datetime
import shutil

def get_song(log_name = 'BOX0.csv'):
    #global LOGS
    #logs = LOGS
    #bird_name = 0
    #log_name = logs[cam_id]
    log_path = '/home/bird/Documents/birds/src/bird_recording/src/playback_logs/'
    tmp_name = 'tmp_' + log_name
    r_log = open(log_path + log_name,'r')
    tmp_log = open(log_path + tmp_name,'w')
    #NOTE: this could be cleaner
    unplayed = 1
    ## Read through the file and find the first unplayed song
    # Write each song to the tmp_file, and then copy it over
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
    shutil.move(log_path + tmp_name,log_path + log_name)
    #os.remove(tmp_name)
    song_name = bird_name  
    return song_name

def run_bash():
    song_path = '/home/bird/Documents/birds/src/bird_recording/src/playback_songs/'
    bash_command = '/home/bird/Documents/birds/src/bird_recording/src/play_record_process.bash'
    time = '20'
    host = 'birdview-2'
    high_quality = 'True'
    audio_delay = '0'
    song_file = song_path + get_song() + '.wav'
    return_code = subprocess.call([bash_command, time, host, high_quality, audio_delay, song_file])
    
if __name__ == '__main__':
    run_bash()

