#!/usr/bin/env python3
import json
import math
import os
import time
from pathlib import Path

import struct
import paho.mqtt.client as mqtt
from epyt import epanet
from pymodbus.client import ModbusTcpClient
from dotenv import load_dotenv

load_dotenv()
BROKER = os.getenv("MQTT_BROKER_URL", "")
TOPIC = os.getenv("MQTT_TOPIC", "")

CA = os.getenv("MQTT_CA_CERT", "certs/ca/ca.crt")
KEY = os.getenv("MQTT_CLIENT_KEY", "certs/server/server.key")
CERT = os.getenv("MQTT_CLIENT_CERT", "certs/server/server.crt")
TLS = os.getenv("MQTT_TLS_ENABLED", "true") == "true"

ep = epanet(Path(__file__).parent.resolve() / "scenario.inp")
CA = os.getenv("MQTT_CA_CERT", "")
KEY = os.getenv("MQTT_CLIENT_KEY", "")
CERT = os.getenv("MQTT_CLIENT_CERT", "")
TLS = os.getenv("MQTT_TLS_ENABLED", "true") == "true"

ep = epanet(Path(__file__).parent.resolve() / "scenario.inp")

# --- CONFIGURATIE ---
PUMP_MAPPING = {
    "z0": {"pump0": 0, "pump1": 1, "pump2": 2, "pump3": 3},
    "z1": {"pump1": 0},
    "z2": {"pump1": 0},
    "z3": {"pump1": 0},
    "z4": {"pump1": 0},
}

VALVE_MAPPING = {
    "z0": {
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
    "z1": {"valve0": 2, "valve1": 4},
    "z2": {"valve0": 2, "valve1": 4},
    "z3": {"valve0": 2, "valve1": 4},
    "z4": {"valve0": 2, "valve1": 4},
}

ZONE_METERS = {"z0": "z0-valve", "z1": "16", "z2": "21", "z3": "18", "z4": "22"}
METER_TO_ZONE = {v: k for k, v in ZONE_METERS.items()}
# --------------------

plc_states = {}


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


def get_coil_index(zone, element, type_map):
    if zone in type_map and element in type_map[zone]:
        return type_map[zone][element]
    digits = "".join(filter(str.isdigit, element))
    return int(digits) if digits else 0


def read_plc(client: ModbusTcpClient) -> dict:
    try:
        controls: dict = {}
        for name_id in ep.getLinkNameID():
            # We besturen alleen items met een zone-prefix
            if "-" not in name_id: continue
            
            zone, element = name_id.split("-", 1)
            link_index = ep.getLinkIndex(name_id)
            
            ltype = ep.getLinkType(link_index)
            if ltype == "PUMP" or ltype in ["VALVE", "TCV", "PRV", "PSV"]:
                controls.setdefault(zone, {})
                controls[zone][element] = {"status": None, "index": link_index, "type": ltype}

    
        if zone in controls and len(controls[zone]) > 0:
            try:
                # Lees genoeg coils (32)
                rr = client.read_coils(address=0, count=32)
                if not rr.isError():
                    plc_states[zone] = rr.bits[:32]
                    for element, data in controls[zone].items():
                        check_type = "PUMP" if data["type"] == "PUMP" else "VALVE"
                        map_dict = (
                            PUMP_MAPPING if check_type == "PUMP" else VALVE_MAPPING
                        )
                        idx = get_coil_index(zone, element, map_dict)
                        if idx < len(rr.bits):
                            is_running = rr.bits[idx]
                            controls[zone][element]["status"] = (
                                1.0 if is_running else 0.0
                            )
            except:
                pass
        return controls
    except Exception as e:
        print(f"Error in get_controls: {e}")
        raise e


def set_values(controls: dict) -> None:
    try:
        for zone, elements in controls.items():
            for element, control in elements.items():
                if "status" in control and control["status"] is not None:
                    idx = control["index"]
                    val = control["status"]
                    ltype = control.get("type", "LINK")

                    new_status = 1 if val > 0.5 else 0
                    current_status = ep.getLinkStatus(idx)

                    if new_status != current_status:
                        ep.setLinkStatus(idx, new_status)
                        # ALLEEN voor pompen de speed aanpassen.
                        # Voor kleppen is setting 0.0 = OPEN (weerstand 0), dus niet doen!
                        if ltype == "PUMP":
                            ep.setLinkSettings(idx, 1.0 if new_status == 1 else 0.0)
    except Exception as e:
        print(f"ERROR in set_controls: {e}")
        raise e


def float_to_registers(value):
    return list(struct.unpack('>HH', struct.pack('>f', value)))

def write_plc(client: ModbusTcpClient, data: dict[str, dict[str, dict]]) -> None:
    try:
        print(
            f"{'ZONE':<6} | {'ELEMENT':<12} | {'TYPE':<6} | {'STATUS/VALUE':<16} | {'PLC/INFO'}"
        )
        print("-" * 75)

        zone = client.comm_params.host

        sensor_mask = 0

        for element, props in data.items():
            if props.get("is_meter"):
                flow_val = abs(float(props.get("flow", 0)))
                print(
                    f"{zone:<6} | {element:<12} | {'METER':<6} | {flow_val:<16.2f} | Reg 700"
                )
                try:
                    client.write_registers(
                        address=700, values=float_to_registers(flow_val)
                    )
                except:
                    pass

            # --- TANKS ---
            elif props.get("type") == "TANK":
                try:
                    tank_num = int("".join(filter(str.isdigit, element)))
                    level = float(props.get("level", 0))

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
                    except:
                        pass
                except:
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
                if zone in plc_states and idx < len(plc_states[zone]):
                    is_on = plc_states[zone][idx]
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
        except:
            pass

    except:
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
    except:
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
