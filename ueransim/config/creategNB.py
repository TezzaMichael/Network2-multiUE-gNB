
def getYamlgNB(ngNB):
    for i in range(1, ngNB+1):
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



        file = open(f"./ueransim/config/open5gs_gnb{i}.yaml", "w")
        file.write(yaml)
        file.close()

    return 


if __name__ == '__main__':
  getYamlgNB(6)
