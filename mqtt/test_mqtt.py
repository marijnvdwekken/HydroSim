import os, sys, json
import paho.mqtt.client as mqtt

BROKER = os.getenv("MQTT_BROKER_URL","mqtt://192.168.2.55")
TOPIC = os.getenv("MQTT_TOPIC", "test/topic")

CA = os.getenv("MQTT_CA_CERT","certs/ca/ca.crt")
KEY = os.getenv("MQTT_CLIENT_KEY","certs/server/server.key")
CERT = os.getenv("MQTT_CLIENT_CERT","certs/server/server.crt")
TLS = os.getenv("MQTT_TLS_ENABLED","true") == "true"

client = mqtt.Client(client_id=f"mqtt-publisher-{os.urandom(4).hex()}")

if TLS and CA and KEY and CERT:
    client.tls_set(ca_certs=CA, certfile=CERT, keyfile=KEY)
    client.tls_insecure_set(True)
    host = BROKER.split("://")[-1]
    print(f"Connecting TLS to {host}:8883")
    client.connect(host, 8883)
else:
    print(f"Connecting to {BROKER} without TLS")
    client.connect(BROKER.split("://")[-1])

client.loop_start()

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    print("Received:", line)
    client.publish(TOPIC, line)
    print("Published to", TOPIC)
client.loop_stop()
client.disconnect()
print("Shutting down.")