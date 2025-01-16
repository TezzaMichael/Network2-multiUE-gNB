# 5G Network Simulation in Communetsemu  

This project involves the creation of a dynamic 5G network using **Communetsemu**, where both **User Equipment (UE)** and **gNodeBs (gNB)** are dynamically managed. The system automatically determines the correct number of gNBs based on the user-defined number of UEs, ensuring that each gNB supports a maximum of 3 UEs.  

---

## **Project Overview**  

The goal is to simulate a flexible and scalable 5G network that adapts to different numbers of connected UEs. The system automatically calculates the required infrastructure and distributes UEs across the gNBs, maintaining load balance and ensuring optimal performance.  

---

## **Key Features**  

### 1. **Dynamic UE and gNB Allocation**  
- The user specifies the desired number of UEs as an input.  
- The system calculates the number of gNBs required based on the rule:
 **Number of gNBs** = ⌈Number of UEs / 3⌉
 (where `⌈x⌉` represents rounding up).  

 For example:
 5 UEs → 2 gNBs (3 UEs on the first gNB, 2 on the second).  
 10 UEs → 4 gNBs.  

### 2. **Balanced Distribution of UEs**  
- UEs are evenly distributed among the gNBs to ensure balanced load distribution.  

### 3. **Network Architecture**  
The simulated network includes the following components:  
- **5G Core**:  
  AMF, SMF, UPF, and other core components for signaling and data traffic management.  
- **gNodeBs (gNBs)**:  
  Serve as radio access points connecting UEs to the 5G core.  
- **User Equipment (UEs)**:  
  Simulates end-user devices connected to the network.  

### 4. **Support for Mobility**  
- The simulation can model scenarios where UEs and gNBs move dynamically, testing coverage and handover scenarios.  

### 5. **Automation via Scripting**  
- The network setup is fully automated, reducing the need for manual configuration.  
- The script dynamically creates the required number of gNBs and distributes the UEs, allowing rapid and efficient network deployment.  

---

## **How It Works**  

1. **User Input**:  
 The user specifies the number of UEs.  

2. **gNB Calculation**:  
 The script computes the required number of gNBs using the formula:
 **Number of gNBs** = ⌈Number of UEs / 3⌉

3. **Network Creation**:  
- The system creates the necessary gNBs and UEs.  
- UEs are evenly distributed across the gNBs.  

4. **Simulation Execution**:  
Once configured, the 5G network simulation runs in **Communetsemu**, enabling performance tests and analysis.  

---

## **Use Cases**  

1. **Scalability Testing**:  
- Evaluate network performance with increasing numbers of UEs.  

2. **Mobility Simulation**:  
- Test how the network performs when UEs and gNBs move dynamically.  

3. **Performance Analysis**:  
- Measure metrics like throughput, latency, and handover efficiency.  

---

## **Benefits**  

- **Flexibility**: Quickly adapt the network to different UE scenarios.  
- **Efficiency**: Automatic load balancing across gNBs avoids congestion and improves performance.  
- **Scalability**: The system can handle various scales, making it suitable for testing large and small networks.  

---
## Prerequisites

- Comnetsemu [[link](https://git.comnets.net/public-repo/comnetsemu)]
- PyMongo

## **Getting Started**  

1. Clone the repository.  
```bash
git clone https://github.com/TezzaMichael/Network2-multiUE-gNB.git
```

2. Build the necessary docker images:

```bash
cd build
./build.sh
```

Or alternatively download them from DockerHub

```bash
cd ../open5gs
./dockerhub_pull.sh
```

3. Run init.sh with the number of UE
```bash
 sudo init.sh nUE
```
for example: nUE = 6
```bash
 sudo init.sh 6
```

