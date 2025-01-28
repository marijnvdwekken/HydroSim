# EPANET Simulation with Modbus Controls

This Python script runs an EPANET simulation with Modbus controls, enabling real-time interaction between the EPANET model/network and external PLCs. The script reads control values from PLCs via Modbus, applies them to the EPANET simulation, and then writes the simulation results back to the PLCs.

To achieve this, we have minimized the use of external modules, keeping the script as close as possible to default Python functionalities. The only modules we used are:

- Python standard library: `sys`, `time`
- Third-party libraries: `epyt`, `pymodbus`

The script consists of the following functions:

- `def parse_arguments() -> str:`
- `def setup_epanet(inp_file: str) -> epanet:`
- `def get_zones(en: epanet) -> set[str]:`
- `def setup_clients(zones: set) -> dict[str, ModbusTcpClient]:`
- `def get_controls(clients: dict[str, ModbusTcpClient], en: epanet) -> dict:`
- `def set_controls(en: epanet, controls: dict) -> None:`
- `def read_data(en: epanet) -> dict:`
- `def write_data(clients: dict[str, ModbusTcpClient], data: dict) -> None:`
- `def main():`

In the section below, we'll explain each function in depth and how they work under the hood.

---

- `def parse_arguments() -> str:`

The `parse_arguments` function is self-explanatory and has been designed for simplicity. It handles command-line arguments to ensure a valid `.inp` file is provided.

Function:

```python
def parse_arguments() -> str:
    if len(sys.argv) != 2 or not sys.argv[1].endswith(".inp"):
        print("Run EPANET simulation with Modbus controls.")
        print(f">>> python {sys.argv[0]} [network.inp]")
        sys.exit(1)
    return sys.argv[1]
```

If a valid EPANET network is provided it will return a string containing the path to the `.inp` file. Else if no valid `.inp` file is provided, the program exits and displays a message showing how to use the script. 

---

- `def setup_epanet(inp_file: str) -> epanet:`

The `setup_epanet` function ...

Function:

```python
def setup_epanet(inp_file: str) -> epanet:
    try:
        en: epanet = epanet(inp_file)
        en.setTimeSimulationDuration(10)  # initial setup; duration will be set to infinite in main function.
        en.setTimeHydraulicStep(1)
        return en
    except Exception as e:
        print(f"ERROR in setup_epanet: {e}")
        sys.exit(1)
```

Something here...

---

- `def get_zones(en: epanet) -> set[str]:`

The `get_zones` function ...

Function:

```python
def get_zones(en: epanet) -> set[str]:
    try:
        zones: set[str] = set()

        for name_id in en.getNodeNameID() + en.getLinkNameID():
            if "-" not in name_id:
                continue
            zone, _ = name_id.split("-", 1)
            zones.add(zone)
        return zones
    except Exception as e:
        print(f"ERROR in get_zones: {e}")
        sys.exit(1)
```

Something here...

---

- `def setup_clients(zones: set) -> dict[str, ModbusTcpClient]:`

The `setup_clients` function ...

Function:

```python
def setup_clients(zones: set) -> dict[str, ModbusTcpClient]:
    try:
        clients: dict[str, ModbusTcpClient] = {
            zone: ModbusTcpClient(host=f'plc-{zone}', port=502)
            for zone in zones
        }
        # clients: dict[str, ModbusTcpClient] = {
        #     zone: ModbusTcpClient(host="127.0.0.1", port=502 + i) 
        #     for i, zone in enumerate(zones)
        # }
        for _, client in clients.items():
            while not client.connect():
                time.sleep(1)
        return clients
    except Exception as e:
        print(f"ERROR in setup_clients: {e}")
        sys.exit(1)
```

Something here...

---

- `def get_controls(clients: dict[str, ModbusTcpClient], en: epanet) -> dict:`

The `get_controls` function ...

Function:

```python
def get_controls(clients: dict[str, ModbusTcpClient], en: epanet) -> dict:
    try:
        controls: dict = {}

        for name_id in en.getNodeNameID() + en.getLinkNameID():
            if "-" not in name_id:
                continue
            zone, element = name_id.split("-", 1)
            controls.setdefault(zone, {})

            if name_id in en.getLinkNameID():
                link_index: int = en.getLinkIndex(name_id)

                match en.getLinkType(link_index):
                    case "PIPE":
                        pass
                    case "PUMP":
                        controls[zone].setdefault(element, {})
                        controls[zone][element]["speed"] = None
                    case _:
                        controls[zone].setdefault(element, {})
                        controls[zone][element]["setting"] = None

        for zone, client in clients.items():
            pump_count = sum(1 for element in controls[zone] if "speed" in controls[zone][element])

            if pump_count > 0: 
                pump_registers = client.read_holding_registers(address=1000, count=pump_count * 2).registers  # this function caused a weird error on the server only, but defining the function parameters this way, the error was solved :)

            for i, element in enumerate(e for e in controls[zone] if "speed" in controls[zone][e]):
                converted_value = client.convert_from_registers(
                    pump_registers[i * 2 : i * 2 + 2], client.DATATYPE.FLOAT32
                )
                controls[zone][element]["speed"] = converted_value

            valve_count = sum(1 for element in controls[zone] if "setting" in controls[zone][element])

            if valve_count > 0: 
                valve_registers = client.read_holding_registers(address=2000, count=valve_count * 2).registers  # same applies here...

            for i, element in enumerate(e for e in controls[zone] if "setting" in controls[zone][e]):
                converted_value = client.convert_from_registers(
                    valve_registers[i * 2 : i * 2 + 2], client.DATATYPE.FLOAT32
                )
                controls[zone][element]["setting"] = converted_value

        return controls
    except Exception as e:
        print(f"Error in get_controls: {e}")
        sys.exit(1)
```

Something here...

---

- `def set_controls(en: epanet, controls: dict) -> None:`

The `set_controls` function ...

Function:

```python
def set_controls(en: epanet, controls: dict) -> None:
    try:
        # offset_speed = 1000
        # offset_setting = 2000
        
        for zone, elements in controls.items():
            for element, control in elements.items():
                link_index: int = en.getLinkIndex(f"{zone}-{element}")

                if "speed" in control:
                    en.setLinkSettings(link_index, control["speed"])
                    # print(f"{zone:<15} -> {element:<15} -> register: {offset_speed:<15} control: speed")
                    # offset_speed += 2

                if "setting" in control:
                    en.setLinkSettings(link_index, control["setting"])
                    # print(f"{zone:<15} -> {element:<15} -> register: {offset_setting:<15} control: setting")
                    # offset_setting += 2

            # print()
    except Exception as e:
        print(f"ERROR in set_controls: {e}")
        sys.exit(1)
```

Something here...

```
zone0           -> valve1          -> register: 2000            control: setting
zone0           -> valve2          -> register: 2002            control: setting
zone0           -> valve3          -> register: 2004            control: setting
zone0           -> valve4          -> register: 2006            control: setting

zone3           -> pump1           -> register: 1000            control: speed
zone3           -> pump2           -> register: 1002            control: speed
zone3           -> pump3           -> register: 1004            control: speed

zone1           -> pump1           -> register: 1006            control: speed
zone1           -> pump2           -> register: 1008            control: speed
zone1           -> pump3           -> register: 1010            control: speed

zone4           -> pump2           -> register: 1012            control: speed
zone4           -> pump3           -> register: 1014            control: speed
zone4           -> pump1           -> register: 1016            control: speed

zone2           -> pump2           -> register: 1018            control: speed
zone2           -> pump3           -> register: 1020            control: speed
zone2           -> pump1           -> register: 1022            control: speed
```

---

- `def read_data(en: epanet) -> dict:`

The `read_data` function ...

Function:

```python
def read_data(en: epanet) -> dict:
    try:
        data: dict = {}

        for name_id in en.getNodeNameID() + en.getLinkNameID():
            if "-" not in name_id:
                continue
            zone, element = name_id.split("-", 1)
            data.setdefault(zone, {}).setdefault(element, {})

            e: dict = data[zone][element]

            if name_id in en.getNodeNameID():
                node_index: int = en.getNodeIndex(name_id)

                e["index"] = str(node_index)
                e["hydraulic_head"] = str(en.getNodeHydraulicHead(node_index))
                e["pressure"] = str(en.getNodePressure(node_index))
                e["elevation"] = str(en.getNodeElevations(node_index))

                if en.getNodeType(node_index) == "TANK":
                    e["minimum_water_level"] = str(en.getNodeTankMinimumWaterLevel(node_index))
                    e["maximum_water_level"] = str(en.getNodeTankMaximumWaterLevel(node_index))
                    e["initial_water_level"] = str(en.getNodeTankInitialLevel(node_index))
                    e["minimum_water_volume"] = str(en.getNodeTankMinimumWaterVolume(node_index))
                    e["maximum_water_volume"] = str(en.getNodeTankMaximumWaterVolume(node_index))
                    e["initial_water_volume"] = str(en.getNodeTankInitialWaterVolume(node_index))

            if name_id in en.getLinkNameID():
                link_index: int = en.getLinkIndex(name_id)

                e["index"] = str(link_index)
                e["status"] = str(en.getLinkStatus(link_index))
                e["flow_rate"] = str(en.getLinkFlows(link_index))

                match en.getLinkType(link_index):
                    case "PIPE":
                        pass
                    case "PUMP":
                        e["power"] = str(en.getLinkPumpPower(link_index))
                        e["speed"] = str(en.getLinkSettings(link_index))
                        e["energy_usage"] = str(en.getLinkEnergy(link_index))
                    case _:  # default case to handle all valve types.
                        e["setting"] = str(en.getLinkSettings(link_index))

        return data
    except Exception as e:
        print(f"ERROR in read_data: {e}")
        sys.exit(1)
```

Something here...

---

- `def write_data(clients: dict[str, ModbusTcpClient], data: dict) -> None:`

The `write_data` function ...

Function:

```python
def write_data(clients: dict[str, ModbusTcpClient], data: dict) -> None:
    try:
        for zone, elements in data.items():
            client: ModbusTcpClient = clients[zone]
            offset: int = 0

            for element, values in elements.items():
                for i, (k, value) in enumerate(values.items()):
                    address: int = offset + i * 2
                    registers: list[int] = client.convert_to_registers(
                        float(value), client.DATATYPE.FLOAT32
                    )

                    client.write_registers(address, registers)

                    # print(
                    #     f"{zone:<15} -> {element:<15} -> {k:<30}: {value:<30}, "
                    #     f"registers: {str(registers):<20}, address: {address}"
                    # )

                offset += len(values) * 2

                # print()  # blank lines for separating log entries.
            # print()
            # print()
    except Exception as e:
        print(f"ERROR in write_data: {e}")
        sys.exit(1)
```

Something here...

Snippet...

```
[---TRUNCATED---]
zone3           -> junction1       -> index                         : 6                             , registers: [16576, 0]          , address: 0
zone3           -> junction1       -> hydraulic_head                : 514.2538452148438             , registers: [17408, 36927]      , address: 2
zone3           -> junction1       -> pressure                      : 514.2538452148438             , registers: [17408, 36927]      , address: 4
zone3           -> junction1       -> elevation                     : 0.0                           , registers: [0, 0]              , address: 6

zone3           -> junction6       -> index                         : 34                            , registers: [16904, 0]          , address: 8
zone3           -> junction6       -> hydraulic_head                : 514.2538452148438             , registers: [17408, 36927]      , address: 10
zone3           -> junction6       -> pressure                      : 514.2538452148438             , registers: [17408, 36927]      , address: 12
zone3           -> junction6       -> elevation                     : 0.0                           , registers: [0, 0]              , address: 14

zone3           -> junction2       -> index                         : 35                            , registers: [16908, 0]          , address: 16
zone3           -> junction2       -> hydraulic_head                : 514.2538452148438             , registers: [17408, 36927]      , address: 18
zone3           -> junction2       -> pressure                      : 514.2538452148438             , registers: [17408, 36927]      , address: 20
zone3           -> junction2       -> elevation                     : 0.0                           , registers: [0, 0]              , address: 22

zone3           -> junction5       -> index                         : 36                            , registers: [16912, 0]          , address: 24
zone3           -> junction5       -> hydraulic_head                : 514.2538452148438             , registers: [17408, 36927]      , address: 26
zone3           -> junction5       -> pressure                      : 514.2538452148438             , registers: [17408, 36927]      , address: 28
zone3           -> junction5       -> elevation                     : 0.0                           , registers: [0, 0]              , address: 30

zone3           -> junction3       -> index                         : 37                            , registers: [16916, 0]          , address: 32
zone3           -> junction3       -> hydraulic_head                : 514.2538452148438             , registers: [17408, 36927]      , address: 34
zone3           -> junction3       -> pressure                      : 514.2538452148438             , registers: [17408, 36927]      , address: 36
zone3           -> junction3       -> elevation                     : 0.0                           , registers: [0, 0]              , address: 38

zone3           -> junction4       -> index                         : 38                            , registers: [16920, 0]          , address: 40
zone3           -> junction4       -> hydraulic_head                : 514.2538452148438             , registers: [17408, 36927]      , address: 42
zone3           -> junction4       -> pressure                      : 514.2538452148438             , registers: [17408, 36927]      , address: 44
zone3           -> junction4       -> elevation                     : 0.0                           , registers: [0, 0]              , address: 46

zone3           -> node40          -> index                         : 39                            , registers: [16924, 0]          , address: 48
zone3           -> node40          -> hydraulic_head                : 514.2538452148438             , registers: [17408, 36927]      , address: 50
zone3           -> node40          -> pressure                      : 514.2538452148438             , registers: [17408, 36927]      , address: 52
zone3           -> node40          -> elevation                     : 0.0                           , registers: [0, 0]              , address: 54
[---TRUNCATED---]
```

---

- `def main():`

The `main` function ...

Function:

```python
def main():
    inp_file: str = parse_arguments()

    try:
        en: epanet = setup_epanet(inp_file)

        zones: set[str] = get_zones(en)

        clients: dict[str, ModbusTcpClient] = setup_clients(zones)

        en.openHydraulicAnalysis()
        en.initializeHydraulicAnalysis()

        while True:
            en.setTimeSimulationDuration(
                en.getTimeSimulationDuration() + en.getTimeHydraulicStep()
            )  # this way the duration is set to infinite.

            controls: dict = get_controls(clients, en)
            set_controls(en, controls)

            en.runHydraulicAnalysis()

            data: dict = read_data(en)
            write_data(clients, data)

            en.nextHydraulicAnalysisStep()

            time.sleep(1)
    except KeyboardInterrupt:
        print(">--- Program interrupted by user ---")
        sys.exit(0)  # clean exit confirmed by user action.
    except Exception as e:
        print(f"Failed to run EPANET simulation due to an unexpected error: {e}")
        sys.exit(1)
    finally:
        if "clients" in locals():
            for client in clients.values():
                client.close()
        if "en" in locals():
            en.closeHydraulicAnalysis()
            en.unload()
```

Something here...
