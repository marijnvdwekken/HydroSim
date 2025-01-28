# ScadaLTS Configuration

**ScadaLTS** will serve as the **HMI (Human-Machine Interface)** for this simulation. It provides capabilities to manipulate the simulation and monitor the status of the water network in real time.

## Automatic Configuration

The ScadaLTS environment is automatically configured during deployment using a `.zip` configuration file located at:  
`/scadalts/config.zip`

The configuration is uploaded and applied using a mechanism described in the following GitHub discussion:  
[SCADA-LTS Discussion #2463](https://github.com/SCADA-LTS/Scada-LTS/discussions/2463).

This process is integrated into the `docker-compose.yaml` file, ensuring seamless setup without manual intervention.

---

## Manual Configuration Steps

If manual configuration is required, follow these steps to log in, upload the configuration file, and import the project.

### 1. Login to ScadaLTS

Use the following `curl` command to log in as the **admin user**:

```bash
curl -d "username=admin&password=admin&submit=Login" -c cookies http://localhost:8080/ScadaBR/login.htm
