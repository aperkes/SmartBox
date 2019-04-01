#! /usr/bin/env python

## Code to run playback experiments 
## For use it Marc Schmidt's lab
## Made April, 2019 by Ammon Perkes
## Contact perkes.ammon@gmail.com for questions

web_cam_ids = 
motion_threshold = 12
codec = 'MJPG'
out_type = '.avi'
duration = 5

def load_cameras():
## Make sure they get the correct cameras in the correct order, and that they're all there...
## The best way to assign cameras to specific places might be to use the markers...
    for c in range(n_cameras):
        caps[c],rets[c] = cv2.VideoCapture(c)
    return caps

def locate_markers():
    return locations

## Based on markers, figure out which cage is which
def define_cages():
    return cage_indices
def check_cameras():
## Check fps, consistency, etc
    global fps
    fps = cap.get(cv2.CAP_PROP_FPS)

## Wait until cowbirds are calm, once it is, return True
# If they never calm down, return false, and decide what to do. 
def monitor_movement(visual = False):
    global n_cameras, window_dict
    success == False
    current_frames = np.empty([n_cameras,h,w])
    previous_frames = np.empty_like(current_frames)
    rets = [[]] * n_cameras
    cage_motion = np.empty([counts,9])
    bool_motion = np.zeros([counts,9])
    for c in range(n_cameras):
        rets[c], previous_frames[c] = caps[c].read()
## Until it exhausts its check time or is successful, within each camera, within each designated cage, check for motion
    while time.time() < end_time() and success == False:
# first read each camera, then compare
        for c in range(n_cameras):
            rets[c], current_frames[c] = caps[c].read()
        for c in range(n_cameras):
            if rets[c] == False:
                continue
            windows = window_dict[c]
            for w in range(len(windows))
                w_pixels = windows[w]
                dif = cv2.absdiff(current_frames[c][w_pixels],previous_frames[c][w_pixels])
                cage_index = cage_indices[c,w]
## Save both the amount of motion, and a boolean of whether it's above the threshold. 
                cage_motion[count,cage_index] = dif
                if dif < motion_threshold:
                    bool_motion[count,bcage_index] = False
        sum_bools = np.sum(bool_motion,0)
        if np.min(sum_bools) > bird_threshold:
            success = True 
        count = (count + 1) % counts
        previous_frames = np.copy(current_frames)
    monitor_time = duration - time.time() - end_time ## probably should have just tracked start time...
    return success, cage_motion, monitor_time         


def select_song():

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

def play_song():
    #while playing, add visual annotation of the signal to the phrames. (a box in corners) 

def add_marker():
    return marked_frame

def save_clip(): 
    ## Only needed if record_clip can't function properly
    pass

def unload_cameras():
    cap.release()
    cv2.destroyAllWindows()

def check_outcome():
    real_fps = frame_count / record_time

def update_log():
