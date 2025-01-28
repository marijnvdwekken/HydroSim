# OpenPLC in the Simulation Environment

This project integrates OpenPLC for simulating programmable logic controllers (PLCs) within the virtual environment. It leverages the repository [OpenPLC-Docker-AutoStart](https://github.com/koztkozt/OpenPLC-Docker-AutoStart) to automate the import and configuration of PLCs using pre-defined `.ST` files during the build process.

## Purpose and Functionality

The OpenPLC setup allows for the inclusion of multiple PLCs to control various zones within the simulation environment. Each PLC can be configured with a specific `.ST` (Structured Text) file, representing the logic for that zone. This provides flexibility in designing complex scenarios involving different operational zones.

## Adding a PLC

To add a new PLC to the environment, you can modify the `docker-compose.yaml` file. Use the following syntax as a template:

```yaml
plc-zone*:
  container_name: plc-zone* # Replace * with the zone name (e.g., plc-zone1, plc-zone2)
  depends_on:
    - scadalts
  build:
    context: ./openplc/.
    dockerfile: Dockerfile
    args:
      script: watertanklogica.st # Replace with the .ST file the PLC should execute
      database: database.sh # Database script; do not modify
  ports:
    - "8082:8080" # Port mapping for external access and debugging; can be disabled if not required
  expose:
    - "502" # Modbus/TCP communication port
    - "8080" # WebUI access; can be removed if not needed
  networks:
    - plc_network
```
![image](https://github.com/user-attachments/assets/b71d7090-d1b7-488d-b714-3ad051348537)


