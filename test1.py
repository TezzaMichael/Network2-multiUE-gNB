from python_modules.Open5GS import Open5GS 
import math
import subprocess
import re

def get_ip(name, interface):
    command = f"docker exec {name} ip addr show {interface}"
    ifconfig_output = subprocess.check_output(command, shell=True, universal_newlines=True)
    # Cerca l'indirizzo IP nell'output
    match = re.search(r"inet\s+(\d+\.\d+\.\d+\.\d+)", ifconfig_output)
    if match:
        return match.group(1)  # Restituisci l'indirizzo IP trovato
    else:
        print("Indirizzo IP non trovato nell'output.")
        return None

def get_interface(ue):
    command = f"docker exec {ue} ls /sys/class/net"
    ifconfig_output = subprocess.check_output(command, shell=True, universal_newlines=True)
    return ifconfig_output.strip().split("\n")

def ping_test(container, interface, destination ):
    command = f"docker exec {container} ping -c 8 -n -I {interface} {destination}"
    ping_output = subprocess.check_output(command, shell=True, universal_newlines=True)
    print(ping_output)

def traceroute_test(name, interface, destination):
    command = f"docker exec {name} traceroute -n -i {interface} {destination}"
    ifconfig_output = subprocess.check_output(command, shell=True, universal_newlines=True)
    print(ifconfig_output)

def throughput_test():
    return 0


if __name__ == '__main__':
    O5GS = Open5GS( "172.17.0.2" ,"27017")
    subscribers = O5GS._GetSubscribers()
    nUE = len(subscribers)
    ngNB = math.ceil(nUE/3)


    #########################################
    # BANDWIDTH TEST

    # Get the ip for every upf server
    print("Getting the ip for every upf")
    upf_to_ip_map = {}  # {"upf_name": 192.168...}
    for upf_name in ["upf_cld", "upf_mec"]:
        interfaces = get_interface(upf_name)
        
        for interface in interfaces:
            if interface.startswith("upf"):
                ip = get_ip(upf_name, interface)
                upf_to_ip_map[upf_name] = ip

    # Enter in every upf and start the server 
    print("Starting servers")
    base_port = 6000
    for i, upf_name in enumerate(upf_to_ip_map.keys()):
        # Kill the server if there's one
        command = f"docker exec {upf_name} pkill -2 -f iperf3"
        subprocess.run(command, shell=True, universal_newlines=True)
        # Start the server
        command = f"docker exec {upf_name} iperf3 -s -p {base_port+i}"
        subprocess.Popen(command, shell=True, universal_newlines=True)

    # For every ue test the bandwidth versus the gnb
    print("Running tests")
    for i in range(nUE):
        ue_name = f"ue{i+1}"
        interfaces = get_interface(ue_name)

        for interface in interfaces:
            if not interface.startswith("uesimtun"):
                continue

            dest_ip = None
            dest_port = None
            interface_ip = None
            if interface == "uesimtun0":  # upf_mec
                dest_ip = upf_to_ip_map["upf_mec"]
                dest_port = 6000
                interface_ip = get_ip(ue_name, interface)
            elif interface == "uesimtun1":  # upf_cld
                dest_ip = upf_to_ip_map["upf_cld"]
                dest_port = 6001
                interface_ip = get_ip(ue_name, interface)

            command = f"docker exec ue{i+1} iperf3 -c {dest_ip} -p {dest_port} -B {interface_ip} -t 15"
            output = subprocess.run(command, shell=True, universal_newlines=True)
            print(output)
    
    # Close the servers
    print("Stopping servers")
    for upf_name in upf_to_ip_map.keys():
        command = f"docker exec {upf_name} pkill -2 -f iperf3"
        output = subprocess.run(command, shell=True, universal_newlines=True)
