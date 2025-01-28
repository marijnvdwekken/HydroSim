# ScadaLTS

**ScadaLTS** will serve as the **HMI (Human-Machine Interface)** for this simulation. It provides capabilities to manipulate the simulation and monitor the status of the water network in real time.
## Automatic Configuration

The ScadaLTS environment is automatically configured during deployment using a `.zip` configuration file located at:  
`/scadalts/config.zip`

The configuration is uploaded and applied using a mechanism described in the following GitHub discussion:  
[SCADA-LTS Discussion #2463](https://github.com/SCADA-LTS/Scada-LTS/discussions/2463).

This process is integrated into the `docker-compose.yaml` file, ensuring seamless setup without manual intervention.

```bash
curl -d "username=admin&password=admin&submit=Login" -c cookies http://localhost:8080/ScadaBR/login.htm
curl -b cookies -v -F importFile=/config.zip http://localhost:8080/ScadaBR/import_project.htm
curl 'http://localhost:8080/ScadaBR/dwr/call/plaincall/EmportDwr.loadProject.dwr' -X POST -b cookies --data-raw $'callCount=1\npage=/ScadaBR/import_project.htm\nhttpSessionId=\nscriptSessionId=D15BC242A0E69D4251D5585A07806324697\nc0-scriptName=EmportDwr\nc0-methodName=loadProject\nc0-id=0\nbatchId=5\n
```


# HMI Water Network Overview

## General Overview of the Water Network

The main view of our HMI consists of the SCADA general overview of the water network. In this view, there are also nodes that link to the rest of the network and provide a general overview of how the network looks.

**Figure 1: General Overview**  
![image](https://github.com/user-attachments/assets/61053b09-f640-4c22-86e2-0b8ed44e998b)

Our water network was developed from the beginning in an **EPANET file**. In this file, the initial water network was designed, and all values in this document originate from it. It is important to note that both **Figure 1** and **Figure 2** are based on this EPANET file.

**Figure 2: Overview of the EPANET Water Network**  
![image](https://github.com/user-attachments/assets/bd601fd8-99e8-4c13-a78c-44a215460bb9)

## Network Structure

The network is divided into two sections:
1. **Water Reservoir**  
   Water is sent from the water reservoir—which we have decided, in this case, to be an infinite water supply—to the different networks.  
   **Figure 3: Overview of the Water Reservoir**  
   ![image](https://github.com/user-attachments/assets/06d042c5-ca6b-4ff4-882c-ce6c78fbb232)

2. **Water Tanks**  
   Each water network corresponds to different water tanks.  
   **Figure 4: Overview of the Water Tanks**  
   ![image](https://github.com/user-attachments/assets/10eba404-bffc-4ac8-9b56-46423e11b07f)

---
## Networks Version 2

The network HMI designs were created based on the EPANET file we developed. This file contains a total of **four networks**. This version is referred to as **Version 2**, as it is a redesign compared to the HMIs from **Phase 3**. 

In the new HMIs, **PMManager** was used as SCADA software, and more suitable designs were created based on it. 

> **Note:** All data points are set to 0 in all other network HMIs besides **Network 1** because, at the time of taking the screenshots, the EPANET file was not being read out anymore due to technical issues.

### Network 1 Version 2
**Figure 5: Network 1 Version 2**  
![image](https://github.com/user-attachments/assets/b2435a00-e23f-4a24-b595-bfac2fb8b230)

### Network 2 Version 2
**Figure 6: Network 2 Version 2**  
![image](https://github.com/user-attachments/assets/ebad50e1-c084-4b9f-9516-d302572c1ca8)

### Network 3 Version 2
**Figure 7: Network 3 Version 2**  
![image](https://github.com/user-attachments/assets/99c7f29f-e557-4923-aee0-bfc701bc45d7)

### Network 4 Version 2
**Figure 8: Network 4 Version 2**  
![image](https://github.com/user-attachments/assets/46053c1a-5c66-4fc6-8ab8-2da6d46f8a40)


---





---

