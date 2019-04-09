# SmartBox
System for tying auditory stimulus to computer vision monitoring of birds. Very much a work in progress. 

Runs from the command line (run_playbacks.py). 
Edit the parameters to define time, motion thresholds, audio files, etc. 

Stay tuned for more documentation. 

Some important points: 
- Don't forget to update the parent directory in run_playbacks.py for your computer (this could probably be fixed)
- Run test.py to make sure you can pull from all the cameras simultaneously. You will likely need to fiddle a bit
- The default Codec runs on Ubuntu 18 out of the box. I have no idea how it will fair on other versions/systems
- I doubt it will work on Windows or Mac without significant modification
