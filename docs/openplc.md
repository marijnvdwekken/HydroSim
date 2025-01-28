# OpenPLC in the Simulation Environment

This project integrates OpenPLC for simulating programmable logic controllers (PLCs) within the virtual environment. It leverages the repository [OpenPLC-Docker-AutoStart](https://github.com/koztkozt/OpenPLC-Docker-AutoStart) to automate the import and configuration of PLCs using pre-defined `.ST` files during the build process.

## Purpose and Functionality

The OpenPLC setup allows for the inclusion of multiple PLCs to control various zones within the simulation environment. Each PLC can be configured with a specific `.ST` (Structured Text) file, representing the logic for that zone. This provides flexibility in designing complex scenarios involving different operational zones.

## Adding a PLC

To add a new PLC to the environment, you can modify the `docker-compose.yaml` file. Use the following syntax as a template:

```yaml
plc-zone*:
  container_name: plc-zone* # Replace * with the zone name (e.g., plc-zone1, plc-zone2)
  depends_on:
    - scadalts
  build:
    context: ./openplc/.
    dockerfile: Dockerfile
    args:
      script: watertanklogica.st # Replace with the .ST file the PLC should execute
      database: database.sh # Database script; do not modify
  ports:
    - "8082:8080" # Port mapping for external access and debugging; can be disabled if not required
  expose:
    - "502" # Modbus/TCP communication port
    - "8080" # WebUI access; can be removed if not needed
  networks:
    - plc_network
```

# Ladder Logic for ScadaLTS Integration

This repository contains the ladder logic program designed to interact with ScadaLTS via holding registers. The program controls a pump's speed and interacts with EPANET for simulation purposes.

## Overview
The ladder logic program uses holding registers to communicate with ScadaLTS. The `PumpSpeed` variable is mapped to `%QW1000`, which corresponds to the pump speed in EPANET.

## Variables
Below are the key variables used in the ladder logic:

- **PumpSpeed**: Located at `%QW1000` in EPANET.
- **StartButton**: Isn't located in epanet but is an functional button within ScadaLTS.

## Logic Explanation
The ladder logic program performs the following tasks:
1. Reads the pump speed from ScadaLTS.
2. Writes the pump speed to `%QW1000` for EPANET simulation.
3. This turns the pump on and makes the water flow through

## Screenshots
Below are screenshots of the ladder logic program and variable mappings:

- **Ladder Logic Diagram**:
  ![Ladder Logic](https://github.com/user-attachments/assets/b71d7090-d1b7-488d-b714-3ad051348537)

- **Variable Mappings**:
  ![Variables](https://github.com/user-attachments/assets/63f969ae-d920-4357-b2a3-0673219d9663)

- **EPANET Integration**:
  ![EPANET](https://github.com/user-attachments/assets/6e044bd1-9854-4733-b9de-a7f583981b74)
  ![EPANET](https://github.com/user-attachments/assets/06fdcd69-9845-4811-b343-fcb45621689d)







