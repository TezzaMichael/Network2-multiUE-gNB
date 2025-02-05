import socket
import struct

def icmp_listener():
    """
    Listens for incoming ICMP Echo Request (ping) packets and prints the address of the client.

    This function creates a raw socket to listen for ICMP Echo Requests (ping requests) and prints the
    source address when such a request is received.

    The server will continuously listen for ICMP packets and handle them accordingly.
    """
    
    # Create a raw socket to listen for ICMP packets
    icmp_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    
    # Set a timeout for the socket (optional; to avoid hanging indefinitely)
    icmp_socket.settimeout(5)  # Timeout of 5 seconds
    
    print("Server started.")
    
    # Infinite loop to continuously listen for packets
    while True:
        try:
            # Receive an ICMP packet (maximum size 65565 bytes)
            packet, addr = icmp_socket.recvfrom(65565)
            
            # Extract the ICMP header (start from byte 20 to byte 28)
            icmp_header = packet[20:28]
            
            # Unpack the ICMP header to get type, code, and other fields
            icmp_type, icmp_code, _, _, _ = struct.unpack("bbHHh", icmp_header)
            
            # Check if the packet is an ICMP Echo Request (ping request)
            if icmp_type == 8 and icmp_code == 0:
                # ICMP Echo Request received, print the source address
                print(f"Received a ping request from client: {addr}")
        
        except socket.timeout:
            # Handle socket timeout (if no packet is received within the timeout period)
            pass

if __name__ == "__main__":
    icmp_listener()  # Start the ICMP listener when the script is run
