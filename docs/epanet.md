# EPANET Simulation with Modbus Controls

This Python script runs an EPANET simulation with Modbus controls, enabling real-time interaction between the EPANET model/network and external PLCs. The script reads control values from PLCs via Modbus, applies them to the EPANET simulation, and then writes the simulation results back to the PLCs.

To achieve this, we have minimized the use of external modules, keeping the script as close as possible to default Python functionalities. The only packages/modules used are:

- Python standard library: `sys`, `time`
- Third-party libraries: `epyt`, `pymodbus`

The script consists of the following functions:

- `parse_arguments() -> str`
- `setup_epanet(inp_file: str) -> epanet`
- `get_zones(en: epanet) -> set[str]`
- `setup_clients(zones: set) -> dict[str, ModbusTcpClient]`
- `get_controls(clients: dict[str, ModbusTcpClient], en: epanet) -> dict`
- `set_controls(en: epanet, controls: dict) -> None`
- `read_data(en: epanet) -> dict`
- `write_data(clients: dict[str, ModbusTcpClient], data: dict) -> None`
- `main()`

Below, we'll explain each function in depth and how they work under the hood.

- `parse_arguments() -> str`

The `parse_arguments()` function is self-explanatory and has been designed for simplicity. It handles command-line arguments to ensure a valid `.inp` file is provided.

Function:

```python
def parse_arguments() -> str:
    if len(sys.argv) != 2 or not sys.argv[1].endswith(".inp"):
        print("Run EPANET simulation with Modbus controls.")
        print(f">>> python {sys.argv[0]} [network.inp]")
        sys.exit(1)
    return sys.argv[1]
```

Input:

- Path to the `.inp` file.

Output:

- str: String containing the path to the `.inp` file.

Behavior:

- If no valid `.inp` file is provided, the program exits and displays a message showing how to use the script.




asdasddasdsdadasdasda
asdasd
asda
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
