import decimal
import json
import math
from dataclasses import dataclass

from epyt import epanet


@dataclass
class Pump:
    id: str
    tag: str
    status: bool
    power: decimal
    speed: decimal
    flow: decimal
    headloss: decimal


@dataclass
class Junction:
    id: str
    tag: str
    demand: decimal
    pressure: decimal


@dataclass
class House(Junction):
    pass


@dataclass
class Valve:
    id: str
    status: bool
    flow: decimal


@dataclass
class Tank:
    id: str
    pressure: decimal
    minimum_water_level: decimal
    maximum_water_level: decimal
    minimum_water_volume: decimal
    maximum_water_volume: decimal


@dataclass
class Reservoir:
    id: str
    head: decimal


ep: epanet


def send_inital():
    for link in ep.getLinkIndex():
        data = ep.getNodeTankData(link)
        name = ep.getNodeTankNameID(link)
        init_level = ep.getNodeTankInitialLevel(link)
        minimum_water_level = ep.getNodeTankMinimumWaterLevel(link)
        maximum_water_level = ep.getNodeTankMaximumWaterLevel(link)
        minimum_water_volume = ep.getNodeTankMinimumWaterVolume(link)
        maximum_water_volume = ep.getNodeTankMaximumWaterVolume(link)


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
        node_data["quality"] = ep.getNodeActualQuality(node)
        node_data["elevation"] = ep.getNodeElevations(node)
        match ep.getNodeType(node):
            case "JUNCTION":
                node_data["demand"] = round(ep.getNodeActualDemand(node), 3)
                node_data["head"] = ep.getNodeHydraulicHead(node)
            case "TANK":
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
        link_data["headloss"] = ep.getLinkHeadloss(link)
        link_data["flow"] = round(float(ep.getLinkFlows(link)), 3)
        # the same as speed = 0 or if the pipe is open of closed
        link_data["status"] = ep.getLinkStatus(link)

        match ep.getLinkType(link):
            case "PIPE":
                link_data["velocity"] = ep.getLinkVelocity(link)
                link_data["length"] = ep.getLinkLength(link)
                pass
            case "PUMP":
                # determent to be always 1
                link_data["power"] = ep.getLinkPumpPower(link)
                # used to change the rotation speed. 0 = off
                link_data["speed"] = float(ep.getLinkSettings(link))
                link_data["energy"] = ep.getLinkEnergy(link)
                link_data["efficeiency"] = ep.getLinkPumpEfficiency(link)
                link_data["state"] = ep.getLinkPumpState(link)
            # there are more valve types but only the TCV is used
            case "VALVE" | "TCV":
                link_data["velocity"] = ep.getLinkVelocity(link)
                pass
            case _:
                pass
        print(name, json.dumps(link_data))
        zone_data[name] = link_data
    return zone_data


def main():
    zone_ids = ["z0", "z1", "z2", "z3", "z4"]
    data = {zone: {} for zone in zone_ids}

    try:
        ep.openHydraulicAnalysis()
        ep.initializeHydraulicAnalysis(0)
        ep.runHydraulicAnalysis()
        for zone in zone_ids:
            nodes, links = get_zone_items(zone)
            # there is no way as of 11-12-2025 to get the tag value of the links and nodes
            # epyt has a way to add comments with setNodeComment() and setLinkComment()
            print(f"Working on zone {zone}")
            data[zone].update(get_linkdata(links))
            data[zone].update(get_nodedata(nodes))

            print("\n")
    finally:
        json.dump(data, open("epanet/app/test.json", "w"), indent=2)
        ep.closeHydraulicAnalysis()
        ep.unload()


if __name__ == "__main__":
    # global ep
    ep = epanet(r"C:\Users\wmhor\Bureaublad\HydroSim\epanet\app\scenario.inp")
    main()
