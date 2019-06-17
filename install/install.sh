#!/bin/bash

echo 'Installing Dependencies - This will required admin permissions'
sudo apt-get -y install python
sudo apt-get -y install python-pip
sudo apt-get -y install libsm6
sudo apt-get -y install libgtk2.0-dev
sudo apt-get -y install ffmpeg

echo -n 'Is this a raspberry pi (y/n)? '
read is_pi
echo "Installing OpenCV"
if [ "${is_pi,,}" == "y" ]; then
  git clone https://github.com/scottbarnesg/Automated-OpenCV-Install.git
  cd Automated-OpenCV-Install/
  bash install-py2.sh
else
  python -m pip install opencv-python
fi

echo 'Installing python packages'
python -m pip install flask
python -m pip install requests

echo -n 'Is this a server instance (y/n)? '
read is_server
if [ "${is_server,,}" == "y" ]; then
  echo "Generating SSL certificate"
  bash generate-cert.sh
  echo "Creating system service"
  path=$(cd ../ && pwd)
  sed -i "/^User=/ s/$/$USER/" ../service/sec-cam-server.service
  echo "ExecStart=/usr/bin/python $path/streamServer.py" >> ../service/sec-cam-server.service
  echo "WorkingDirectory=$path/" >> ../service/sec-cam-server.service
  sudo cp ../service/sec-cam-server.service /etc/systemd/system/
  echo -n "Would you like the server to run automatically (y/n)? "
  read create_service
  if [ "${create_service,,}" == "y" ]; then
    echo "Enabling and starting server service"
    sudo systemctl enable sec-cam-server
    sudo systemctl start sec-cam-server
  fi
fi

echo 'Install complete!'
echo 'To start the server service: sudo systemctl start sec-cam-server'
echo 'To run the server: python smart_sec_cam/streamServer.py'
echo 'To run the client: python smart_sec_cam/streamClient.py'
cd ..
