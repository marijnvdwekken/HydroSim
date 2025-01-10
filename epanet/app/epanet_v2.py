#!/usr/bin/env python3
import sys
import time

from epyt import epanet
from pymodbus.client import ModbusTcpClient


def parse_arguments() -> str:
    if len(sys.argv) != 2 or not sys.argv[1].endswith(".inp"):
        print("Run EPANET simulation with Modbus controls.")
        print(f">>> python {sys.argv[0]} [network.inp]")
        sys.exit(1)
    return sys.argv[1]


def get_zones(en: epanet) -> set:
    try:
        zones = set()

        for name_id in en.getNodeNameID() + en.getLinkNameID():
            if "-" not in name_id:
                continue
            zone, _ = name_id.split("-", 1)
            zones.add(zone)
        return zones
    except Exception as e:
        print(f"ERROR in get_zones: {e}")
        sys.exit(1)


def setup_clients(zones: set) -> dict[str, ModbusTcpClient]:
    try:
        # clients = {
        #     zone: ModbusTcpClient(host=f'plc-{zone}', port=502) for zone in zones
        # }
        ### CODE FOR LOCAL TESTING
        clients = {
            zone: ModbusTcpClient(host="127.0.0.1", port=502 + i) 
            for i, zone in enumerate(zones)
        }
        ### END
        for zone, client in clients.items():
            while not client.connect():
                time.sleep(1)
        return clients
    except Exception as e:
        print(f"ERROR in setup_clients: {e}")
        sys.exit(1)


def setup_epanet(inp_file: str) -> epanet:
    try:
        en = epanet(inp_file)
        en.setTimeSimulationDuration(10)  # initial setup; duration will be set to infinite in main function.
        en.setTimeHydraulicStep(1)
        return en
    except Exception as e:
        print(f"ERROR in setup_epanet: {e}")
        sys.exit(1)


def get_controls(clients: dict[str, ModbusTcpClient]) -> dict:
    try:
        ### TODO
        pass
    except Exception as e:
        print(f"ERROR in get_controls: {e}")
        sys.exit(1)


def set_controls(en: epanet, controls: dict) -> None:
    try:
        ### TODO
        pass
    except Exception as e:
        print(f"ERROR in set_controls: {e}")
        sys.exit(1)


def read_data(en: epanet) -> dict:
    try:
        data = {}

        for name_id in en.getNodeNameID() + en.getLinkNameID():
            if "-" not in name_id:
                continue
            zone, element = name_id.split("-", 1)
            data.setdefault(zone, {}).setdefault(element, {})

            e = data[zone][element]  # holds entry point for specific element.

            if name_id in en.getNodeNameID():
                node_index = en.getNodeIndex(name_id)

                e["index"] = str(node_index)
                e["hydraulic_head"] = str(en.getNodeHydraulicHead(node_index))
                e["pressure"] = str(en.getNodePressure(node_index))
                e["elevation"] = str(en.getNodeElevations(node_index))

                if en.getNodeType(node_index) == "TANK":
                    e["minimum_water_level"] = str(en.getNodeTankMinimumWaterLevel(node_index))
                    e["maximum_water_level"] = str(en.getNodeTankMaximumWaterLevel(node_index))
                    e["initial_level"] = str(en.getNodeTankInitialLevel(node_index))
                    e["maximum_water_volume"] = str(en.getNodeTankMinimumWaterVolume(node_index))

            if name_id in en.getLinkNameID():
                link_index = en.getLinkIndex(name_id)

                e["index"] = str(link_index)
                e["status"] = str(en.getLinkStatus(link_index))
                e["flow_rate"] = str(en.getLinkFlows(link_index))

                match en.getLinkType(link_index):  # read values based on link type.
                    case "PIPE":
                        pass
                    case "PUMP":
                        e["power"] = str(en.getLinkPumpPower(link_index))
                        e["speed"] = str(en.getLinkSettings(link_index))
                        e["energy_usage"] = str(en.getLinkEnergy(link_index))
                    case _:  # default case to handle all valve types.
                        e["setting"] = str(en.getLinkSettings(link_index))  # i'm not sure where this is used for...

        return data
    except Exception as e:
        print(f"ERROR in read_data: {e}")
        sys.exit(1)


def write_data(clients: dict[str, ModbusTcpClient], data: dict) -> None:
    try:
        for zone, elements in data.items():
            # if zone not in clients:
                # continue
            client = clients[zone]

            for i, (element, values) in enumerate(elements.items()):
                address = i * 2

                for k, value in values.items():
                    registers = client.convert_to_registers(float(value), client.DATATYPE.FLOAT32)
                    client.write_registers(address, registers)
                    ### TEST
                    # print(f"writing value {value} (converted to registers: {registers}) from {zone} -> {element} -> {k} to register address {address}")
    except Exception as e:
        print(f"ERROR in write_data: {e}")
        sys.exit(1)


def main():
    inp_file = parse_arguments()

    try:
        en = setup_epanet(inp_file)

        clients = setup_clients(
            get_zones(en)
        )

        en.openHydraulicAnalysis()
        en.initializeHydraulicAnalysis()

        while True:
            en.setTimeSimulationDuration(
                en.getTimeSimulationDuration() + en.getTimeHydraulicStep()
            )  # this way the duration is set to infinite.

            # controls = get_controls(clients)
            # set_controls(en, controls)

            en.runHydraulicAnalysis()

            data = read_data(en)
            # write_data(clients, data)

            ### TEST
            import json; data_json = json.dumps(data, indent=4)
            print(data_json)

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


if __name__ == "__main__":
    main()
