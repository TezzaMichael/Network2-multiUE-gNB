#!/bin/bash

docker exec -i $(docker ps -aq -f "name=^$1$") /bin/bash -c "tcpdump -i gnb1-s1 -n -w -" > test.pcap
