#!/usr/bin/env python3
import json
import math
import os
import re
import struct
import time
from pathlib import Path

import paho.mqtt.client as mqtt
from dotenv import load_dotenv
from epyt import epanet
from pymodbus.client import ModbusTcpClient

load_dotenv()
BROKER = os.getenv("MQTT_BROKER_URL", "")
TOPIC = os.getenv("MQTT_TOPIC", "")

CA = os.getenv("MQTT_CA_CERT", "certs/ca/ca.crt")
KEY = os.getenv("MQTT_CLIENT_KEY", "certs/server/server.key")
CERT = os.getenv("MQTT_CLIENT_CERT", "certs/server/server.crt")
TLS = os.getenv("MQTT_TLS_ENABLED", "true") == "true"

CA = os.getenv("MQTT_CA_CERT", "")
KEY = os.getenv("MQTT_CLIENT_KEY", "")
CERT = os.getenv("MQTT_CLIENT_CERT", "")
TLS = os.getenv("MQTT_TLS_ENABLED", "true") == "true"
DEBUG = os.getenv("DEBUG",True)

ep = epanet((Path(__file__).parent.resolve() / "scenario.inp").as_posix())

# --- CONFIGURATIE ---
zone0 = "plc-zone0" if not DEBUG else "127.0.0.1:5022"
zone1 = "plc-zone1" if not DEBUG else "127.0.0.1:5023"
zone2 = "plc-zone2" if not DEBUG else "127.0.0.1:5024"
zone3 = "plc-zone3" if not DEBUG else "127.0.0.1:5025"
zone4 = "plc-zone4" if not DEBUG else "127.0.0.1:5026"


PUMP_MAPPING = {
    zone0: {"pump0": 0, "pump1": 1, "pump2": 2, "pump3": 3},
    zone1: {"pump1": 0},
    zone2: {"pump1": 0},
    zone3: {"pump1": 0},
    zone4: {"pump1": 0},
}

VALVE_MAPPING = {
    zone0: {
        "valve": 8,
        "valv01": 9,
        "valve00": 10,
        "valve10": 11,
        "valve11": 12,
        "valve20": 13,
        "valve21": 14,
        "valve30": 15,
        "valve31": 16,
    },
    zone1: {"valve0": 2, "valve1": 4},
    zone2: {"valve0": 2, "valve1": 4},
    zone3: {"valve0": 2, "valve1": 4},
    zone4: {"valve0": 2, "valve1": 4},
}

ZONE_METERS = {"z0": "z0-valve", "z1": "16", "z2": "21", "z3": "18", "z4": "22"}
METER_TO_ZONE = {v: k for k, v in ZONE_METERS.items()}
# --------------------


def setup_clients(zones: dict[str, dict]) -> dict[str, ModbusTcpClient]:
    try:
        if not DEBUG:
            clients: dict[str, ModbusTcpClient] = {
                zone: ModbusTcpClient(host=f"plc-{zone.replace('z', 'zone')}", port=502)
                for zone in zones
            }
        else:
            clients: dict[str, ModbusTcpClient] = {
                zone: ModbusTcpClient(host="127.0.0.1", port=5022 + i)
                for i, zone in enumerate(zones)
            }
        for client in clients.values():
            while not client.connect():
                time.sleep(1)
        return clients
    except Exception as e:
        print(f"ERROR in setup_clients: {e}")
        raise e


def get_coil_index(zone, element, type_map):
    if zone in type_map and element in type_map[zone]:
        return type_map[zone][element]
    digits = "".join(filter(str.isdigit, element))
    return int(digits) if digits else 0


def read_plc(client: ModbusTcpClient) -> dict[str, dict]:
    try:
        controls = {}
        if not DEBUG:
            zone = client.comm_params.host 
        else:
            zone = client.comm_params.host + "" + str(client.comm_params.port)
        for name_id in ep.getLinkNameID():
            if not re.search("^z\\d", name_id):
                continue
            link_index = ep.getLinkIndex(name_id)
            ltype = ep.getLinkType(link_index)
            controls[name_id] = {"type": ltype, "index": link_index}

        rr = client.read_coils(address=0, count=32)
        if not rr.isError():
            for element, data in controls.items():
                check_type = "PUMP" if data["type"] == "PUMP" else "VALVE"
                map_dict = PUMP_MAPPING if check_type == "PUMP" else VALVE_MAPPING
                idx = get_coil_index(zone, element, map_dict)
                if idx < len(rr.bits):
                    is_running = rr.bits[idx]
                    controls[element]["status"] = 1.0 if is_running else 0.0

        return controls
    except Exception as e:
        print(f"Error in read_plc: {e}")
        raise e


def set_values( values: dict) -> None:
    try:
        for element, control in values.items():
            if "status" in control and control["status"] is not None:
                idx = control["index"]
                val = control["status"]
                ltype = control.get("type", "LINK")
                
                new_status = 1 if val > 0.5 else 0
                current_status = ep.getLinkStatus(idx)
                
                if new_status != current_status:
                    ep.setLinkStatus(idx, new_status)
                    if ltype == "PUMP":
                        ep.setLinkSettings(idx, 1.0 if new_status==1 else 0.0)
    except Exception as e:
        print(f"ERROR in set_values: {e}")


def float_to_registers(value):
    return list(struct.unpack(">HH", struct.pack(">f", value)))


def write_plc(client: ModbusTcpClient, data: dict[str, dict[str, dict]]) -> None:
    try:
        # print(
        #     f"{'ZONE':<6} | {'ELEMENT':<12} | {'TYPE':<6} | {'STATUS/VALUE':<16} | {'PLC/INFO'}"
        # )
        # print("-" * 75)

        if not DEBUG:
            zone = client.comm_params.host 
        else:
            zone = client.comm_params.host + ":" + str(client.comm_params.port)

        sensor_mask = 0

        for element, props in data.items():
            if props.get("is_meter"):
                flow_val = abs(float(props.get("flow", 0)))
                
                # print(
                #     f"{zone:<6} | {element:<12} | {'METER':<6} | {flow_val:<16.2f} | Reg 700"
                # )
                try:
                    client.write_registers(
                        address=700, values=float_to_registers(flow_val)
                    )
                except Exception:
                    pass

            elif props.get("type") == "TANK":
                try:
                    tank_num = int("".join(filter(str.isdigit, element)))
                    level = props.get("level")
                    is_low, is_high = level < 5.0, level > 15.0
                    base_bit = tank_num * 2
                    if is_low:
                        sensor_mask |= 1 << base_bit
                    if is_high:
                        sensor_mask |= 1 << (base_bit + 1)
                    try:
                        client.write_registers(
                            address=10 + (tank_num * 2),
                            values=float_to_registers(level),
                        )
                    except Exception:
                        pass
                except Exception:
                    pass

            elif props.get("type") in ["PUMP", "VALVE"]:
                status_val = float(props.get("status", 0))

                if props["type"] == "VALVE":
                    epa_text = "OPEN" if status_val > 0 else "DICHT"
                else:
                    epa_text = "AAN" if status_val > 0 else "UIT"

                check_type = "PUMP" if props["type"] == "PUMP" else "VALVE"
                map_dict = PUMP_MAPPING if check_type == "PUMP" else VALVE_MAPPING
                idx = get_coil_index(zone, element, map_dict)

                plc_text = "?"
                is_on = props.get("status")
                if props["type"] == "VALVE":
                    plc_text = "OPEN" if is_on else "DICHT"
                else:
                    plc_text = "AAN" if is_on else "UIT"

                plc_display = f"{plc_text} (Coil {idx})"
                print(
                    f"{zone:<6} | {element:<12} | {props['type']:<6} | {epa_text:<16} | {plc_display}"
                )

        try:
            client.write_registers(address=0, values=[sensor_mask])
        except Exception:
            pass

    except Exception:
        pass


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
                diameter = ep.getNodeTankDiameter(node)
                volume = ep.getNodeTankVolume(node)

                # Bereken oppervlakte van de bodem: pi * r^2
                # (r = diameter / 2)
                area = math.pi * ((diameter / 2) ** 2)

                # Bereken level: Volume / Oppervlakte
                if area > 0:
                    calculated_level = volume / area
                else:
                    calculated_level = 0.0

                node_data["level"] = round(float(calculated_level), 3)
            case "RESERVOIR":
                pass
            case _:
                pass
        # print(name, json.dumps(node_data))
        zone_data[name] = node_data
    return zone_data


def get_linkdata(links):
    zone_data = {}
    for link in links:
        link_data = dict()
        # variables of every node
        name = ep.getLinkNameID(link)
        link_data["type"] = ep.getLinkType(link)
        link_data["quality"] = float(ep.getLinkActualQuality(link))
        link_data["headloss"] = round(float(ep.getLinkHeadloss(link)), 3)
        link_data["flow"] = round(float(ep.getLinkFlows(link)), 3)
        # the same as speed = 0 or if the pipe is open of closed
        link_data["status"] = int(ep.getLinkStatus(link))

        match ep.getLinkType(link):
            case "PIPE":
                link_data["velocity"] = round(float(ep.getLinkVelocity(link)), 3)
                link_data["length"] = int(ep.getLinkLength(link))
                pass
            case "PUMP":
                # determent to be always 1
                link_data["power"] = ep.getLinkPumpPower(link)
                # used to change the rotation speed. 0 = off
                link_data["speed"] = float(ep.getLinkSettings(link))
                link_data["energy"] = round(float(ep.getLinkEnergy(link)), 3)
                link_data["efficeiency"] = round(ep.getLinkPumpEfficiency(link), 3)
                link_data["state"] = ep.getLinkPumpState(link)
            # there are more valve types but only the TCV is used
            case "VALVE" | "TCV":
                link_data["velocity"] = round(float(ep.getLinkVelocity(link)), 3)
                pass
            case _:
                pass
        # print(name, json.dumps(link_data))
        zone_data[name] = link_data
    return zone_data


def main():
    mqtt_client = mqtt.Client(client_id=f"mqtt-{os.urandom(4).hex()}")
    try:
        if TLS and CA and KEY and CERT:
            mqtt_client.tls_set(ca_certs=CA, certfile=CERT, keyfile=KEY)
            mqtt_client.tls_insecure_set(True)
            host = BROKER.split("://")[-1]
            mqtt_client.connect(host, 8883)
        else:
            mqtt_client.connect(BROKER.split("://")[-1])
        mqtt_client.loop_start()
    except Exception:
        pass

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

            for zone, client in clients.items():
                # nodes, links = get_zone_items(zone)
                new_data = read_plc(client)
                # with open("new_data.json","w") as f:
                #     json.dump(new_data,f)

            tstep = ep.runHydraulicAnalysis()

            for zone, client in clients.items():
                data = {}
                nodes, links = get_zone_items(zone)
                # there is no way as of 11-12-2025 to get the tag value of the links and nodes
                # epyt has a way to add comments with setNodeComment() and setLinkComment()
                data.update(get_linkdata(links))
                data.update(get_nodedata(nodes))

                write_plc(client, data)
                # mqtt_client.publish(TOPIC, str(data))

            ep.nextHydraulicAnalysisStep()

            time.sleep(1)
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
