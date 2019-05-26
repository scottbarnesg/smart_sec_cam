#!/bin/bash

echo 'Installing Dependencies - This will required admin permissions'
sudo apt-get -y install python
sudo apt-get -y install python-pip
sudo apt-get -y install libsm6
sudo apt-get -y install libgtk2.0-dev
sudo apt-get -y install ffmpeg

echo 'Installing python packages'
python -m pip install opencv-python
python -m pip install flask
python -m pip install requests

echo 'Is this a server instance (y/n)?'
read is_server
if [ "${is_server,,}" == "y" ]; then
  echo "Generating SSL certificate"
  bash generate-cert.sh
  echo "Done"
fi

echo 'Install complete!'
echo 'To run the server: python smart_sec_cam/streamServer.py'
echo 'To run the client: python smart_sec_cam/streamClient.py'
