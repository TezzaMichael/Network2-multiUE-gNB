#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import os

from comnetsemu.cli import CLI, spawnXtermDocker
from comnetsemu.net import Containernet, VNFManager
from mininet.link import TCLink
from mininet.log import info, setLogLevel
from mininet.node import Controller

from python_modules.Open5GS   import Open5GS
import sys
sys.path.append('/home/ubuntu/Network2-multiUE-gNB1/python_modules/')
from createJson import getJson

sys.path.append('/home/ubuntu/Network2-multiUE-gNB1/ueransim/config/')
from createUE import getYaml
from creategNB import getYamlgNB
import json, time
import math

if __name__ == "__main__":
    nUE = sys.argv[1]  # Cli parameter
    nUE = int(nUE)
    ngNB = math.ceil(nUE/3)
    getYaml(nUE)
    getYamlgNB(ngNB)
    AUTOTEST_MODE = os.environ.get("COMNETSEMU_AUTOTEST_MODE", 0)

    setLogLevel("info")

    prj_folder="/home/ubuntu/Network2-multiUE-gNB1"
    mongodb_folder="/home/ubuntu/mongodbdata"

    env = dict()

    net = Containernet(controller=Controller, link=TCLink)

    info("*** Adding Host for open5gs CP\n")
    cp = net.addDockerHost(
        "cp",
        dimage="my5gc_v2-4-4",
        ip="192.168.0.111/24",
        # dcmd="",
        dcmd="bash /open5gs/install/etc/open5gs/5gc_cp_init.sh",
        docker_args={
            "ports" : { "3000/tcp": 3000 },
            "volumes": {
                prj_folder + "/log": {
                    "bind": "/open5gs/install/var/log/open5gs",
                    "mode": "rw",
                },
                mongodb_folder: {
                    "bind": "/var/lib/mongodb",
                    "mode": "rw",
                },
                prj_folder + "/open5gs/config": {
                    "bind": "/open5gs/install/etc/open5gs",
                    "mode": "rw",
                },
                "/etc/timezone": {
                    "bind": "/etc/timezone",
                    "mode": "ro",
                },
                "/etc/localtime": {
                    "bind": "/etc/localtime",
                    "mode": "ro",
                },
            },
        },
    )


    info("*** Adding Host for open5gs UPF\n")
    env["COMPONENT_NAME"]="upf_cld"
    upf_cld = net.addDockerHost(
        "upf_cld",
        dimage="my5gc_v2-4-4",
        ip="192.168.0.112/24",
        # dcmd="",
        dcmd="bash /open5gs/install/etc/open5gs/temp/5gc_up_init.sh",
        docker_args={
            "environment": env,
            "volumes": {
                prj_folder + "/log": {
                    "bind": "/open5gs/install/var/log/open5gs",
                    "mode": "rw",
                },
                prj_folder + "/open5gs/config": {
                    "bind": "/open5gs/install/etc/open5gs/temp",
                    "mode": "rw",
                },
                "/etc/timezone": {
                    "bind": "/etc/timezone",
                    "mode": "ro",
                },
                "/etc/localtime": {
                    "bind": "/etc/localtime",
                    "mode": "ro",
                },
            },
            "cap_add": ["NET_ADMIN"],
            "sysctls": {"net.ipv4.ip_forward": 1},
            "devices": "/dev/net/tun:/dev/net/tun:rwm"
        }, 
    )

    info("*** Adding Host for open5gs UPF MEC\n")
    env["COMPONENT_NAME"]="upf_mec"
    upf_mec = net.addDockerHost(
        "upf_mec",
        dimage="my5gc_v2-4-4",
        ip="192.168.0.113/24",
        # dcmd="",
        dcmd="bash /open5gs/install/etc/open5gs/temp/5gc_up_init.sh",
        docker_args={
            "environment": env,
            "volumes": {
                prj_folder + "/log": {
                    "bind": "/open5gs/install/var/log/open5gs",
                    "mode": "rw",
                },
                prj_folder + "/open5gs/config": {
                    "bind": "/open5gs/install/etc/open5gs/temp",
                    "mode": "rw",
                },
                "/etc/timezone": {
                    "bind": "/etc/timezone",
                    "mode": "ro",
                },
                "/etc/localtime": {
                    "bind": "/etc/localtime",
                    "mode": "ro",
                },
            },
            "cap_add": ["NET_ADMIN"],
            "sysctls": {"net.ipv4.ip_forward": 1},
            "devices": "/dev/net/tun:/dev/net/tun:rwm"
        },
    )

    info("*** Adding gNB\n")
    array1 = []
    for i in range(1, ngNB+1):
        env["COMPONENT_NAME"]=f"gnb{i}"
        array1.append(net.addDockerHost(
            f"gnb{i}", 
            dimage="myueransim_v3-2-6",
            ip=f"192.168.0.{130+i}/24",
            # dcmd="",
            dcmd=f"bash /mnt/ueransim/open5gs_gnb_init.sh {i}",
            docker_args={
                "environment": env,
                "volumes": {
                    prj_folder + "/ueransim/config": {
                        "bind": "/mnt/ueransim",
                        "mode": "rw",
                    },
                    prj_folder + "/log": {
                        "bind": "/mnt/log",
                        "mode": "rw",
                    },
                    "/etc/timezone": {
                        "bind": "/etc/timezone",
                        "mode": "ro",
                    },
                    "/etc/localtime": {
                        "bind": "/etc/localtime",
                        "mode": "ro",
                    },
                    "/dev": {"bind": "/dev", "mode": "rw"},
                },
                "cap_add": ["NET_ADMIN"],
                "devices": "/dev/net/tun:/dev/net/tun:rwm"
            },
        ))

    info("*** Adding UE\n")
    array = []
    for i in range(1, nUE+1):
        env["COMPONENT_NAME"]= f"ue{i}"
        array.append(net.addDockerHost(
            f"ue{i}", 
            dimage="myueransim_v3-2-6",
            ip=f"192.168.0.{139+i}/24",
            dcmd=f"bash /mnt/ueransim/open5gs_ue_init.sh {i}",
            docker_args={
                "environment": env,
                "volumes": {
                    prj_folder + "/ueransim/config": {
                        "bind": "/mnt/ueransim",
                        "mode": "rw",
                    },
                    prj_folder + "/log": {
                        "bind": "/mnt/log",
                        "mode": "rw",
                    },
                    "/etc/timezone": {
                        "bind": "/etc/timezone",
                        "mode": "ro",
                    },
                    "/etc/localtime": {
                        "bind": "/etc/localtime",
                        "mode": "ro",
                    },
                    "/dev": {"bind": "/dev", "mode": "rw"},
                },
                "cap_add": ["NET_ADMIN"],
                "devices": "/dev/net/tun:/dev/net/tun:rwm"
            },
        )  )

            
    info("*** Add controller\n")
    net.addController("c0")

    info("*** Adding switch\n")
    s1 = net.addSwitch("s1")
    s2 = net.addSwitch("s2")
    s3 = net.addSwitch("s3")

    info("*** Adding links\n")
    net.addLink(s1,  s2, bw=1000, delay="10ms", intfName1="s1-s2",  intfName2="s2-s1")
    net.addLink(s2,  s3, bw=1000, delay="50ms", intfName1="s2-s3",  intfName2="s3-s2")
    
    net.addLink(cp,      s3, bw=1000, delay="1ms", intfName1="cp-s1",  intfName2="s1-cp")
    net.addLink(upf_cld, s3, bw=1000, delay="1ms", intfName1="upf-s3",  intfName2="s3-upf_cld")
    net.addLink(upf_mec, s2, bw=1000, delay="1ms", intfName1="upf_mec-s2", intfName2="s2-upf_mec")
    
    for i in range(nUE):
        net.addLink(array[i],  s1, bw=1000, delay="1ms", intfName1=f"ue{i+1}-s1",  intfName2=f"s1-ue{i+1}")
    for i in range(ngNB):
        net.addLink(array1[i], s1, bw=1000, delay="1ms", intfName1=f"gnb{i+1}-s1", intfName2=f"s1-gnb{i+1}")
    
    print(f"*** Open5GS: Init subscriber for UE")
    o5gs   = Open5GS( "172.17.0.2" ,"27017")
    o5gs.removeAllSubscribers()
    getJson(nUE)
    
    with open( prj_folder + "/python_modules/subscribers.json" , 'r') as f:
        data = json.load( f )
    
    #json_data = json.loads(data)
    if "subscribers" in data:
        subscribers = data["subscribers"]
        n = 0
        for subscriber in subscribers:
            n += 1
            o5gs.addSubscriber(subscriber)
        info(f"*** Open5GS: Successfuly added {n} subscribers ")
    else:
        info(f"*** Open5GS: No subscribers found")



    info("\n*** Starting network\n")
    net.start()

    if not AUTOTEST_MODE:
        # spawnXtermDocker("open5gs")
        # spawnXtermDocker("gnb")
        CLI(net)

    net.stop()
