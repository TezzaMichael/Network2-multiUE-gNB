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

import ueransim.config.ue_setup as ue_setup
import ueransim.config.gnb_setup as gnb_setup
import python_modules.ue_configuration as ue_configuration
import json, time
import math


def instantiate_cp():
    info("*** Adding Host for open5gs CP\n")
    env["COMPONENT_NAME"]="cp"
    cp = net.addDockerHost(
        "cp",
        dimage="my5gc_v2-4-4",
        ip="192.168.0.111/24",
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
    
    return cp


def instantiate_upf_cld():
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

    return upf_cld


def instantiate_upf_mec():
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
    
    return upf_mec

def instantiate_mec_server():
    info("*** Adding MEC SERVER\n")
    env["COMPONENT_NAME"]="mec_server"
    mec_server = net.addDockerHost(
        "mec_server", 
        dimage="mec_server",
        ip="192.168.0.135/24",
        dcmd="bash /mnt/mec_server/mec_server.sh",
        docker_args={
            "environment": env,
            "volumes": {
                prj_folder + "/mec_server": {
                    "bind": "/mnt/mec_server",
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
            },
            "cap_add": ["NET_ADMIN"],
        },
    )
    return mec_server


def instantiate_gnbs(ngNB):
    info("*** Adding gNB\n")
    gnb_list = []

    for i in range(1, ngNB+1):
        env["COMPONENT_NAME"]=f"gnb{i}"
        gnb_list.append(net.addDockerHost(
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

    return gnb_list


def instantiate_ues(nUE):
    info("*** Adding UE\n")
    ue_list = []

    for i in range(1, nUE+1):
        env["COMPONENT_NAME"]= f"ue{i}"
        ue_list.append(net.addDockerHost(
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

    return ue_list 
            

def add_subscribers(nUE):
    ue_configuration.generate_json(nUE)
    
    with open( prj_folder + "/python_modules/subscribers.json" , 'r') as f:
        data = json.load( f )
    
    if "subscribers" in data:
        subscribers = data["subscribers"]
        n = 0
        for subscriber in subscribers:
            n += 1
            o5gs.addSubscriber(subscriber)
        info(f"*** Open5GS: Successfuly added {n} subscribers ")
    else:
        info(f"*** Open5GS: No subscribers found")

if __name__ == "__main__":
    nUE = int(sys.argv[1])  # Cli parameter
    ngNB = math.ceil(nUE/3)

    ue_setup.generate_yaml(nUE, ngNB)
    gnb_setup.generate_yaml(ngNB)

    AUTOTEST_MODE = os.environ.get("COMNETSEMU_AUTOTEST_MODE", 0)

    setLogLevel("info")

    script_path = os.path.abspath(__file__)
    prj_folder = os.path.dirname(script_path)

    homepath = os.getenv("HOME")  # Works only for linux
    mongodb_folder= f"{homepath}/mongodbdata"

    env = dict()

    net = Containernet(controller=Controller, link=TCLink)

    cp = instantiate_cp()
    upf_cld = instantiate_upf_cld()
    upf_mec = instantiate_upf_mec()
    mec_server = instantiate_mec_server()
    gnb_list = instantiate_gnbs(ngNB)
    ue_list = instantiate_ues(nUE)

    info("*** Add controller\n")
    net.addController("c0")

    info("*** Adding switch\n")
    s1 = net.addSwitch("s1")
    s2 = net.addSwitch("s2")
    s3 = net.addSwitch("s3")

    info("*** Adding links\n")
    net.addLink(s1,  s2, bw=1000, delay="10ms", intfName1="s1-s2",  intfName2="s2-s1")
    net.addLink(s2,  s3, bw=1000, delay="50ms", intfName1="s2-s3",  intfName2="s3-s2")
    
    net.addLink(cp,      s3, bw=1000, delay="1ms", intfName1="cp-s3",  intfName2="s3-cp")
    net.addLink(upf_cld, s3, bw=1000, delay="1ms", intfName1="upf_cld-s3",  intfName2="s3-upf_cld")
    net.addLink(upf_mec, s2, bw=1000, delay="1ms", intfName1="upf_mec-s2", intfName2="s2-upf_mec")
    
    for i in range(nUE):
        net.addLink(ue_list[i],  s1, bw=1000, delay="1ms", intfName1=f"ue{i+1}-s1",  intfName2=f"s1-ue{i+1}")
    for i in range(ngNB):
        net.addLink(gnb_list[i], s1, bw=1000, delay="1ms", intfName1=f"gnb{i+1}-s1", intfName2=f"s1-gnb{i+1}")
    
    net.addLink(mec_server, s3, bw=1000, delay="5ms", intfName1="mec_server-s3", intfName2="s3-mec_server")

    print(f"*** Open5GS: Init subscriber for UE")
    o5gs   = Open5GS( "172.17.0.2" ,"27017")
    o5gs.removeAllSubscribers()
    add_subscribers(nUE)

    info("\n*** Starting network\n")
    net.start()

    if not AUTOTEST_MODE:
        # spawnXtermDocker("open5gs")
        # spawnXtermDocker("gnb")
        CLI(net)

    net.stop()
