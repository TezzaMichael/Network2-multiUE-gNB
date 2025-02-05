import os

def generate_yaml(ngNB):
    """
    Deletes all existing 'open5gs_gnb*' files in the current directory and generates new YAML configuration files 
    for the specified number of gNodeBs (ngNB).

    This function creates a YAML configuration for each gNodeB with essential parameters like 
    MCC (Mobile Country Code), MNC (Mobile Network Code), Cell Identity, IP addresses for different
    interfaces (Radio Link, N2, N3), and other parameters required for the gNB setup. The configuration
    is saved to a file for each gNodeB.

    Args:
        ngNB (int): The number of gNodeBs to generate YAML configurations for.

    Returns:
        None
    """
    
    # Get the current directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Delete all existing 'open5gs_gnb*' files in the current directory
    for file_name in os.listdir(script_dir):
        if file_name.startswith("open5gs_gnb") and file_name.endswith(".yaml"):
            os.remove(os.path.join(script_dir, file_name))
            print(f"Deleted existing file: {file_name}")
    
    # Loop through the number of gNodeBs to create their configurations
    for i in range(1, ngNB + 1):
        # Generate the YAML configuration content for each gNB
        yaml = f"""
mcc: '001'         # Mobile Country Code value
mnc: '01'          # Mobile Network Code value (2 or 3 digits)

nci: '0x000000010'  # NR Cell Identity (36-bit)
idLength: 32        # NR gNB ID length in bits [22...32]
tac: 1              # Tracking Area Code

linkIp: 192.168.0.{130+i}   # gNB's local IP address for Radio Link Simulation (Usually same with local IP)
ngapIp: 192.168.0.{130+i}   # gNB's local IP address for N2 Interface (Usually same with local IP)
gtpIp: 192.168.0.{130+i}    # gNB's local IP address for N3 Interface (Usually same with local IP)

# List of AMF address information
amfConfigs:
  - address: 192.168.0.111
    port: 38412

# List of supported S-NSSAIs by this gNB
slices:
  - sst: 1
    sd: 1
  - sst: 2
    sd: 1

# Indicates whether or not SCTP stream number errors should be ignored.
ignoreStreamIds: true
"""
        # Write the generated YAML configuration to a file
        with open(f"./ueransim/config/open5gs_gnb{i}.yaml", "w") as file:
            file.write(yaml)

    # Return after completing the YAML generation
    return

if __name__ == '__main__':
    generate_yaml(6)  # Generate YAML for 6 gNBs
