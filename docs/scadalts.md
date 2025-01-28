# ScadaLTS

**ScadaLTS** will serve as the **HMI (Human-Machine Interface)** for this simulation. It provides capabilities to manipulate the simulation and monitor the status of the water network in real time.


# PLEASE ADD PART ABOUT HOW TO BUILD HMI etc.


---

## Automatic Configuration

The ScadaLTS environment is automatically configured during deployment using a `.zip` configuration file located at:  
`/scadalts/config.zip`

The configuration is uploaded and applied using a mechanism described in the following GitHub discussion:  
[SCADA-LTS Discussion #2463](https://github.com/SCADA-LTS/Scada-LTS/discussions/2463).

This process is integrated into the `docker-compose.yaml` file, ensuring seamless setup without manual intervention.

```bash
curl -d "username=admin&password=admin&submit=Login" -c cookies http://localhost:8080/ScadaBR/login.htm
curl -b cookies -v -F importFile=/config.zip http://localhost:8080/ScadaBR/import_project.htm
curl 'http://localhost:8080/ScadaBR/dwr/call/plaincall/EmportDwr.loadProject.dwr' -X POST -b cookies --data-raw $'callCount=1\npage=/ScadaBR/import_project.htm\nhttpSessionId=\nscriptSessionId=D15BC242A0E69D4251D5585A07806324697\nc0-scriptName=EmportDwr\nc0-methodName=loadProject\nc0-id=0\nbatchId=5\n
```
