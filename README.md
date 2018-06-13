# Converts USB Webcam into Smart Security Camera

## Overview
Turns a USB Webcam into a smart security camera. Frames are captured at fixed
intervals and compared to detect motion. When motion is detected, video is
captured and stored as:  
```
bin/videos0/video_name.avi
```
A new folder is created each time the program is run so as not to override old
files.  

Parameters can be modified in the command line. The image capture delay, video
length, USB port, and mode can be set. See the main function for guidance.

## Dependencies:
Python 2.7.x
OpenCV 3.4.x

## Installing Dependences:
The default pip version of OpenCV does not contain the required video capabilities.
This requires the install to be compiled with ffmpeg, which can be accomplished by installing from source or using precompiled anaconda channel (below):  
```
$ conda install -c conda-forge ffmpeg
$ conda install -c conda-forge opencv
```
