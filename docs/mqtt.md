# MQTT with TLS (MQTTS)

This Docker container contains the MQTT broker configuration and helper scripts to set up a secure MQTT (Mosquitto) connection using TLS/SSL encryption. This setup is designed to establish a secure connection between the remote server running the simulation environment and the physical hardware used for the physical display over the network.

## Purpose

The main goal is to allow physical hardware components to subscribe to the simulation securely. By using MQTTS (MQTT over TLS) on port 8883 and enforcing client certificate authentication, we ensure that only authorized devices can interact with the simulation.

## Directory Structure

- **certs/**: Stores the generated Certificate Authority (CA), server, and client certificates.
- **conf/**: Contains the `mosquitto.conf` configuration file.
- **Scripts**:
  - `generate_all.sh`: Master script to generate all necessary certificates. Calls the following individual shell scripts:
    - `generate_ca.sh`: Generates CA certificate.
    - `generate_server_certs.sh`: Generates server certifacte.
    - `generate_client_certs.sh`: Generates a client certificate.
  - `test_pub.sh` / `test_sub.sh`: Shell scripts to test publishing and subscribing (requires [mosquitto-clients](https://mosquitto.org/download/) on the machine).

## Setup & Certificates

To secure the connection, we use a custom Certificate Authority (CA) to sign both the server and client certificates. Mutual TLS (mTLS) is enforced, meaning both the server (broker) and the client must present valid certificates.

### Generating Certificates

1.  Navigate to the `mqtt` directory.
    ```bash
    cd mqtt
    ```
2.  Run the generation script:
    ```bash
    ./generate_all.sh
    ```
    **Note:** If the script doesn't run, you might need to change the permissions or the owner of the scripts to be allowed to execute this shell scripts (or you can run the script as sudo):
    ```bash
    # Change permissions
    sudo chmod +x generate_*

    # Change owner
    sudo chown [your_user] generate_*
    ```
3.  The script will:
    -   Generate a CA certificate and key in `mqtt/certs/ca/`.
    -   Generate a server certificate and key in `mqtt/certs/server/`.
    -   Ask for the number of clients to generate (e.g., if you need several devices to interact with the MQTT-broker).
    -   Generate client certificates in `mqtt/certs/client/` (e.g., `RPI.crt`, `HydroSim.crt`).

**Note:** Ensure that the Common Name (CN) used for the server certificate matches the hostname or IP address used by clients to connect (e.g., `145.52.x.x`).

## Configuration

### Mosquitto Configuration (`conf/mosquitto.conf`)

The broker is configured to listen on port **8883** (standard for MQTTS) and requires client certificates for authentication.

Key settings:
-   `listener 8883`: Listens on the secure port.
-   `cafile`, `certfile`, `keyfile`: Points to the generated certificates inside the container.
-   `require_certificate true`: **Crucial**. Enforces that clients must provide a valid certificate signed by the CA.
-   `use_identity_as_username true`: Uses the CN from the client certificate as the username.
-   `allow_anonymous false`: Disables unauthenticated access.

### Docker Configuration (`docker-compose.yaml`)

The service maps the local configuration and certificates into the container:

```yaml
volumes:
  - ./mqtt/conf:/mosquitto/config
  - ./mqtt/certs:/mosquitto/certs
```

It exposes port `8883` to the host.

## Usage

### Starting the Broker

To start the MQTT broker, run:

```bash
docker-compose up -d
```

### Testing Connectivity

You can verify the setup using the provided scripts. These scripts assume `mosquitto-clients` is installed on your machine.

**1. Subscribe (Listener):**
You'll need to change most of the arguments passed:
  - The `--host` argument needs to be changed to the CN (IP-address of the broker).
  - The `--cafile`, `--cert` and `--key` arguments need to be changed to the certificates you created (e.g., `ca.crt`, `RPI.crt` & `RPI.key`).
  - The `--topic` needs to be changed to the topic the server will be publishing on. You can also pas a wildcard (#) if you want to receive all published data.

  Now run the script:
```bash
./test_sub.sh
```

**2. Publish (Sender):**
You'll also need to change most of these arguments: 
  - The `--host` argument needs to be changed to the CN (IP-address of the broker).
  - The `--cafile`, `--cert` and `--key` arguments need to be changed to the certificates you created (e.g., `ca.crt`, `test_pub.crt` & `test_pub.key`).
  - The `--topic` needs to be changed to a topic of your choosing.

  Now run the script:
```bash
./test_pub.sh
```

## Integration with Simulation

To connect the simulation (e.g., `epanet`) to this broker, a MQTT client has been integrated into the epanet code. A JSON file is created by epanet and published to the topic defined in the environment variables (`.env`) as `MQTT-TOPIC`.
