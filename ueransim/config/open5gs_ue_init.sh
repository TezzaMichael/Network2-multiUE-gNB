#!/bin/bash

sleep 25
./nr-ue -c "/mnt/ueransim/open5gs_ue$1.yaml" > "/mnt/log/ue$1.log" 2>&1
