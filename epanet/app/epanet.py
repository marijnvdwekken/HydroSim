#!/usr/bin/env python3
import sys
import time
import os, sys, json
import paho.mqtt.client as mqtt
from epyt import epanet
from pymodbus.client import ModbusTcpClient


BROKER = os.getenv("MQTT_BROKER_URL","mqtt://192.168.2.55")
TOPIC = os.getenv("MQTT_TOPIC", "test/topic")

CA = os.getenv("MQTT_CA_CERT","certs/ca/ca.crt")
KEY = os.getenv("MQTT_CLIENT_KEY","certs/server/server.key")
CERT = os.getenv("MQTT_CLIENT_CERT","certs/server/server.crt")
TLS = os.getenv("MQTT_TLS_ENABLED","true") == "true"


def parse_arguments() -> str:
    if len(sys.argv) != 2 or not sys.argv[1].endswith(".inp"):
        print("Run EPANET simulation with Modbus controls.")
        print(f">>> python {sys.argv[0]} [network.inp]")
        sys.exit(1)
    return sys.argv[1]


def setup_epanet(inp_file: str) -> epanet:
    try:
        en: epanet = epanet(inp_file)
        en.setTimeSimulationDuration(24 * 3600)  # bv. 1 dag in seconden
        en.setTimeHydraulicStep(60)
        
        return en
    except Exception as e:
        print(f"ERROR in setup_epanet: {e}")
        sys.exit(1)


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
                        controls[zone][element]["status"] = None
                    case _:
                        controls[zone].setdefault(element, {})
                        controls[zone][element]["setting"] = None

        for zone, client in clients.items():
            pump_count = sum(1 for element in controls[zone] if "status" in controls[zone][element])

            if pump_count > 0: 
                pump_registers = client.read_holding_registers(address=1000, count=pump_count * 2).registers  # this function caused a weird error on the server only, but defining the function parameters this way, the error was solved :)

            for i, element in enumerate(e for e in controls[zone] if "status" in controls[zone][e]):
                converted_value = client.convert_from_registers(
                    pump_registers[i * 2 : i * 2 + 2], client.DATATYPE.FLOAT32
                )
                controls[zone][element]["status"] = converted_value

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


def set_controls(en: epanet, controls: dict) -> None:
    try:
        # offset_speed: int = 1000
        # offset_setting: int = 2000
        
        for zone, elements in controls.items():
            for element, control in elements.items():
                link_index: int = en.getLinkIndex(f"{zone}-{element}")

                # if "status" in control:
                #     en.setLinkSettings(link_index, control["status"])
                    # print(f"{zone:<15} -> {element:<15} -> speed        -> register: {offset_speed:<15}")
                    # offset_speed += 2

                if "setting" in control:
                    en.setLinkSettings(link_index, control["setting"])
                    # print(f"{zone:<15} -> {element:<15} -> setting      -> register: {offset_setting:<15}")
                    # offset_setting += 2

            # print()  # blank line for separating log entries.
    except Exception as e:
        print(f"ERROR in set_controls: {e}")
        sys.exit(1)


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
                    if len(registers) == 2:
                        registers = [registers[1], registers[0]]

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
#zone2-pump1-speed
#zone3-pump1-speed
def main():
    inp_file: str = parse_arguments()
    mqtt_client = mqtt.Client(client_id=f"mqtt-publisher-{os.urandom(4).hex()}")

    if TLS and CA and KEY and CERT:
        mqtt_client.tls_set(ca_certs=CA, certfile=CERT, keyfile=KEY)
        mqtt_client.tls_insecure_set(True)
        host = BROKER.split("://")[-1]
        print(f"Connecting TLS to {host}:8883")
        mqtt_client.connect(host, 8883)
    else:
        print(f"Connecting to {BROKER} without TLS")
        mqtt_client.connect(BROKER.split("://")[-1])
    mqtt_client.loop_start()
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
            print(controls)
            set_controls(en, controls)

            en.runHydraulicAnalysis()

            data: dict = read_data(en)
            write_data(clients, data)
            mqtt_client.publish(TOPIC, str(data))

            en.nextHydraulicAnalysisStep()

            time.sleep(1)
    except KeyboardInterrupt:
        print(">--- Program interrupted by user ---")
        mqtt_client.loop_stop()
        mqtt_client.disconnect()
        sys.exit(0)  # clean exit confirmed by user action.
    except Exception as e:
        print(f"Failed to run EPANET simulation due to an unexpected error: {e}")
        sys.exit(1)
        mqtt_client.loop_stop()
        mqtt_client.disconnect()
    finally:
        if "clients" in locals():
            for client in clients.values():
                client.close()
        if "en" in locals():
            en.closeHydraulicAnalysis()
            en.unload()
        mqtt_client.loop_stop()
        mqtt_client.disconnect()


if __name__ == "__main__":
    main()
