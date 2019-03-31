#!/bin/bash

echo 'Installing Dependencies - This will required admin permissions'
sudo apt-get install python
sudo apt-get install pip
sudo apt-get install libsm6
sudo apt-get install libgtk2.0-dev
sudo apt-get install git

echo 'Installing python packages'
python -m pip install opencv-python
python -m pip install flask
python -m pip install requests

echo 'Fetching the repository'
git clone https://github.com/scottbarnesg/smart_sec_cam.git

echo 'Install complete!'
echo 'To run the server: python smart_sec_cam/streamServer.py'
echo 'To run the client: python smart_sec_cam/streamClient.py'
