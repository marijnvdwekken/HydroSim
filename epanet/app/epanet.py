#!/usr/bin/env python3
import sys
import time
import os, sys, json
import struct
import paho.mqtt.client as mqtt
from epyt import epanet
from pymodbus.client import ModbusTcpClient
from dotenv import load_dotenv

load_dotenv()

BROKER = os.getenv("MQTT_BROKER_URL","")
TOPIC = os.getenv("MQTT_TOPIC", "")

CA = os.getenv("MQTT_CA_CERT","")
KEY = os.getenv("MQTT_CLIENT_KEY","")
CERT = os.getenv("MQTT_CLIENT_CERT","")
TLS = os.getenv("MQTT_TLS_ENABLED","true") == "true"

# --- CONFIGURATIE ---
PUMP_MAPPING = {
    "z0": {"pump0": 0, "pump1": 1, "pump2": 2, "pump3": 3},
    "z1": {"pump1": 0}, "z2": {"pump1": 0}, "z3": {"pump1": 0}, "z4": {"pump1": 0}
}

VALVE_MAPPING = {
    "z0": {
        "valve": 8, "valv01": 9, "valve00": 10, "valve10": 11, 
        "valve11": 12, "valve20": 13, "valve21": 14, "valve30": 15, "valve31": 16
    },
    "z1": {"valve0": 2, "valve1": 4},
    "z2": {"valve0": 2, "valve1": 4},
    "z3": {"valve0": 2, "valve1": 4},
    "z4": {"valve0": 2, "valve1": 4}
}

ZONE_METERS = {
    "z0": "z0-valve",
    "z1": "16",
    "z2": "21",
    "z3": "18",
    "z4": "22"
}
METER_TO_ZONE = {v: k for k, v in ZONE_METERS.items()}
# --------------------

plc_states = {}

def parse_arguments() -> str:
    if len(sys.argv) != 2 or not sys.argv[1].endswith(".inp"):
        sys.exit(1)
    return sys.argv[1]

def setup_epanet(inp_file: str) -> epanet:
    try:
        en: epanet = epanet(inp_file)
        en.setTimeSimulationDuration(24 * 3600)
        en.setTimeHydraulicStep(60)
        return en
    except Exception: sys.exit(1)

def get_zones(en: epanet) -> set[str]:
    try:
        zones: set[str] = set()
        for name_id in en.getNodeNameID() + en.getLinkNameID():
            if "-" in name_id:
                zone, _ = name_id.split("-", 1)
                zones.add(zone)
        for z in ZONE_METERS.keys():
            zones.add(z)
        return zones
    except Exception: sys.exit(1)

def setup_clients(zones: set) -> dict[str, ModbusTcpClient]:
    try:
        clients: dict[str, ModbusTcpClient] = {
            zone: ModbusTcpClient(host=f'plc-zone{zone.split('z')[1]}', port=502)
            for zone in zones
        }
        for _, client in clients.items():
            try:
                if not client.connect(): time.sleep(1)
            except: pass
        return clients
    except Exception: sys.exit(1)

def get_coil_index(zone, element, type_map):
    if zone in type_map and element in type_map[zone]:
        return type_map[zone][element]
    digits = ''.join(filter(str.isdigit, element))
    return int(digits) if digits else 0

def get_controls(clients: dict[str, ModbusTcpClient], en: epanet) -> dict:
    global plc_states
    try:
        controls: dict = {}
        for name_id in en.getLinkNameID():
            # We besturen alleen items met een zone-prefix
            if "-" not in name_id: continue
            
            zone, element = name_id.split("-", 1)
            link_index = en.getLinkIndex(name_id)
            
            ltype = en.getLinkType(link_index)
            if ltype == "PUMP" or ltype in ["VALVE", "TCV", "PRV", "PSV"]:
                controls.setdefault(zone, {})
                controls[zone][element] = {"status": None, "index": link_index, "type": ltype}

        for zone, client in clients.items():
            if zone in controls and len(controls[zone]) > 0:
                try:
                    # Lees genoeg coils (32)
                    rr = client.read_coils(address=0, count=32) 
                    if not rr.isError():
                        plc_states[zone] = rr.bits[:32]
                        for element, data in controls[zone].items():
                            check_type = "PUMP" if data["type"] == "PUMP" else "VALVE"
                            map_dict = PUMP_MAPPING if check_type == "PUMP" else VALVE_MAPPING
                            idx = get_coil_index(zone, element, map_dict)
                            if idx < len(rr.bits):
                                is_running = rr.bits[idx]
                                controls[zone][element]["status"] = 1.0 if is_running else 0.0
                except: pass
        return controls
    except Exception: sys.exit(1)

def set_controls(en: epanet, controls: dict) -> None:
    try:
        for zone, elements in controls.items():
            for element, control in elements.items():
                if "status" in control and control["status"] is not None:
                    idx = control["index"]
                    val = control["status"]
                    ltype = control.get("type", "LINK")
                    
                    new_status = 1 if val > 0.5 else 0
                    current_status = en.getLinkStatus(idx)
                    
                    if new_status != current_status:
                        en.setLinkStatus(idx, new_status)
                        # ALLEEN voor pompen de speed aanpassen.
                        # Voor kleppen is setting 0.0 = OPEN (weerstand 0), dus niet doen!
                        if ltype == "PUMP":
                            en.setLinkSettings(idx, 1.0 if new_status==1 else 0.0)
    except Exception as e:
        print(f"ERROR in set_controls: {e}")
        sys.exit(1)

def read_data(en: epanet) -> dict:
    try:
        data: dict = {}
        all_ids = en.getNodeNameID() + en.getLinkNameID()
        
        for name_id in all_ids:
            zone = None
            element = None
            
            if name_id in METER_TO_ZONE:
                zone = METER_TO_ZONE[name_id]
                element = name_id 
            elif "-" in name_id:
                zone, element = name_id.split("-", 1)
            
            if not zone: continue

            data.setdefault(zone, {}).setdefault(element, {})
            e: dict = data[zone][element]

            # --- Check Nodes ---
            if name_id in en.getNodeNameID():
                idx = en.getNodeIndex(name_id)
                if en.getNodeType(idx) == "TANK":
                    e["type"] = "TANK"
                    e["level"] = en.getNodePressure(idx)
                else:
                    e["type"] = "NODE"

            if name_id in en.getLinkNameID():
                idx = en.getLinkIndex(name_id)
                ltype = en.getLinkType(idx)
                e["status"] = en.getLinkStatus(idx)
                e["flow"] = en.getLinkFlows(idx)
                
                if name_id == ZONE_METERS.get(zone):
                    e["is_meter"] = True
                
                if ltype == "PUMP": e["type"] = "PUMP"
                elif ltype in ["VALVE", "TCV", "PRV", "PSV", "PBV", "FCV", "GPV"]: e["type"] = "VALVE"
                else: e["type"] = "LINK"

        return data
    except: sys.exit(1)

def float_to_registers(value):
    return list(struct.unpack('>HH', struct.pack('>f', value)))

def write_data(clients: dict[str, ModbusTcpClient], data: dict) -> None:
    global plc_states
    try:
        print(f"{'ZONE':<6} | {'ELEMENT':<12} | {'TYPE':<6} | {'STATUS/VALUE':<16} | {'PLC/INFO'}")
        print("-" * 75)

        sorted_zones = sorted(data.keys())

        for zone in sorted_zones:
            elements = data[zone]
            if zone not in clients: continue
            
            client: ModbusTcpClient = clients[zone]
            sensor_mask = 0 
            
            for element, props in elements.items():
                
                if props.get("is_meter"):
                    flow_val = abs(float(props.get("flow", 0)))
                    print(f"{zone:<6} | {element:<12} | {'METER':<6} | {flow_val:<16.2f} | Reg 700")
                    try:
                        client.write_registers(address=700, values=float_to_registers(flow_val))
                    except: pass

                # --- TANKS ---
                elif props.get("type") == "TANK":
                    try:
                        tank_num = int(''.join(filter(str.isdigit, element)))
                        level = float(props.get("level", 0))
                        
                        is_low, is_high = level < 5.0, level > 15.0
                        base_bit = tank_num * 2
                        if is_low: sensor_mask |= (1 << base_bit)
                        if is_high: sensor_mask |= (1 << (base_bit + 1))
                        try:
                            client.write_registers(address=10+(tank_num*2), values=float_to_registers(level))
                        except: pass
                    except: pass 

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
                    print(f"{zone:<6} | {element:<12} | {props['type']:<6} | {epa_text:<16} | {plc_display}")

            try: client.write_registers(address=0, values=[sensor_mask])
            except: pass
            
    except: pass

def main():
    inp_file = parse_arguments()
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
    except: pass

    try:
        en = setup_epanet(inp_file)
        
        zones = get_zones(en)
        clients = setup_clients(zones)
        en.openHydraulicAnalysis()
        en.initializeHydraulicAnalysis()
        
        print("\n--- RUNNING SIMULATION (STABLE VERSION - NO ROUNDING) ---\n")
        while True:
            en.setTimeSimulationDuration(en.getTimeSimulationDuration() + en.getTimeHydraulicStep())
            
            ctls = get_controls(clients, en)
            set_controls(en, ctls)
            en.runHydraulicAnalysis()
            
            data = read_data(en)
            write_data(clients, data)
            mqtt_client.publish(TOPIC, str(data))
            
            en.nextHydraulicAnalysisStep()
            time.sleep(2)
            
    except KeyboardInterrupt: sys.exit(0)
    except: sys.exit(1)
    finally:
        if "en" in locals(): en.closeHydraulicAnalysis(); en.unload()

if __name__ == "__main__": main()