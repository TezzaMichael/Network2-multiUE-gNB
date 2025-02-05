import os

from comnetsemu.cli import CLI
from comnetsemu.net import Containernet
from mininet.link import TCLink
from mininet.log import info, setLogLevel
from mininet.node import Controller

from python_modules.Open5GS import Open5GS
import sys

import ueransim.config.ue_setup as ue_setup
import ueransim.config.gnb_setup as gnb_setup
import python_modules.ue_configuration as ue_configuration
import json
import math


def instantiate_cp():
    """
    Instantiates the Open5GS Control Plane (CP) as a Docker container with the necessary configurations.

    This function adds the Control Plane (CP) container to the network, binds relevant volumes for logging, 
    configuration, and MongoDB, and initializes the CP container using the specified startup script.

    Returns:
        cp (DockerHost): The instantiated Open5GS Control Plane (CP) Docker container.
    """
    
    # Log message indicating the addition of the Control Plane host
    info("*** Adding Host for open5gs CP\n")
    
    # Set environment variable for the component name
    env["COMPONENT_NAME"] = "cp"
    
    # Add the Docker host for Open5GS CP with necessary configurations
    cp = net.addDockerHost(
        "cp",  # Name of the host
        dimage="my5gc_v2-4-4",  # Docker image for the Open5GS Control Plane
        ip="192.168.0.111/24",  # IP address for the CP container
        dcmd="bash /open5gs/install/etc/open5gs/5gc_cp_init.sh",  # Command to initialize the CP
        docker_args={
            "ports": {"3000/tcp": 3000},  # Map port 3000 for web interface access
            "volumes": {
                prj_folder + "/log": {
                    "bind": "/open5gs/install/var/log/open5gs",  # Bind project log folder to CP logs
                    "mode": "rw",  # Read-write mode
                },
                mongodb_folder: {
                    "bind": "/var/lib/mongodb",  # Bind MongoDB data folder
                    "mode": "rw",  # Read-write mode
                },
                prj_folder + "/open5gs/config": {
                    "bind": "/open5gs/install/etc/open5gs",  # Bind Open5GS config files
                    "mode": "rw",  # Read-write mode
                },
                "/etc/timezone": {
                    "bind": "/etc/timezone",  # Bind timezone file
                    "mode": "ro",  # Read-only mode
                },
                "/etc/localtime": {
                    "bind": "/etc/localtime",  # Bind localtime file
                    "mode": "ro",  # Read-only mode
                },
            },
        },
    )
    
    # Return the instantiated Control Plane Docker container
    return cp

def instantiate_upf_cld():
    """
    Instantiates the Open5GS User Plane Function (UPF) Cloud as a Docker container with the necessary configurations.

    This function adds the UPF Cloud container to the network, binds relevant volumes for logging, 
    configuration, and timezone, and initializes the UPF Cloud container using the specified startup script.

    Returns:
        upf_cld (DockerHost): The instantiated Open5GS User Plane Function (UPF) Cloud Docker container.
    """
    
    # Log message indicating the addition of the User Plane Function (UPF) Cloud host
    info("*** Adding Host for open5gs UPF\n")
    
    # Set environment variable for the component name
    env["COMPONENT_NAME"] = "upf_cld"
    
    # Add the Docker host for Open5GS UPF Cloud with necessary configurations
    upf_cld = net.addDockerHost(
        "upf_cld",  # Name of the host
        dimage="my5gc_v2-4-4",  # Docker image for the Open5GS UPF Cloud
        ip="192.168.0.112/24",  # IP address for the UPF Cloud container
        dcmd="bash /open5gs/install/etc/open5gs/temp/5gc_up_init.sh",  # Command to initialize the UPF Cloud
        docker_args={
            "environment": env,  # Pass environment variables to the container
            "volumes": {
                prj_folder + "/log": {
                    "bind": "/open5gs/install/var/log/open5gs",  # Bind project log folder to UPF logs
                    "mode": "rw",  # Read-write mode
                },
                prj_folder + "/open5gs/config": {
                    "bind": "/open5gs/install/etc/open5gs/temp",  # Bind Open5GS config files
                    "mode": "rw",  # Read-write mode
                },
                "/etc/timezone": {
                    "bind": "/etc/timezone",  # Bind timezone file
                    "mode": "ro",  # Read-only mode
                },
                "/etc/localtime": {
                    "bind": "/etc/localtime",  # Bind localtime file
                    "mode": "ro",  # Read-only mode
                },
            },
            "cap_add": ["NET_ADMIN"],  # Add NET_ADMIN capability to the container
            "sysctls": {"net.ipv4.ip_forward": 1},  # Enable IP forwarding in the container
            "devices": "/dev/net/tun:/dev/net/tun:rwm"  # Grant access to TUN device for networking
        },
    )
    
    # Return the instantiated UPF Cloud Docker container
    return upf_cld

def instantiate_upf_mec():
    """
    Instantiates the Open5GS User Plane Function (UPF) MEC as a Docker container with the necessary configurations.

    This function adds the UPF MEC container to the network, binds relevant volumes for logging, 
    configuration, and timezone, and initializes the UPF MEC container using the specified startup script.

    Returns:
        upf_mec (DockerHost): The instantiated Open5GS User Plane Function (UPF) MEC Docker container.
    """
    
    # Log message indicating the addition of the User Plane Function (UPF) MEC host
    info("*** Adding Host for open5gs UPF MEC\n")
    
    # Set environment variable for the component name
    env["COMPONENT_NAME"] = "upf_mec"
    
    # Add the Docker host for Open5GS UPF MEC with necessary configurations
    upf_mec = net.addDockerHost(
        "upf_mec",  # Name of the host
        dimage="my5gc_v2-4-4",  # Docker image for the Open5GS UPF MEC
        ip="192.168.0.113/24",  # IP address for the UPF MEC container
        dcmd="bash /open5gs/install/etc/open5gs/temp/5gc_up_init.sh",  # Command to initialize the UPF MEC
        docker_args={
            "environment": env,  # Pass environment variables to the container
            "volumes": {
                prj_folder + "/log": {
                    "bind": "/open5gs/install/var/log/open5gs",  # Bind project log folder to UPF logs
                    "mode": "rw",  # Read-write mode
                },
                prj_folder + "/open5gs/config": {
                    "bind": "/open5gs/install/etc/open5gs/temp",  # Bind Open5GS config files
                    "mode": "rw",  # Read-write mode
                },
                "/etc/timezone": {
                    "bind": "/etc/timezone",  # Bind timezone file
                    "mode": "ro",  # Read-only mode
                },
                "/etc/localtime": {
                    "bind": "/etc/localtime",  # Bind localtime file
                    "mode": "ro",  # Read-only mode
                },
            },
            "cap_add": ["NET_ADMIN"],  # Add NET_ADMIN capability to the container
            "sysctls": {"net.ipv4.ip_forward": 1},  # Enable IP forwarding in the container
            "devices": "/dev/net/tun:/dev/net/tun:rwm"  # Grant access to TUN device for networking
        },
    )
    
    # Return the instantiated UPF MEC Docker container
    return upf_mec

def instantiate_mec_server():
    """
    Instantiates the MEC Server as a Docker container with the necessary configurations.

    This function adds the MEC Server container to the network, binds relevant volumes for logging and 
    configuration, and initializes the MEC Server container using the specified startup script.

    Returns:
        mec_server (DockerHost): The instantiated MEC Server Docker container.
    """
    
    # Log message indicating the addition of the MEC Server host
    info("*** Adding MEC SERVER\n")
    
    # Set environment variable for the component name
    env["COMPONENT_NAME"] = "mec_server"
    
    # Add the Docker host for MEC Server with necessary configurations
    mec_server = net.addDockerHost(
        "mec_server",  # Name of the host
        dimage="mec_server",  # Docker image for the MEC Server
        ip="192.168.0.140/24",  # IP address for the MEC Server container
        dcmd="bash /mnt/mec_server/mec_server.sh",  # Command to initialize the MEC Server
        docker_args={
            "environment": env,  # Pass environment variables to the container
            "volumes": {
                prj_folder + "/mec_server": {
                    "bind": "/mnt/mec_server",  # Bind project folder to MEC server
                    "mode": "rw",  # Read-write mode
                },
                prj_folder + "/log": {
                    "bind": "/mnt/log",  # Bind log folder for the MEC server
                    "mode": "rw",  # Read-write mode
                },
                "/etc/timezone": {
                    "bind": "/etc/timezone",  # Bind timezone file
                    "mode": "ro",  # Read-only mode
                },
                "/etc/localtime": {
                    "bind": "/etc/localtime",  # Bind localtime file
                    "mode": "ro",  # Read-only mode
                },
            },
            "cap_add": ["NET_ADMIN"],  # Add NET_ADMIN capability to the container
        },
    )
    
    # Return the instantiated MEC Server Docker container
    return mec_server

def instantiate_gnbs(ngNB):
    """
    Instantiates multiple gNodeBs (gNBs) as Docker containers with the necessary configurations.

    This function adds the specified number of gNB containers to the network, binds relevant volumes for
    logging, configuration, and time-related files, and initializes each gNB container using the specified
    startup script.

    Args:
        ngNB (int): The number of gNodeBs (gNBs) to instantiate.

    Returns:
        list: A list of instantiated gNodeB (gNB) Docker containers.
    """
    
    # Log message indicating the addition of the gNB hosts
    info("*** Adding gNB\n")
    
    # List to hold instantiated gNB Docker containers
    gnb_list = []
    
    # Loop through the range of gNBs to instantiate
    for i in range(1, ngNB + 1):
        # Set the environment variable for the component name (e.g., "gnb1", "gnb2", etc.)
        env["COMPONENT_NAME"] = f"gnb{i}"
        
        # Add the Docker host for each gNB with necessary configurations
        gnb_list.append(net.addDockerHost(
            f"gnb{i}",  # Name of the host (e.g., gnb1, gnb2)
            dimage="myueransim_v3-2-6",  # Docker image for the gNB
            ip=f"192.168.0.{130 + i}/24",  # IP address for the gNB container
            dcmd=f"bash /mnt/ueransim/open5gs_gnb_init.sh {i}",  # Command to initialize the gNB
            docker_args={
                "environment": env,  # Pass environment variables to the container
                "volumes": {
                    prj_folder + "/ueransim/config": {
                        "bind": "/mnt/ueransim",  # Bind project configuration folder
                        "mode": "rw",  # Read-write mode
                    },
                    prj_folder + "/log": {
                        "bind": "/mnt/log",  # Bind log folder
                        "mode": "rw",  # Read-write mode
                    },
                    "/etc/timezone": {
                        "bind": "/etc/timezone",  # Bind timezone file
                        "mode": "ro",  # Read-only mode
                    },
                    "/etc/localtime": {
                        "bind": "/etc/localtime",  # Bind localtime file
                        "mode": "ro",  # Read-only mode
                    },
                    "/dev": {
                        "bind": "/dev",  # Bind /dev directory for device access
                        "mode": "rw",  # Read-write mode
                    },
                },
                "cap_add": ["NET_ADMIN"],  # Add NET_ADMIN capability to the container
                "devices": "/dev/net/tun:/dev/net/tun:rwm"  # Grant access to TUN device for networking
            },
        ))
    
    # Return the list of instantiated gNodeB Docker containers
    return gnb_list

def instantiate_ues(nUE):
    """
    Instantiates multiple User Equipments (UEs) as Docker containers with the necessary configurations.

    This function adds the specified number of UE containers to the network, binds relevant volumes for
    logging, configuration, and time-related files, and initializes each UE container using the specified
    startup script.

    Args:
        nUE (int): The number of User Equipments (UEs) to instantiate.

    Returns:
        list: A list of instantiated UE (User Equipment) Docker containers.
    """
    
    # Log message indicating the addition of the User Equipment (UE) hosts
    info("*** Adding UE\n")
    
    # List to hold instantiated UE Docker containers
    ue_list = []
    
    # Loop through the range of UEs to instantiate
    for i in range(1, nUE + 1):
        # Set the environment variable for the component name (e.g., "ue1", "ue2", etc.)
        env["COMPONENT_NAME"] = f"ue{i}"
        
        # Add the Docker host for each UE with necessary configurations
        ue_list.append(net.addDockerHost(
            f"ue{i}",  # Name of the host (e.g., ue1, ue2)
            dimage="myueransim_v3-2-6",  # Docker image for the UE
            ip=f"192.168.0.{140 + i}/24",  # IP address for the UE container
            dcmd=f"bash /mnt/ueransim/open5gs_ue_init.sh {i}",  # Command to initialize the UE
            docker_args={
                "environment": env,  # Pass environment variables to the container
                "volumes": {
                    prj_folder + "/ueransim/config": {
                        "bind": "/mnt/ueransim",  # Bind project configuration folder
                        "mode": "rw",  # Read-write mode
                    },
                    prj_folder + "/log": {
                        "bind": "/mnt/log",  # Bind log folder for the UE
                        "mode": "rw",  # Read-write mode
                    },
                    "/etc/timezone": {
                        "bind": "/etc/timezone",  # Bind timezone file
                        "mode": "ro",  # Read-only mode
                    },
                    "/etc/localtime": {
                        "bind": "/etc/localtime",  # Bind localtime file
                        "mode": "ro",  # Read-only mode
                    },
                    "/dev": {
                        "bind": "/dev",  # Bind /dev directory for device access
                        "mode": "rw",  # Read-write mode
                    },
                },
                "cap_add": ["NET_ADMIN"],  # Add NET_ADMIN capability to the container
                "devices": "/dev/net/tun:/dev/net/tun:rwm"  # Grant access to TUN device for networking
            },
        ))
    
    # Return the list of instantiated UE Docker containers
    return ue_list

def add_subscribers(nUE):
    """
    Adds subscribers to Open5GS from a JSON configuration file.

    This function reads a JSON file containing subscriber information and adds each subscriber to 
    Open5GS using the `addSubscriber` method. It logs the number of successfully added subscribers.

    Args:
        nUE (int): The number of User Equipment (UE) subscribers to add (though not directly used in the function).
    """
    
    # Generate the subscriber configuration JSON
    ue_configuration.generate_json(nUE)
    
    # Open the subscribers JSON file and load its content
    with open(prj_folder + "/python_modules/subscribers.json", 'r') as f:
        data = json.load(f)

    # Check if "subscribers" key exists in the loaded JSON data
    if "subscribers" in data:
        subscribers = data["subscribers"]
        n = 0
        
        # Iterate over the list of subscribers and add each one to Open5GS
        for subscriber in subscribers:
            n += 1
            o5gs.addSubscriber(subscriber)  # Add subscriber to Open5GS
        
        # Log the number of successfully added subscribers
        info(f"*** Open5GS: Successfully added {n} subscribers")
    else:
        # Log a message if no subscribers are found in the JSON file
        info("*** Open5GS: No subscribers found")


if __name__ == "__main__":
    """
    This script initializes a network of User Equipment (UEs), gNodeBs (gNBs), Control Plane (CP), 
    User Plane Functions (UPFs), and a MEC server, and connects them using Docker containers.
    It sets up the network with specific bandwidth and delay configurations for each link.
    
    The number of UEs must be passed as a command-line argument, and must be between 1 and 10.
    """
    
    # Check if the number of UE (User Equipment) is passed as a command-line argument
    if len(sys.argv) <= 1:
        print("Please, pass the number of UE that you want to generate as parameter")
        sys.exit(-1)
    
    nUE = int(sys.argv[1])  # Command-line argument for the number of UEs
    
    # Validate the number of UEs
    if nUE <= 0 or nUE > 10:
        print("Make sure that the number of UE is between 1 and 10")
        sys.exit(-1)
    
    # Calculate the number of gNodeBs based on the number of UEs
    ngNB = math.ceil(nUE / 3)
    
    # Generate YAML configuration files for UEs and gNBs
    ue_setup.generate_yaml(nUE, ngNB)
    gnb_setup.generate_yaml(ngNB)
    
    # Get AUTOTEST_MODE environment variable (defaults to 0 if not set)
    AUTOTEST_MODE = os.environ.get("COMNETSEMU_AUTOTEST_MODE", 0)
    
    # Set log level for the script
    setLogLevel("info")
    
    # Get the script path and project folder
    script_path = os.path.abspath(__file__)
    prj_folder = os.path.dirname(script_path)
    
    # Get the home path and MongoDB data folder
    homepath = os.getenv("HOME")  # Works only for Linux
    mongodb_folder = f"{homepath}/mongodbdata"
    
    # Initialize environment dictionary
    env = dict()
    
    # Initialize the network with a controller and link type
    net = Containernet(controller=Controller, link=TCLink)
    
    # Instantiate network components (CP, UPF, gNB, UE, MEC Server)
    cp = instantiate_cp()
    upf_cld = instantiate_upf_cld()
    upf_mec = instantiate_upf_mec()
    mec_server = instantiate_mec_server()
    gnb_list = instantiate_gnbs(ngNB)
    ue_list = instantiate_ues(nUE)
    
    # Add controller to the network
    info("*** Add controller\n")
    net.addController("c0")
    
    # Add switches to the network
    info("*** Adding switch\n")
    s1 = net.addSwitch("s1")
    s2 = net.addSwitch("s2")
    s3 = net.addSwitch("s3")
    
    # Add links between switches
    info("*** Adding links\n")
    net.addLink(s1, s2, bw=1000, delay="10ms", intfName1="s1-s2", intfName2="s2-s1")
    net.addLink(s2, s3, bw=1000, delay="50ms", intfName1="s2-s3", intfName2="s3-s2")
    
    # Add links between network components (CP, UPFs, and MEC Server)
    net.addLink(cp, s3, bw=1000, delay="1ms", intfName1="cp-s3", intfName2="s3-cp")
    net.addLink(upf_cld, s3, bw=1000, delay="1ms", intfName1="upf_cld-s3", intfName2="s3-upf_cld")
    net.addLink(upf_mec, s2, bw=1000, delay="1ms", intfName1="upf_mec-s2", intfName2="s2-upf_mec")
    
    # Add links for UEs and gNBs
    for i in range(nUE):
        net.addLink(ue_list[i], s1, bw=1000, delay="1ms", intfName1=f"ue{i+1}-s1", intfName2=f"s1-ue{i+1}")
    
    for i in range(ngNB):
        net.addLink(gnb_list[i], s1, bw=1000, delay="1ms", intfName1=f"gnb{i+1}-s1", intfName2=f"s1-gnb{i+1}")
    
    # Add link between MEC Server and switch
    net.addLink(mec_server, s3, bw=1000, delay="5ms", intfName1="mec_server-s3", intfName2="s3-mec_server")
    
    # Initialize Open5GS and subscribers
    print("*** Open5GS: Init subscriber for UE")
    o5gs = Open5GS("172.17.0.2", "27017")
    o5gs.removeAllSubscribers()
    add_subscribers(nUE)
    
    # Start the network
    info("\n*** Starting network\n")
    net.start()
    
    # If not in AUTOTEST_MODE, launch the CLI for manual control
    if not AUTOTEST_MODE:
        CLI(net)
    
    # Stop the network after the CLI session or test
    net.stop()
