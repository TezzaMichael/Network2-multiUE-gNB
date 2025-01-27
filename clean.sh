#!/bin/bash

sudo mn -c

docker stop $(docker ps -aq)

docker container prune -f

if [ "$1" == "log" ]; then
    cd log && sudo rm *.log 
fi

# Delete all generated files 
rm ueransim/config/open5gs*.yaml
rm python_modules/subscribers.json

sudo ip link delete s1-ue1
sudo ip link delete s1-ue2
sudo ip link delete s1-ue3
sudo ip link delete s1-ue4
sudo ip link delete s1-ue5
sudo ip link delete s1-ue6
sudo ip link delete s1-ue7
sudo ip link delete s1-ue8
sudo ip link delete s1-ue9
sudo ip link delete s1-ue10
sudo ip link delete s1-ue11
sudo ip link delete s1-ue12
sudo ip link delete s1-ue13
sudo ip link delete s1-ue14
sudo ip link delete s1-ue15
sudo ip link delete s1-ue16
sudo ip link delete s1-ue17
sudo ip link delete s1-ue18
sudo ip link delete s1-ue19
sudo ip link delete s1-ue20
sudo ip link delete s2-s3
sudo ip link delete s2-s1
sudo ip link delete gnb1-s1
sudo ip link delete gnb2-s1
sudo ip link delete gnb3-s1
sudo ip link delete s3-cp
sudo ip link delete s2-upf_mec
sudo ip link delete s3-upf
sudo ip link delete s3-mec_server
