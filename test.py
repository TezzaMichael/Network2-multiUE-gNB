from python_modules.Open5GS import Open5GS 
import math
import subprocess
import re

class Component:

    def __init__(self, name):
        """
        Initializes a Component object.

        :param name: Name of the component
        """
        self.name = name
        self.interfaces = {}  # Dictionary to store interfaces and their data
     
    def add_interface(self, interface_name, interface_ip):
        """
        Adds or updates an interface in the dictionary.

        :param interface_name: Name of the interface (e.g., "eth0")
        :param interface_ip: IP associated with the interface
        """
        self.interfaces[interface_name] = interface_ip

    def remove_interface(self, interface_name):
        """
        Removes an interface from the dictionary.

        :param interface_name: Name of the interface to be removed
        """
        if interface_name in self.interfaces:
            del self.interfaces[interface_name]
        else:
            print(f"The interface {interface_name} does not exist.")
    
    def show_interfaces(self):
        """
        Prints all interfaces with their respective IPs.
        """
        if self.interfaces:
            print(f"Interfaces for the component '{self.name}':")
            for interface, ip in self.interfaces.items():
                print(f" - {interface}: {ip}")
        else:
            print(f"The component '{self.name}' has no configured interfaces.")

    def __str__(self):
        """
        String representation of the Component object.
        """
        return f"Component: {self.name}, Interfaces: {len(self.interfaces)}"

def network(nUE, ngNB):
    net = []
    for i in range(nUE):
        net.append( Component(name=f"ue{i+1}"))
        interfaces = get_interface(f"ue{i+1}")
        for interface in interfaces:
            if interface != "lo" and interface != "eth0":
                ip =get_ip(f"ue{i+1}", interface)
                add_interface(net, f"ue{i+1}", interface, ip)
        print(net[i])
        net[i].show_interfaces()
    print('\n')
    for i in range(ngNB):
        net.append( Component(name=f"gnb{i+1}"))
        interfaces = get_interface(f"gnb{i+1}")
        for interface in interfaces:
            if interface != "lo" and interface != "eth0":
                ip =get_ip(f"gnb{i+1}", interface)
                add_interface(net, f"gnb{i+1}", interface, ip)
        print(net[nUE+i])
        net[nUE+i].show_interfaces()
    print('\n')
    net.append( Component(name="upf_mec"))
    interfaces = get_interface("upf_mec")
    for interface in interfaces:
         if interface != "lo" and interface != "eth0":
            ip =get_ip("upf_mec", interface)
            add_interface(net, "upf_mec", interface, ip)
    print(net[-1])
    net[-1].show_interfaces()
    print('\n')
    net.append( Component(name="upf_cld"))
    interfaces = get_interface("upf_cld")
    for interface in interfaces:
        if interface != "lo" and interface != "eth0":
            ip =get_ip("upf_cld", interface)
            add_interface(net, "upf_cld", interface, ip)
    print(net[-1])
    net[-1].show_interfaces()
    print('\n')
    net.append( Component(name="cp"))
    interfaces = get_interface("cp")
    for interface in interfaces:
         if interface != "lo" and interface != "eth0":
            ip =get_ip("cp", interface)
            add_interface(net, "cp", interface, ip)
    print(net[-1])
    net[-1].show_interfaces()
    print('\n')
    return net 

def add_interface(network_list, network_name, interface_name, interface_ip):
    for network in network_list:
        if network.name == network_name:  # Search for the matching name
            network.add_interface(interface_name, interface_ip)
            return
    print(f"Network with name '{network_name}' not found.")

def get_ip(name, interface):
    command = f"docker exec {name} ip addr show {interface}"
    ifconfig_output = subprocess.check_output(command, shell=True, universal_newlines=True)
    # Find IPv4
    match = re.search(r"inet\s+(\d+\.\d+\.\d+\.\d+)", ifconfig_output)
    if match:
        return match.group(1)
    else:
        print("IP not found")
        return None

def get_interface(ue):
    command = f"docker exec {ue} ls /sys/class/net"
    ifconfig_output = subprocess.check_output(command, shell=True, universal_newlines=True)
    return ifconfig_output.strip().split("\n")

def ping_test(container, interface, destination ):
    command = f"docker exec {container} ping -c 8 -n -I {interface} {destination}"
    ping_output = subprocess.check_output(command, shell=True, universal_newlines=True)
    print(ping_output)

def throughput_test():
    return 0


if __name__ == '__main__':
    O5GS = Open5GS( "172.17.0.2" ,"27017")
    subscribers = O5GS._GetSubscribers()
    nUE = len(subscribers)
    ngNB = math.ceil(nUE/3)
    print(f"TESTING NETWORK 5G UE: {nUE} GNB: {ngNB}")
    print("--------- SHOW DETAILS ----------")   
    net = network(nUE, ngNB)
    print("----------------------------------")
    #########################################
    # PING TEST
    print("-------- LATENCY TEST ---------")
    get_interface("gnb1")
    get_ip("gnb1", "gnb1-s1")
    
    for i in range(nUE) :
        print(f"Test ping for ue{i+1}")
        interfaces = get_interface(f"ue{i+1}")[3:]
        for interface in interfaces:
            print(f"-    interface: {interface}")
            if interface == "uesimtun0":
                print("-    upf_cld")
                ip_upf = get_ip(f"upf_cld", get_interface("upf_cld")[3])
                ping_test(f"ue{i+1}", interface, ip_upf)
            else:
                print("-    upf_mec")
                ip_upf = get_ip(f"upf_mec", get_interface("upf_mec")[3])
                ping_test(f"ue{i+1}", interface, ip_upf)    
    print("--------------------------------------------")
    #########################################
    # BANDWIDTH TEST
    print("---------- BANDWIDTH TEST -----------------")
    #docker exec {ue} iperf3 -c {destination} -B {interface_ip} -t 15
    for i in range(nUE):
        ue = f"ue{i+1}"
        destination = "192.168.1.112" #113
        interface_ip = get_ip(ue, "uesimtun0")
        command = f"docker exec {ue} iperf3 -c {destination} -B {interface_ip} -t 15"
        test = subprocess.check_output(command, shell=True, universal_newlines=True)
        print(test)

    # Get the ip for every gnb
    gnb_map = {}
    for i in range(ngNB) :
        gnb_name = f"gnb{i+1}"
        interfaces = get_interface(gnb_name)
        
        for interface in interfaces:
            if interface.startswith(gnb_name):
                ip = get_ip(gnb_name, interface)
                gnb_map[gnb_name] = ip


    # Enter in every gnb and start listening for new connections
    base_port = 6000
    for i, gnb_name in enumerate(gnb_map.keys()):
        command = f"docker exec {gnb_name} iperf3 -s -p {base_port+i} -1"
        subprocess.Popen(command, shell=True, universal_newlines=True)

    # For every ue test the bandwidth versus the gnb
    for i in range(nUE):
        ue_name = f"ue{i+1}"
        interfaces = get_interface(ue_name)

        for interface in interfaces:
            if interface.startswith(ue_name):
                for j, gnb_ip in enumerate(gnb_map.values()):
                    command = f"docker exec {ue_name} iperf3 -c {gnb_ip} -p {base_port+i}"
                    config_output = subprocess.check_output(command, shell=True, universal_newlines=True)
                    print(config_output)





