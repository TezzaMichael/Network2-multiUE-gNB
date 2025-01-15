#!/bin/bash


sleep 20
./nr-gnb -c "/mnt/ueransim/open5gs_gnb$1.yaml" > "/mnt/log/gnb$1.log" 2>&1
