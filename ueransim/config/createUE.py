
def getYaml(nUE):
    for i in range(1, nUE+1):
        # TODO: dividere gli UE in modo pari tra i gNB
        if i == 1 or i == 2:
            ipfinal= "131"
        else:
            ipfinal= "132"
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

        file = open(f"./ueransim/config/open5gs_ue{i}.yaml", "w")
        file.write(yaml)
        file.close()

    return 


if __name__ == '__main__':
  getYaml(6)
