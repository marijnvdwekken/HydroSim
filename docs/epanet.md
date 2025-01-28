# EPANET Simulation with Modbus Controls

This Python script runs an EPANET simulation with Modbus controls, allowing for real-time interaction between the EPANET model/network and external PLCs. The script reads control values from PLCs via Modbus, applies them to the EPANET simulation, and then writes the simulation results back to the PLCs.

## Table of Contents
- [Overview](#overview)
- [Function Descriptions](#function-descriptions)
  - [parse_arguments()](#parse_arguments)
  - [setup_epanet(inp_file: str)](#setup_epanetinp_file-str)
  - [get_zones(en: epanet)](#get_zonesen-epanet)
  - [setup_clients(zones: set)](#setup_clientszones-set)
  - [get_controls(clients: dict, en: epanet)](#get_controlsclients-dict-en-epanet)
  - [set_controls(en: epanet, controls: dict)](#set_controlsen-epanet-controls-dict)
  - [read_data(en: epanet)](#read_dataen-epanet)
  - [write_data(clients: dict, data: dict)](#write_dataclients-dict-data-dict)
  - [main()](#main)
- [Data Flow](#data-flow)
- [Modbus Register Mapping](#modbus-register-mapping)

---

## Overview

The script reads an EPANET network (.inp) file and then fetches calculated values from the EPANET network every second. It uses Modbus TCP communication for real-time control and monitoring of the water distribution network. The script continuously:

1. Reads control values from PLCs via Modbus.
2. Updates the EPANET simulation based on these controls.
3. Runs hydraulic analysis steps in EPANET every second to simulate a realistic scenario.
4. Writes simulation results (e.g., hydraulic head, pressures) back to the PLCs.

---

## Function Descriptions

### parse_arguments()
Handles command-line arguments to ensure a valid `.inp` file is provided.

- **Input**: Command-line arguments.
- **Output**: String containing the path to the `.inp` file.
- **Behavior**:
  - If no valid `.inp` file is provided, the program exits with an error message.

---

### setup_epanet(inp_file: str)
Initializes the EPANET simulation environment.

- **Input**: Path to the `.inp` file.
- **Output**: An `epanet` object representing the simulation.
- **Behavior**:
  - Sets up initial simulation parameters (e.g., duration, hydraulic step).
  - Exits if initialization fails.

---

### get_zones(en: epanet)
Extracts unique zones from node and link IDs in the EPANET network.

- **Input**: An `epanet` object.
- **Output**: A set of zone names.
- **Behavior**:
  - Parses node and link IDs to identify zones based on naming conventions (e.g., `zone-element`).

---

### setup_clients(zones: set)
Establishes Modbus TCP connections for each zone.

- **Input**: Set of zone names.
- **Output**: Dictionary mapping zones to `ModbusTcpClient` objects.
- **Behavior**:
  - Creates Modbus clients for each zone and attempts to connect repeatedly until successful.

---

### get_controls(clients: dict, en: epanet)
Reads control values (e.g., pump speeds, valve settings) from PLCs via Modbus.

- **Input**:
  - Dictionary of Modbus clients.
  - An `epanet` object.
- **Output**: Dictionary of control values for pumps and valves.
- **Behavior**:
  - Reads values from Modbus registers for each zone and maps them to corresponding elements in EPANET.

---

### set_controls(en: epanet, controls: dict)
Applies control values from PLCs to the EPANET simulation.

- **Input**:
  - An `epanet` object.
  - Dictionary of control values.
- **Output**: None.
- **Behavior**:
  - Updates pump speeds and valve settings in EPANET based on received controls.

---

### read_data(en: epanet)
Extracts current simulation data (e.g., pressures, flow rates) from EPANET.

- **Input**: An `epanet` object.
- **Output**: Dictionary containing simulation data for nodes and links.
- **Behavior**:
  - Reads hydraulic properties (e.g., pressure, flow rate) for each element in the network.

---

### write_data(clients: dict, data: dict)
Writes simulation results back to PLCs via Modbus.

- **Input**:
  - Dictionary of Modbus clients.
  - Dictionary of simulation data.
- **Output**: None.
- **Behavior**:
  - Converts simulation data into Modbus register format and writes it to the appropriate PLC registers.

---

### main()
Orchestrates the entire process of running the EPANET simulation with Modbus controls.

1. Initializes EPANET and Modbus connections.
2. Enters a continuous loop where it:
   - Reads control values from PLCs.
   - Updates EPANET with these controls.
   - Runs a hydraulic analysis step in EPANET.
   - Extracts simulation data and writes it back to PLCs.
3. Handles program interruption and cleanup.

---

## Data Flow

1. **PLC to EPANET**:
   - Control values (e.g., pump speeds, valve settings) are read from Modbus registers and applied to corresponding elements in EPANET.

2. **EPANET to PLC**:
   - After each hydraulic analysis step, results (e.g., pressures, flow rates) are extracted from EPANET and written back to Modbus registers for each zone.

---

## Modbus Register Mapping

| Data Type       | Register Address | Description              |
|------------------|------------------|--------------------------|
| Pump Speeds      | Starting at 1000 | Control pump operation.  |
| Valve Settings   | Starting at 2000 | Control valve operation. |
| Simulation Data  | Sequential       | Results for monitoring.  |

Each value occupies two registers (FLOAT32 format).

---

This documentation provides a detailed explanation of how the script operates and interacts with both EPANET and external PLCs via Modbus TCP communication. It ensures real-time bidirectional data flow for efficient water distribution network management.
