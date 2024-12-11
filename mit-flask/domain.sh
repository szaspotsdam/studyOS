#!/bin/bash
#sudo avahi-set-host-name studyos
#sudo avahi-daemon
cd /home/studyos/studyOS/mit-flask/
sudo gunicorn -w 4 -b 0.0.0.0:80 rec:app
