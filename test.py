from python_modules.Open5GS import Open5GS 
import math
import subprocess
import re
import time
import signal
import argparse
import textwrap

class Network:

    def __init__(self, ue_list, gnb_list, upf_mec, upf_cld, cp, mec_server):
        self.ue_list = ue_list
        self.gnb_list = gnb_list
        self.upf_mec = upf_mec
        self.upf_cld = upf_cld
        self.cp = cp
        self.mec_server = mec_server

    def __str__(self):
        result = "Network Configuration:\n"

        # Stampare gli UE
        result += "\nUE List:\n"
        for ue in self.ue_list:
            result += f"{ue}\n"
            result += ue.get_interfaces_info()
        
        # Stampare i gNB
        result += "\ngNB List:\n"
        for gnb in self.gnb_list:
            result += f"{gnb}\n"
            result += gnb.get_interfaces_info()
        
        # Stampare UPF MEC
        result += "\nUPF MEC:\n"
        result += f"{self.upf_mec}\n"
        result += self.upf_mec.get_interfaces_info()

        # Stampare UPF Cloud
        result += "\nUPF Cloud:\n"
        result += f"{self.upf_cld}\n"
        result += self.upf_cld.get_interfaces_info()
        
        # Stampare CP
        result += "\nControl Plane (CP):\n"
        result += f"{self.cp}\n"
        result += self.cp.get_interfaces_info()
        
        # Stampare MEC Server
        result += "\nMEC Server:\n"
        result += f"{self.mec_server}\n"
        result += self.mec_server.get_interfaces_info()

        return result

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
    
    def get_interfaces_info(self):
        """
        Prints all interfaces with their respective IPs.
        """
        interfaces = ""
        if self.interfaces:
            interfaces += f"Interfaces for the component '{self.name}':\n"
            for interface, ip in self.interfaces.items():
                interfaces += f" - {interface}: {ip}\n"
        else:
            interfaces = "The component '{self.name}' has no configured interfaces."
        return interfaces

    def __str__(self):
        """
        String representation of the Component object.
        """
        return f"Component: {self.name}, Interfaces: {len(self.interfaces)}"

def get_network_components(nUE, ngNB):
    ue_list = []
    for i in range(nUE):
        ue_list.append( Component(name=f"ue{i+1}"))
        interfaces = get_interface(f"ue{i+1}")
        for interface in interfaces:
            if interface != "lo" and interface != "eth0":
                ip =get_ip(f"ue{i+1}", interface)
                ue_list[i].add_interface(interface, ip)
    gnb_list = []
    for i in range(ngNB):
        gnb_list.append( Component(name=f"gnb{i+1}"))
        interfaces = get_interface(f"gnb{i+1}")
        for interface in interfaces:
            if interface != "lo" and interface != "eth0":
                ip =get_ip(f"gnb{i+1}", interface)
                gnb_list[i].add_interface(interface, ip)
    upf_mec = Component(name="upf_mec")
    interfaces = get_interface("upf_mec")
    for interface in interfaces:
         if interface != "lo" and interface != "eth0":
            ip =get_ip("upf_mec", interface)
            upf_mec.add_interface(interface, ip)
    upf_cld = Component(name="upf_cld")
    interfaces = get_interface("upf_cld")
    for interface in interfaces:
        if interface != "lo" and interface != "eth0":
            ip =get_ip("upf_cld", interface)
            upf_cld.add_interface(interface, ip)
    cp = Component(name="cp")
    interfaces = get_interface("cp")
    for interface in interfaces:
         if interface != "lo" and interface != "eth0":
            ip =get_ip("cp", interface)
            cp.add_interface(interface, ip)
    mec_server = Component(name="mec_server")
    interfaces = get_interface("mec_server")
    for interface in interfaces:
         if interface != "lo" and interface != "eth0":
            ip = get_ip("mec_server", interface)
            mec_server.add_interface(interface, ip)

    return (ue_list, gnb_list, upf_mec, upf_cld, cp, mec_server) 

def start_tcpdump(upf,interface):
    """Avvia tcpdump in background e stampa l'output in tempo reale."""
    if "s1" in interface:
        cmd = f"docker exec {upf} timeout 4 tcpdump -i {interface} -n -l"
    else:
        cmd = f"docker exec {upf} timeout 12 tcpdump -i {interface} -n -l"
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    return process

def stop_tcpdump(process):
    """Termina tcpdump in modo pulito."""
    if process:
        process.terminate()
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            process.kill()

def print_tcpdump_output(process, ue):
    """Legge l'output di tcpdump in tempo reale e lo stampa."""
    try:
         for line in iter(process.stdout.readline, ''):
            stripped_line = line.strip()  # Rimuove spazi bianchi e newline
            if ue:
                # Controlla se l'IP 192.168.0.140 è presente nella riga
                if ue in stripped_line and "UDP" in stripped_line:
                    print(stripped_line)  # Stampa solo se l'IP è presente
            else:
                print(stripped_line)  # Stampa tutte le righe se gnb è False
     
    except KeyboardInterrupt:
        pass

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
    return ping_output #print(ping_output)

def latency(network):
    for ue in network.ue_list:
        print(f"Test latency for {ue.name}")
        for interface in ue.interfaces:
            if interface == "uesimtun0":
                print(f"-    interface: {interface}")
                print("-    upf_cld")   
                print(ping_test(ue.name, interface, network.upf_cld.interfaces["upf_cld-s3"]))
            elif interface == "uesimtun1":
                print(f"-    interface: {interface}")
                print("-    upf_mec")
                print(ping_test(ue.name, interface, network.upf_mec.interfaces["upf_mec-s2"]))

def bandwidth(network):
    for upf in [network.upf_mec, network.upf_cld]:
        dest_ip = None
        for interface in upf.interfaces:
            if interface.startswith("upf"):
                dest_ip = get_ip(upf.name, interface)

        if dest_ip == None:
            continue

        # Enter in every upf and start the server 
        print("Starting server")

        # Kill the server if there's one
        command = f"docker exec {upf.name} pkill -2 -f iperf3"
        subprocess.run(command, shell=True, universal_newlines=True)
        # Start the server
        command = f"docker exec {upf.name} iperf3 -s"
        subprocess.Popen(command, shell=True, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        print("Iterating over the list of UE")
        for ue in network.ue_list:
            interface_ip = None
            interface_name = None

            for interface in ue.interfaces:
                if upf.name == "upf_mec" and interface == "uesimtun1":  
                    interface_ip = get_ip(ue.name, interface)
                    interface_name = interface
                elif upf.name == "upf_cld" and interface == "uesimtun0":  
                    interface_ip = get_ip(ue.name, interface)
                    interface_name = interface
            
            if not interface_ip:
                continue
                
            command = ["docker", "exec", ue.name, "iperf3", "-c", dest_ip, "-B", interface_ip, "-t", "5"]
            result = subprocess.run(command, capture_output=True, text=True)

            final_result = []
            lines = reversed(result.stdout.splitlines())
            for line in lines:
                final_result.append(line + "\n")
                if line.startswith("[ ID]"):
                    break

            print("".join(reversed(final_result)))
    
        print("Stopping the server")
        command = f"docker exec {upf.name} pkill -2 -f iperf3"
        output = subprocess.run(command, shell=True, universal_newlines=True)

def routing(network):
    ngNB = len(network.gnb_list)
    
    for ue in network.ue_list:
        n = int(re.search(r'(\d+)', ue.name).group(1))
        gnb = f"gnb{(n-1)%ngNB +1}"
        print(f"### Check rounting {ue.name} -> {gnb} ###")
        process = start_tcpdump(gnb, f"{gnb}-s1")
        time.sleep(2)
        print_tcpdump_output(process, ue.interfaces[f"{ue.name}-s1"])
        stop_tcpdump(process) 
        
        for interface in ue.interfaces:
            if interface not in ["uesimtun0", "uesimtun1"]:
                continue

            upf = ""
            if interface == "uesimtun0":
                print(f"### Check rounting {ue.name} -> {gnb} -> upf_cld ###")
                destination = "www.google.com"
                upf = "upf_cld"
                routing = f"Routing: {ue.name}[{interface}] -> {gnb} -> {upf} -> {destination}"

            elif interface == "uesimtun1":
                print(f"### Check routing {ue.name} -> {gnb} -> upf_mec ###")
                destination = network.mec_server.interfaces["mec_server-s3"]
                upf = "upf_mec"
                routing = f"Routing: {ue.name}[{interface}] -> {gnb} -> {upf} -> mec_server"
        
            process1 = start_tcpdump(f"{upf}", "ogstun")
            time.sleep(2)  # Attendi che tcpdump sia pronto

            print(f"### Eseguo il ping {ue.name}[{interface}] -> {destination} ###")
            ping_test(ue.name, interface, destination)

            print(f"### Output tcpdump {upf} ###")
            print_tcpdump_output(process1, None)
            
            print(f"### Arresto tcpdump {upf} ###")
            stop_tcpdump(process1)
            
            print(routing)
            time.sleep(2)

def details(network):
    print(network)

def main():
    # Creazione del parser degli argomenti
    parser = argparse.ArgumentParser(
        description="Un programma di esempio per gestire comandi da riga di comando.",
        formatter_class=argparse.RawTextHelpFormatter,  # Permette di formattare l'help in modo più leggibile
        epilog=textwrap.dedent("""\
        Comandi disponibili per l'opzione -c/--command:
          details    Stampa i dettagli della rete
          latency    Misura la latenza della rete.
          bandwidth  Misura la banda disponibile.
          routing    Visualizza il percorso che i pacchetti percorrono
        """)
    )
    
    parser.add_argument(
        "-c", "--command", 
        type=str, 
        help="Esegui un comando specifico. Usa '-h' per vedere la lista completa."
    )
    args = parser.parse_args()

    command_function = None
    if args.command == "latency":
        command_function = latency
    elif args.command == "bandwidth":
        command_function = bandwidth
    elif args.command == "routing":
        command_function = routing
    elif args.command == "details":
        command_function = details
    elif args.command:
        print(f"Comando '{args.command}' non riconosciuto.\n")
        parser.print_help()
        return
    else:
        # Mostra l'aiuto se non viene passato nessun comando
        parser.print_help()
        return
    print("########### Loading Network ###########")
    O5GS = Open5GS( "172.17.0.2" ,"27017")
    subscribers = O5GS._GetSubscribers()
    nUE = len(subscribers)
    ngNB = math.ceil(nUE/3)
    network = Network(*get_network_components(nUE, ngNB))

    command_function(network)

if __name__ == '__main__':
    main()
