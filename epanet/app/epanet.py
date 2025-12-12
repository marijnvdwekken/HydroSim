#!/usr/bin/env python3
import json
import math
import os
import time
from pathlib import Path

# import paho.mqtt.client as mqtt
from epyt import epanet
from pymodbus.client import ModbusTcpClient

BROKER = os.getenv("MQTT_BROKER_URL", "mqtt://192.168.2.55")
TOPIC = os.getenv("MQTT_TOPIC", "test/topic")

CA = os.getenv("MQTT_CA_CERT", "certs/ca/ca.crt")
KEY = os.getenv("MQTT_CLIENT_KEY", "certs/server/server.key")
CERT = os.getenv("MQTT_CLIENT_CERT", "certs/server/server.crt")
TLS = os.getenv("MQTT_TLS_ENABLED", "true") == "true"

ep = epanet(Path(__file__).parent.resolve() / "scenario.inp")


def setup_epanet(inp_file: str) -> epanet:
    try:
        ep.setTimeSimulationDuration(24 * 3600)  # bv. 1 dag in seconden
        ep.setTimeHydraulicStep(5 * 60)
    except Exception as e:
        print(f"ERROR in setup_epanet: {e}")
        raise e


def setup_clients(zones: dict[str, dict]) -> dict[str, ModbusTcpClient]:
    try:
        # clients: dict[str, ModbusTcpClient] = {
        #     zone: ModbusTcpClient(host=f"plc-{zone.replace('z', 'zone')}", port=502)
        #     for zone in zones
        # }
        clients: dict[str, ModbusTcpClient] = {
            zone: ModbusTcpClient(host="127.0.0.1", port=502 + i)
            for i, zone in enumerate(zones)
        }
        for client in clients.values():
            while not client.connect():
                time.sleep(1)
        return clients
    except Exception as e:
        print(f"ERROR in setup_clients: {e}")
        raise e


def read_plc(client: ModbusTcpClient) -> dict:
    try:
        controls: dict = {}

        for name_id in ep.getNodeNameID() + ep.getLinkNameID():
            if "-" not in name_id:
                continue
            zone, element = name_id.split("-", 1)
            controls.setdefault(zone, {})

            if name_id in ep.getLinkNameID():
                link_index: int = ep.getLinkIndex(name_id)

                match ep.getLinkType(link_index):
                    case "PIPE":
                        pass
                    case "PUMP":
                        controls[zone].setdefault(element, {})
                        controls[zone][element]["speed"] = None
                    case _:
                        controls[zone].setdefault(element, {})
                        controls[zone][element]["setting"] = None

        # for zone, client in clients.items():
        pump_count = sum(
            1 for element in controls[zone] if "speed" in controls[zone][element]
        )

        if pump_count > 0:
            pump_registers = client.read_holding_registers(
                address=1000, count=pump_count * 2
            ).registers  # this function caused a weird error on the server only, but defining the function parameters this way, the error was solved :)

        for i, element in enumerate(
            e for e in controls[zone] if "speed" in controls[zone][e]
        ):
            converted_value = client.convert_from_registers(
                pump_registers[i * 2 : i * 2 + 2], client.DATATYPE.FLOAT32
            )
            controls[zone][element]["speed"] = converted_value

        valve_count = sum(
            1 for element in controls[zone] if "setting" in controls[zone][element]
        )

        if valve_count > 0:
            valve_registers = client.read_holding_registers(
                address=2000, count=valve_count * 2
            ).registers  # same applies here...

        for i, element in enumerate(
            e for e in controls[zone] if "setting" in controls[zone][e]
        ):
            converted_value = client.convert_from_registers(
                valve_registers[i * 2 : i * 2 + 2], client.DATATYPE.FLOAT32
            )
            controls[zone][element]["setting"] = converted_value

        return controls
    except Exception as e:
        print(f"Error in get_controls: {e}")
        raise e


def set_values(controls: dict) -> None:
    try:
        # offset_speed: int = 1000
        # offset_setting: int = 2000

        for zone, elements in controls.items():
            for element, control in elements.items():
                link_index: int = ep.getLinkIndex(f"{zone}-{element}")

                # if "speed" in control:
                #     ep.setLinkSettings(link_index, control["speed"])
                # print(f"{zone:<15} -> {element:<15} -> speed        -> register: {offset_speed:<15}")
                # offset_speed += 2

                if "setting" in control:
                    ep.setLinkSettings(link_index, control["setting"])
                    # print(f"{zone:<15} -> {element:<15} -> setting      -> register: {offset_setting:<15}")
                    # offset_setting += 2

            # print()  # blank line for separating log entries.
    except Exception as e:
        print(f"ERROR in set_controls: {e}")
        raise e


def write_plc(client: ModbusTcpClient, data: dict[str, dict[str, dict]]) -> None:
    try:
        offset: int = 0
        for element, values in data.items():
            for i, (k, value) in enumerate(values.items()):
                address: int = offset + i * 2
                if isinstance(value, str):
                    pass
                    registers: list[int] = client.convert_to_registers(
                        value, client.DATATYPE.STRING
                    )
                elif isinstance(value, float | int):
                    registers: list[int] = client.convert_to_registers(
                        value, client.DATATYPE.FLOAT32
                    )

                client.write_registers(address, registers)

                print(
                    f"{client.comm_params.host:<15} -> {element:<15} -> {k:<30}: {value:<30}, "
                    f"registers: {str(registers):<20}, address: {address}"
                )

            else:
                # TODO print id/name to plc
                print(element)
            offset += len(values) * 2
    except Exception as e:
        print(f"ERROR in write_data: {e}")
        raise e


def get_zone_items(zone_id: str) -> tuple[list, list]:
    """fucntion to get the items from a zone

    Args:
        zone_id (str): id of the zone u want the items from

    Returns:
        tuple (list, list): returns a tuple of the nodes and links in the zone
    """
    nodes = [
        id
        for id, name in zip(ep.getNodeIndex(), ep.getNodeNameID())
        if name.startswith(zone_id)
    ]
    links = [
        id
        for id, name in zip(ep.getLinkIndex(), ep.getLinkNameID())
        if name.startswith(zone_id)
    ]
    return nodes, links


def get_nodedata(nodes):
    zone_data = {}

    for node in nodes:
        node_data = dict()
        name = ep.getNodeNameID(node)
        node_data["type"] = ep.getNodeType(node)
        node_data["pressure"] = round(ep.getNodePressure(node), 3)
        node_data["quality"] = round(ep.getNodeActualQuality(node), 3)
        node_data["elevation"] = ep.getNodeElevations(node)
        match ep.getNodeType(node):
            case "JUNCTION":
                node_data["demand"] = round(ep.getNodeActualDemand(node), 3)
                node_data["head"] = round(ep.getNodeHydraulicHead(node), 3)
            case "TANK":
                # h = V / (pi * r^2)
                # V = pi * r^2 * h

                node_data["level"] = round(
                    float(
                        ep.getNodeTankVolume(node)
                        / (math.pi * ep.getNodeTankDiameter(node))
                    ),
                    3,
                )
            case "RESERVOIR":
                pass
            case _:
                pass
        print(name, json.dumps(node_data))
        zone_data[name] = node_data
    return zone_data


def get_linkdata(links):
    zone_data = {}
    for link in links:
        link_data = dict()
        # variables of every node
        name = ep.getLinkNameID(link)
        link_data["type"] = ep.getLinkType(link)
        link_data["quality"] = ep.getLinkActualQuality(link)
        link_data["headloss"] = round(ep.getLinkHeadloss(link), 3)
        link_data["flow"] = round(float(ep.getLinkFlows(link)), 3)
        # the same as speed = 0 or if the pipe is open of closed
        link_data["status"] = ep.getLinkStatus(link)

        match ep.getLinkType(link):
            case "PIPE":
                link_data["velocity"] = round(ep.getLinkVelocity(link), 3)
                link_data["length"] = ep.getLinkLength(link)
                pass
            case "PUMP":
                # determent to be always 1
                link_data["power"] = ep.getLinkPumpPower(link)
                # used to change the rotation speed. 0 = off
                link_data["speed"] = float(ep.getLinkSettings(link))
                link_data["energy"] = round(ep.getLinkEnergy(link), 3)
                link_data["efficeiency"] = round(ep.getLinkPumpEfficiency(link), 3)
                link_data["state"] = ep.getLinkPumpState(link)
            # there are more valve types but only the TCV is used
            case "VALVE" | "TCV":
                link_data["velocity"] = round(ep.getLinkVelocity(link), 3)
                pass
            case _:
                pass
        print(name, json.dumps(link_data))
        zone_data[name] = link_data
    return zone_data


def main():
    # mqtt_client = mqtt.Client(client_id=f"mqtt-publisher-{os.urandom(4).hex()}")

    # if TLS and CA and KEY and CERT:
    #     mqtt_client.tls_set(ca_certs=CA, certfile=CERT, keyfile=KEY)
    #     mqtt_client.tls_insecure_set(True)
    #     host = BROKER.split("://")[-1]
    #     print(f"Connecting TLS to {host}:8883")
    #     mqtt_client.connect(host, 8883)
    # else:
    #     print(f"Connecting to {BROKER} without TLS")
    #     mqtt_client.connect(BROKER.split("://")[-1])
    # mqtt_client.loop_start()
    try:

        zone_ids = ["z0", "z1", "z2", "z3", "z4"]

        clients: dict[str, ModbusTcpClient] = setup_clients(zone_ids)

        ep.setTimeSimulationDuration(24 * 3600)  # bv. 1 dag in seconden
        ep.setTimeHydraulicStep(5 * 60)
        ep.openHydraulicAnalysis()
        ep.initializeHydraulicAnalysis(0)
        
        while True:
            # this way the duration is set to infinite.
            ep.setTimeSimulationDuration(
                ep.getTimeSimulationDuration() + ep.getTimeHydraulicStep()
            )

            # for zone, client in clients.items():
            #     # nodes, links = get_zone_items(zone)
            #     new_data = read_plc(client)
            #     set_values(new_data)

            tstep = ep.runHydraulicAnalysis()

            for zone, client in clients.items():
                data = {}
                nodes, links = get_zone_items(zone)
                # there is no way as of 11-12-2025 to get the tag value of the links and nodes
                # epyt has a way to add comments with setNodeComment() and setLinkComment()
                print(f"Working on zone {zone}")
                data.update(get_linkdata(links))
                data.update(get_nodedata(nodes))

                write_plc(client, data)
                # mqtt_client.publish(TOPIC, str(data))

            ep.nextHydraulicAnalysisStep()


            print(f"time step = {tstep}")
            time.sleep(1)
            break
    except KeyboardInterrupt:
        print(">--- Program interrupted by user ---")
    except Exception as e:
        print(f"Failed to run EPANET simulation due to an unexpected error: {e}")
    finally:
        local_variables = locals()
        if "clients" in local_variables:
            for client in clients.values():
                client.close()

        ep.closeHydraulicAnalysis()
        ep.unload()
        # mqtt_client.loop_stop()
        # mqtt_client.disconnect()


if __name__ == "__main__":
    main()
