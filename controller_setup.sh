#!/bin/bash

# Update and upgrade the system
sudo apt update && sudo apt full-upgrade -y

# Install Adafruit Blinka
cd ~
pip3 install --upgrade adafruit-python-shell
wget https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/master/raspi-blinka.py
sudo -E env PATH=$PATH python3 raspi-blinka.py <<EOF
n
EOF

# Install sensor libraries
sudo pip3 install adafruit-circuitpython-bme280
sudo pip3 install adafruit-circuitpython-lsm6ds

# Remove old numpy version
sudo apt remove -y python3-numpy

# Install newer numpy version
sudo pip3 install numpy --index-url https://pypi.org/simple --no-cache-dir

# Install pyqtgraph
sudo pip3 install pyqtgraph

# Install OpenBLAS development libraries
sudo apt install -y libopenblas-dev

# Install smbus2 library
sudo pip3 install smbus2

# Print completion message
echo "Setup completed successfully! Reboot your system if necessary."
