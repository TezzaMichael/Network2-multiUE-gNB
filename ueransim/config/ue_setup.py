import os

def generate_yaml(nUE, gnNB):
    """
    Deletes all existing 'open5gs_ue*' files in the current directory and generates new YAML configuration files 
    for the specified number of User Equipments (UEs).

    This function creates a YAML configuration for each UE with essential parameters such as IMSI, 
    Mobile Country Code (MCC), Mobile Network Code (MNC), Authentication Management Field (AMF), 
    Device IMEI, PDU session information, and encryption configuration. The configuration is saved 
    to a file for each UE.

    Args:
        nUE (int): The number of User Equipments (UEs) to generate YAML configurations for.
        gnNB (int): The number of gNodeBs, used to determine the IP address for each UE.

    Returns:
        None
    """
    
    # Get the current directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Delete all existing 'open5gs_ue*' files in the current directory
    for file_name in os.listdir(script_dir):
        if file_name.startswith("open5gs_ue") and file_name.endswith(".yaml"):
            os.remove(os.path.join(script_dir, file_name))
            print(f"Deleted existing file: {file_name}")
    
    # Loop through the number of UEs (nUE) to generate their configurations
    for i in range(1, nUE + 1):
        # Calculate the final gNB IP address for the UE
        ipfinal = str(131 + (i - 1) % gnNB)

        # Generate the YAML configuration content for each UE
        yaml = f"""
# IMSI number of the UE. IMSI = [MCC|MNC|MSISDN] (In total 15 or 16 digits)
supi: 'imsi-0010112345678{i:02d}'
# Mobile Country Code value of HPLMN
mcc: '001'
# Mobile Network Code value of HPLMN (2 or 3 digits)
mnc: '01'

# Permanent subscription key
key: '8baf473f2f8fd09487cccbd7097c6862'
# Operator code (OP or OPC) of the UE
op: '11111111111111111111111111111111'
# This value specifies the OP type and it can be either 'OP' or 'OPC'
opType: 'OP'
# Authentication Management Field (AMF) value
amf: '8000'
# IMEI number of the device. It is used if no SUPI is provided
imei: '3569380356438{i:02d}'
# IMEISV number of the device. It is used if no SUPI and IMEI is provided
imeiSv: '43708161258161{i:02d}'

# List of gNB IP addresses for Radio Link Simulation
gnbSearchList:
  - 192.168.0.{ipfinal}

# UAC Access Identities Configuration
uacAic:
  mps: false
  mcs: false

# UAC Access Control Class
uacAcc:
  normalClass: 0
  class11: false
  class12: false
  class13: false
  class14: false
  class15: false

# Initial PDU sessions to be established
sessions:
  - type: 'IPv4'
    # apn: 'internet'
    slice:
      sst: 1
      sd: 1
    emergency: false
  - type: 'IPv4'
    # apn: 'mec'
    slice:
      sst: 2
      sd: 1
    emergency: false

# Configured NSSAI for this UE by HPLMN
configured-nssai:
  - sst: 1
    sd: 1
  - sst: 2
    sd: 1

# Default Configured NSSAI for this UE
default-nssai:
  - sst: 1
    sd: 1

# Supported encryption algorithms by this UE
integrity:
  IA1: true
  IA2: true
  IA3: true

# Supported integrity algorithms by this UE
ciphering:
  EA1: true
  EA2: true
  EA3: true

# Integrity protection maximum data rate for user plane
integrityMaxRate:
  uplink: 'full'
  downlink: 'full'
"""
        # Write the generated YAML configuration to a file
        with open(f"./ueransim/config/open5gs_ue{i}.yaml", "w") as file:
            file.write(yaml)

    # Return after completing the YAML generation
    return


if __name__ == '__main__':
    generate_yaml(11, 3)  # Generate YAML for 11 UEs and 3 gNBs
