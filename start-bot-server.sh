#!/bin/bash  
echo "activating environment"
. .venv/bin/activate
echo "reading requirements"
sudo pip3 install -r ./reqs.txt
echo "starting dir server"
python3 server.py

