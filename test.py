from python_modules.Open5GS import Open5GS
import math
import subprocess
import re
import time
import argparse
import textwrap
import os
from prettytable import PrettyTable


class Network:
    """Represents a network configuration with various components such as UEs, gNBs, 
    UPF MEC, UPF Cloud, Control Plane, and MEC Server.
    """

    def __init__(self, ue_list, gnb_list, upf_mec, upf_cld, cp, mec_server):
        """Initializes the Network instance.

        Args:
            ue_list (list): List of User Equipment (UE) objects.
            gnb_list (list): List of gNB (gNodeB) objects.
            upf_mec (object): UPF MEC (Multi-access Edge Computing) instance.
            upf_cld (object): UPF Cloud instance.
            cp (object): Control Plane (CP) instance.
            mec_server (object): MEC Server instance.
        """
        self.ue_list = ue_list
        self.gnb_list = gnb_list
        self.upf_mec = upf_mec
        self.upf_cld = upf_cld
        self.cp = cp
        self.mec_server = mec_server
    
    def get_component_list(self):
        return self.ue_list + self.gnb_list + [self.upf_mec] + [self.upf_cld] + [self.cp] + [self.mec_server]

    def __str__(self):
        """Returns a formatted string representation of the network configuration.

        The output includes details for:
        - UE List
        - gNB List
        - UPF MEC
        - UPF Cloud
        - Control Plane (CP)
        - MEC Server

        Returns:
            str: A formatted string describing the network components.
        """
        result = "Network Configuration:\n"

        # Print User Equipment (UE) details
        result += "\nUE List:\n"
        for ue in self.ue_list:
            result += f"{ue}\n"
            result += ue.get_interfaces_info()

        # Print gNB (gNodeB) details
        result += "\ngNB List:\n"
        for gnb in self.gnb_list:
            result += f"{gnb}\n"
            result += gnb.get_interfaces_info()

        # Print UPF MEC details
        result += "\nUPF MEC:\n"
        result += f"{self.upf_mec}\n"
        result += self.upf_mec.get_interfaces_info()

        # Print UPF Cloud details
        result += "\nUPF Cloud:\n"
        result += f"{self.upf_cld}\n"
        result += self.upf_cld.get_interfaces_info()

        # Print Control Plane (CP) details
        result += "\nControl Plane (CP):\n"
        result += f"{self.cp}\n"
        result += self.cp.get_interfaces_info()

        # Print MEC Server details
        result += "\nMEC Server:\n"
        result += f"{self.mec_server}\n"
        result += self.mec_server.get_interfaces_info()

        return result

class Component:
    """Represents a network component with configurable interfaces."""

    def __init__(self, name):
        """
        Initializes a Component object.

        Args:
            name (str): Name of the component.
        """
        self.name = name
        self.ip = ""
        self.interfaces = {}  # Dictionary to store interfaces and their IPs

    def add_interface(self, interface_name, interface_ip):
        """
        Adds or updates an interface in the dictionary.

        Args:
            interface_name (str): Name of the interface (e.g., "eth0").
            interface_ip (str): IP address associated with the interface.
        """
        if self.name in interface_name:
            self.ip = interface_ip
        else:
            self.interfaces[interface_name] = interface_ip

    def remove_interface(self, interface_name):
        """
        Removes an interface from the dictionary if it exists.

        Args:
            interface_name (str): Name of the interface to be removed.

        Returns:
            bool: True if the interface was removed, False if it did not exist.
        """
        if interface_name in self.interfaces:
            del self.interfaces[interface_name]
            return True
        else:
            print(f"The interface '{interface_name}' does not exist.")
            return False

    def get_interfaces_info(self):
        """
        Retrieves information about all configured interfaces.

        Returns:
            str: A formatted string containing all interface names and IPs.
        """
        if self.interfaces:
            interfaces = f"Interfaces for the component '{self.name}':\n"
            for interface, ip in self.interfaces.items():
                interfaces += f" - {interface}: {ip}\n"
        else:
            interfaces = f"The component '{self.name}' has no configured interfaces."
        return interfaces

    def __str__(self):
        """
        Returns a string representation of the Component object.

        Returns:
            str: A summary of the component's name and the number of interfaces.
        """
        return f"Component: {self.name}, Ip: {self.ip}, Interfaces: {len(self.interfaces)}"

def get_network_components(nUE, ngNB):
    """
    Creates and initializes network components, including UEs, gNBs, UPFs, CP, and MEC server.

    Args:
        nUE (int): Number of User Equipment (UE) components to create.
        ngNB (int): Number of gNodeB (gNB) components to create.

    Returns:
        tuple: A tuple containing:
            - ue_list (list): List of UE components.
            - gnb_list (list): List of gNB components.
            - upf_mec (Component): UPF MEC component.
            - upf_cld (Component): UPF Cloud component.
            - cp (Component): Control Plane component.
            - mec_server (Component): MEC Server component.
    """
    
    ue_list = []
    for i in range(nUE):
        ue = Component(name=f"ue{i+1}")
        interfaces = get_interface(f"ue{i+1}")
        
        # Add all interfaces except "lo" (loopback) and "eth0" (default interface)
        for interface in interfaces:
            if interface not in {"lo", "eth0"}:
                ip = get_ip(f"ue{i+1}", interface)
                ue.add_interface(interface, ip)
        
        ue_list.append(ue)

    gnb_list = []
    for i in range(ngNB):
        gnb = Component(name=f"gnb{i+1}")
        interfaces = get_interface(f"gnb{i+1}")
        
        for interface in interfaces:
            if interface not in {"lo", "eth0"}:
                ip = get_ip(f"gnb{i+1}", interface)
                gnb.add_interface(interface, ip)
        
        gnb_list.append(gnb)

    # Initialize UPF MEC component
    upf_mec = Component(name="upf_mec")
    interfaces = get_interface("upf_mec")
    for interface in interfaces:
        if interface not in {"lo", "eth0"}:
            ip = get_ip("upf_mec", interface)
            upf_mec.add_interface(interface, ip)

    # Initialize UPF Cloud component
    upf_cld = Component(name="upf_cld")
    interfaces = get_interface("upf_cld")
    for interface in interfaces:
        if interface not in {"lo", "eth0"}:
            ip = get_ip("upf_cld", interface)
            upf_cld.add_interface(interface, ip)

    # Initialize Control Plane (CP) component
    cp = Component(name="cp")
    interfaces = get_interface("cp")
    for interface in interfaces:
        if interface not in {"lo", "eth0"}:
            ip = get_ip("cp", interface)
            cp.add_interface(interface, ip)

    # Initialize MEC Server component
    mec_server = Component(name="mec_server")
    interfaces = get_interface("mec_server")
    for interface in interfaces:
        if interface not in {"lo", "eth0"}:
            ip = get_ip("mec_server", interface)
            mec_server.add_interface(interface, ip)

    return ue_list, gnb_list, upf_mec, upf_cld, cp, mec_server

def start_tcpdump(upf, interface):
    """Starts tcpdump in the background and prints the output in real-time."""
    
    # If the interface contains "s1", set a timeout of 4 seconds
    if "s1" in interface:
        cmd = f"docker exec {upf} timeout 4 tcpdump -i {interface} -n -l"
    else:
        # Otherwise, set a timeout of 12 seconds
        cmd = f"docker exec {upf} timeout 12 tcpdump -i {interface} -n -l"
    
    # Execute the tcpdump command inside the Docker container
    process = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
    )
    
    return process

def stop_tcpdump(process):
    """Gracefully terminates the tcpdump process."""
    
    if process:
        process.terminate()  # Attempt to terminate the process
        
        try:
            process.wait(timeout=2)  # Wait up to 2 seconds for termination
        except subprocess.TimeoutExpired:
            process.kill()  # Force kill the process if it doesn't terminate in time

def print_tcpdump_output(process, ue):
    """Reads tcpdump output in real-time and prints it."""
    
    try:
        output = ""
        for line in iter(process.stdout.readline, ''):
            stripped_line = line.strip()  # Remove whitespace and newline characters
            
            if ue:
                # Check if the specified IP (e.g., 192.168.0.140) is present in the line
                if ue in stripped_line and "UDP" in stripped_line:
                    print(stripped_line)  # Print only if the IP is found
                    output += " " + stripped_line
            else:
                print(stripped_line)  # Print all lines if no UE filter is provided
                output += " " + stripped_line
            
        return output
                
    except KeyboardInterrupt:
        pass  # Handle interruption gracefully

def get_ip(name, interface):
    """
    Retrieves the IPv4 address of a specified network interface within a Docker container.

    Args:
        name (str): Name of the Docker container.
        interface (str): Name of the network interface (e.g., "eth1").

    Returns:
        str or None: The IPv4 address of the interface if found, otherwise None.
    """
    
    command = f"docker exec {name} ip addr show {interface}"
    
    try:
        # Execute the command and capture the output
        ifconfig_output = subprocess.check_output(command, shell=True, universal_newlines=True)
        
        # Search for an IPv4 address pattern
        match = re.search(r"inet\s+(\d+\.\d+\.\d+\.\d+)", ifconfig_output)
        
        if match:
            return match.group(1)
        else:
            print(f"IP address not found for interface '{interface}' in container '{name}'")
            return None

    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        return None

def get_interface(ue):
    """
    Retrieves the list of network interfaces available in a Docker container.

    Args:
        ue (str): Name of the Docker container.

    Returns:
        list: A list of network interface names available in the container.
    """
    
    command = f"docker exec {ue} ls /sys/class/net"
    
    try:
        # Execute the command and capture the output
        ifconfig_output = subprocess.check_output(command, shell=True, universal_newlines=True)
        
        # Return the list of interfaces, removing any trailing whitespace
        return ifconfig_output.strip().split("\n")

    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        return []

def ping_test(container, interface, destination):
    """
    Performs a ping test from a specified network interface within a Docker container.

    Args:
        container (str): Name of the Docker container.
        interface (str): Network interface to use for the ping test.
        destination (str): IP address or hostname to ping.

    Returns:
        str: The output of the ping command.

    Raises:
        subprocess.CalledProcessError: If the ping command fails.
    """
    
    command = f"docker exec {container} ping -c 8 -n -I {interface} {destination}"
    
    try:
        # Execute the ping command and capture the output
        ping_output = subprocess.check_output(command, shell=True, universal_newlines=True)
        return ping_output

    except subprocess.CalledProcessError as e:
        print(f"Ping test failed: {e}")
        return None

def latency(network):
    """
    Tests the latency between User Equipment (UE) and network components (UPF Cloud, UPF MEC).
    
    Iterates through all UEs in the network and pings the respective network components 
    based on the interface type ('uesimtun0' or 'uesimtun1').
    
    Args:
        network (Network): The network object containing UEs, UPF Cloud, and UPF MEC components.
    """

    results = []
    # Loop through all UEs in the network
    for ue in network.ue_list:
        print(f"Test latency for {ue.name}")
        
        for interface in ue.interfaces:
            if interface == "uesimtun0":
                destination = network.upf_cld
            elif interface == "uesimtun1":
                destination = network.upf_mec
            else:
                continue

            print(f"-    interface: {interface}")
            print(f"-    {destination.name}")
            # Perform the ping test and print the result
            ping_output = ping_test(ue.name, interface, destination.ip)
            result = ""
            if not ping_output:
                result = "Error"
            elif "SO_BINDTODEVICE" in ping_output:
                result = "Not Found"
            else:
                match = re.search(r"(\d+) packets transmitted, (\d+) received", ping_output)
                if match:
                    transmitted = int(match.group(1))
                    received = int(match.group(2))
                    result = f"{received}/{transmitted}"
                else: 
                    result = "Error"

            results.append((f"{ue.name}[{interface}]", destination.name, result))
            
            print(ping_output)

    field_names = ["From", "To", "Result"] 
    print_table(field_names, results, True)

def bandwidth(network):
    """
    Measures the available bandwidth between User Equipment (UE) and UPF components (MEC, Cloud).

    This function starts an iperf3 server on each UPF component (MEC and Cloud), then iterates over 
    the UEs to perform bandwidth tests using iperf3 between the UEs and the UPFs.

    Args:
        network (Network): The network object containing UEs, UPF Cloud, and UPF MEC components.
    """
    
    results = []

    # Iterate over the UPF components (MEC and Cloud)
    for upf in [network.upf_mec, network.upf_cld]:
       
        # Starting the iperf3 server on the current UPF component
        print(f"Starting server {upf.name}")
        
        # Kill any existing iperf3 server process (if any)
        command = f"docker exec {upf.name} pkill -2 -f iperf3"
        subprocess.run(command, shell=True, universal_newlines=True)
        
        # Start the iperf3 server
        command = f"docker exec {upf.name} iperf3 -s"
        subprocess.Popen(command, shell=True, universal_newlines=True, 
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Iterate over the list of UEs to run bandwidth tests
        print("Iterating over the list of UE")

        for ue in network.ue_list:
            interface_ip = None
            interface = None

            # Find the IP address for the appropriate UE interface
            if upf.name == "upf_mec":
                interface = "uesimtun1"
            elif upf.name == "upf_cld":
                interface = "uesimtun0"
                    
            interface_ip = ue.interfaces[interface]
            # Skip if no interface IP is found for the current UE
            if not interface_ip:
                continue
            
            print(f"## {ue.name}[{interface}] ##")
            # Run the iperf3 bandwidth test from the UE to the UPF
            command = ["docker", "exec", ue.name, "iperf3", "-c", upf.ip, "-B", interface_ip, "-t", "5"]
            result = subprocess.run(command, capture_output=True, text=True)

            # Process and print the result of the bandwidth test
            final_result = []
            lines = reversed(result.stdout.splitlines())
            for line in lines:
                final_result.append(line + "\n")
                if line.startswith("[ ID]"):
                    break

            result = "".join(reversed(final_result))
            print(result)

            # Regular expression to match the bitrate (Mbits/sec)
            bitrate_pattern = r'(\d+\.\d+) Mbits/sec'
            # Find all matches
            bitrate_matches = re.findall(bitrate_pattern, result)

            results.append((upf.name, ue.name, *bitrate_matches))


        # Stop the iperf3 server after the tests
        print("Stopping the server")
        command = f"docker exec {upf.name} pkill -2 -f iperf3"
        subprocess.run(command, shell=True, universal_newlines=True)
    
    field_names = ["Server", "Host", "H->S (Mbits/sec)", "S->H (Mbits/sec)"]
    print_table(field_names, results, True)

def routing(network):
    """
    Simulates and checks the routing path for User Equipment (UE) across different network components 
    including gNB, UPF Cloud, UPF MEC, and the MEC server. It also captures and analyzes network traffic 
    using tcpdump and performs ping tests for routing validation.

    Args:
        network (Network): The network object containing UEs, gNBs, UPFs, and the MEC server.
    """
    
    ngNB = len(network.gnb_list)  # Get the number of gNBs in the network
    
    results= [] 

    # Iterate through all User Equipment (UE) in the network
    for ue in network.ue_list:
        match = re.search(r'(\d+)', ue.name)  # Extract the number from the UE's name
        
        if match:
            n = int(match.group(1))  # Convert the matched group to an integer (UE number)
        else:
            continue  # Skip if the match is not found
        
        # Determine the corresponding gNB for the current UE
        gnb = f"gnb{(n-1)%ngNB + 1}"
        print(f"### Check routing {ue.name} -> {gnb} ###")
        
        # Start tcpdump to capture traffic on the gNB's s1 interface
        process = start_tcpdump(gnb, f"{gnb}-s1")
        time.sleep(2)  # Wait for tcpdump to start
        
        # Print tcpdump output for the current UE
        print_tcpdump_output(process, ue.ip)
        stop_tcpdump(process)  # Stop tcpdump after capturing traffic
        
        # Iterate through the interfaces of the current UE to simulate routing
        for interface in ue.interfaces:
            if interface not in ["uesimtun0", "uesimtun1"]:
                continue  # Skip interfaces that are not relevant for routing tests

            upf = ""
            destination = ""
            routing = ""
            
            # Simulate routing via UPF Cloud for "uesimtun0" interface
            if interface == "uesimtun0":
                print(f"### Check routing {ue.name} -> {gnb} -> upf_cld ###")
                destination = "www.google.com"  # Set the destination for UPF Cloud
                upf = "upf_cld"
                routing = f"Routing: {ue.name}[{interface}] -> {gnb} -> {upf} -> {destination}"
            
            # Simulate routing via UPF MEC for "uesimtun1" interface
            elif interface == "uesimtun1":
                print(f"### Check routing {ue.name} -> {gnb} -> upf_mec ###")
                destination = network.mec_server.ip  # Get MEC server IP
                upf = "upf_mec"
                routing = f"Routing: {ue.name}[{interface}] -> {gnb} -> {upf} -> mec_server"
            
            # Start tcpdump on the selected UPF (MEC or Cloud)
            process1 = start_tcpdump(f"{upf}", "ogstun")
            time.sleep(2)  # Wait for tcpdump to be ready
            
            # Perform a ping test from UE to the destination
            print(f"### Ping {ue.name}[{interface}] -> {destination} ###")
            ping_test(ue.name, interface, destination)
            
            # Display tcpdump output for the selected UPF
            print(f"### Output tcpdump {upf} ###")
            process_output = print_tcpdump_output(process1, None)
            
            # Stop tcpdump after completing the test
            print(f"### Stopping tcpdump {upf} ###")
            stop_tcpdump(process1)
            
            # Print the routing path
            print(routing)
            time.sleep(2)  # Sleep before proceeding to the next test

            # Parse output to print in the table 
            captured_match = re.search(r'(\d+) packets captured', process_output)
            captured = int(captured_match.group(1)) if captured_match else None

            received_match = re.search(r'(\d+) packets received by filter', process_output)
            received = int(received_match.group(1)) if received_match else None

            routing = routing.replace("Routing: ", "")
            results.append((routing, f"{captured}/{received}"))

    field_names = ["Routing", "Result"] 
    print_table(field_names, results, True)

def details(network):
    """
    Prints the details of the entire network configuration, including UEs, gNBs, UPFs, and the MEC server.

    Args:
        network (Network): The network object containing all components (UEs, gNBs, UPFs, and MEC server).
    """
    print(network)  # Print the full network details (invokes the __str__ method of the Network class)
    field_names = ["Component name", "ip", "interfaces"]
    result = []

    for component in network.get_component_list():
        interfaces = " ".join([f"{name}:{ip}" for name, ip in component.interfaces.items()])
        result.append((component.name, component.ip, interfaces))
    print_table(field_names, result, True)
    
def print_table(field_names, rows, clear_screen=False):
    """
    Prints a table on the screen representing the user provided informations

    Args:
        field_names (list): List containing the headers of the table 
        rows (list): List containing the values to display
        clear_srceen (bool): should the function clear the previous outputs on the terminal?
    """
    # Print the results in a table for better readability
    table = PrettyTable()
    table.field_names = field_names

    # Add the data to the table
    for row in rows:
        if len(row) == len(table.field_names):
            table.add_row(row)
    
    if clear_screen:
        os.system("clear")  

    print(table)


def main():
    """
    Main function that handles command-line arguments, sets up the network components, 
    and executes the appropriate command based on user input.
    """
    
    # Create the argument parser for command-line options
    parser = argparse.ArgumentParser(
        description="A sample program to handle command-line commands.",
        # Allows formatting help text in a more readable way
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=textwrap.dedent("""\
        Available commands for the -c/--command option:
          details    Prints network details.
          latency    Measures network latency.
          bandwidth  Measures available bandwidth.
          routing    Displays the route packets take.
        """)
    )

    # Define the command-line argument for selecting a command
    parser.add_argument(
        "-c", "--command",
        type=str,
        help="Execute a specific command. Use '-h' to see the full list."
    )

    # Parse the command-line arguments
    args = parser.parse_args()

    # Initialize the function variable to hold the selected command
    command_function = None

    # Match the provided command with the corresponding function
    if args.command == "latency":
        command_function = latency
    elif args.command == "bandwidth":
        command_function = bandwidth
    elif args.command == "routing":
        command_function = routing
    elif args.command == "details":
        command_function = details
    elif args.command:
        print(f"Command '{args.command}' not recognized.\n")
        parser.print_help()
        return
    else:
        # Show help if no command is provided
        parser.print_help()
        return

    # Initialize the network and print a message
    print("########### Loading Network ###########")
    
    # Initialize Open5GS object (mocked with IP and port for this example)
    O5GS = Open5GS("172.17.0.2", "27017")
    
    # Fetch subscribers from Open5GS
    subscribers = O5GS._GetSubscribers()
    
    # Calculate the number of UEs and gNBs based on the number of subscribers
    nUE = len(subscribers)
    ngNB = math.ceil(nUE / 3)
    
    # Get network components and create the network instance
    network = Network(*get_network_components(nUE, ngNB))
    
    # Execute the selected command with the network object
    command_function(network)


if __name__ == '__main__':
    main()
