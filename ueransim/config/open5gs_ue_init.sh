#!/bin/bash

sleep 25
./nr-ue -c "/mnt/ueransim/open5gs_ue$1.yaml" -i "imsi-00101123456780$1" > "/mnt/log/ue$1.log" 2>&1
