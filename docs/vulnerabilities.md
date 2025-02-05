# 1. Vulnerabilities in OT-Simulation

The **OT SIM** environment consists of the following components:

1. **Epanet container**  
2. **Web server**  
3. **ScadaLTS**  
4. **Database for ScadaLTS**  
5. **OpenPLC (multiple instances)**

For each one of these components we have researched its attack surfaces and have archived different vulnerabilities that can be used to exploit.  

## 2. Web Server

The web server runs on a **`wordpress:5.8-php7.4-apache`** container. Within this container, an outdated and vulnerable version of Bash is installed: **`bash-3.1`**, which is susceptible to the **Shellshock vulnerability**. This allows an attacker to exploit remote command execution (RCE) through a vulnerable script that can be triggered remotely.

Additionally, the server contains credentials for an employee account, which could be compromised and used for further attacks.

---

## 3. ScadaLTS

The **ScadaLTS environment** is protected by a login screen, but it is susceptible to brute-force attacks.

With the compromised employee credentials, an attacker can gain access to the **ScadaLTS environment**, which runs **`ScadaLTS v2.7.5.2`**. This version is vulnerable to **CVE-2023-33472** / **CVE-2022-41976**, a security flaw that allows:
- **Privilege escalation** from an unprivileged account.
- **Arbitrary code execution**.
- **Extraction of sensitive information** via the **Event Handlers** function.

### HMI Manipulation Attack
Once an attacker gains administrative privileges, they can manipulate key values, alarms, and views within the **HMI (Human-Machine Interface)**. This could lead to:
- Displaying **false alarms** or **suppressing critical alarms**, misleading operators.
- Direct manipulation of the **water control system**, potentially causing damage or disruption.
- Unauthorized changes to **process values**, leading to incorrect decision-making by operators.

### CVE's
- **CVE-2022-41976**
  An privilege escalation issue was discovered in Scada-LTS 2.7.1.1 build 2948559113 allows remote attackers, authenticated in the application as a low-privileged user to change role (e.g., to administrator) by updating their user profile.

- **CVE-2023-33472**
  An issue was discovered in Scada-LTS v2.7.5.2 build 4551883606 and before, allows remote attackers with low-level authentication to escalate privileges, execute arbitrary code, and obtain sensitive information via Event Handlers function.

- **CVE-2024-7901**
  A vulnerability has been found in Scada-LTS 2.7.8 and classified as problematic. Affected by this vulnerability is an unknown functionality of the file /Scada-LTS/app.shtm#/alarms/Scada of the component Message Handler. The manipulation leads to cross site scripting. The attack can be launched remotely. The exploit has been disclosed to the public and may be used. NOTE: A fix is planned for the upcoming release at the end of September 2024.

---

## 5. OpenPLC

The **PLCs (Programmable Logic Controllers)** are accessible from the **HMI**, and the **Modbus port** is open. If the PLCs are not securely programmed, attackers can directly control pumps and other equipment, bypassing normal operational logic.

### Modbus-Based Attacks
- An attacker could **overwrite operator instructions**.  
  - *Example:* If an operator sends a command to **turn off a pump for maintenance**, an attacker could continuously send **Modbus write commands**, reversing the operator’s action. This would prevent the operator from successfully controlling the PLC.
- If **authentication and access control** are weak, attackers can send unauthorized commands to manipulate industrial processes.

### Web Interface Vulnerability
- **Port 8080** is open on the PLCs, exposing the **PLC’s web interface**, where values can be viewed, and new logic can be uploaded.
- The web interface is protected by a login screen, but **default credentials** may still be in use, or they could be brute-forced.
- If compromised, an attacker could **remove critical safety functions**, allowing for unsafe operation of the water network.

### CVE's
- **CVE-2018-20818**  
  A buffer overflow vulnerability was discovered in the OpenPLC controller, in the OpenPLC_v2 and OpenPLC_v3 versions. It occurs in the `modbus.cpp` `mapUnusedIO()` function, which can cause a runtime crash of the PLC or possibly have unspecified other impacts.

- **CVE-2021-3351**  
  OpenPLC runtime V3 through 2016-03-14 allows stored XSS via the Device Name to the web server's "Add New Device" page.

- **CVE-2021-31630**  
  Command Injection in OpenPLC Webserver v3 allows remote attackers to execute arbitrary code via the "Hardware Layer Code Box" component on the `/hardware` page of the application. *(Authentication required)* **POC Available**  

- **CVE-2024-34026**  
  A stack-based buffer overflow vulnerability exists in the OpenPLC Runtime EtherNet/IP parser functionality of OpenPLC_v3 `b4702061dc14d1024856f71b4543298d77007b88`. A specially crafted EtherNet/IP request can lead to remote code execution. An attacker can send a series of EtherNet/IP requests to trigger this vulnerability.

- **CVE-2024-36980**  
  An out-of-bounds read vulnerability exists in the OpenPLC Runtime EtherNet/IP PCCC parser functionality of OpenPLC_v3 `b4702061dc14d1024856f71b4543298d77007b88`. A specially crafted network request can lead to denial of service. An attacker can send a series of EtherNet/IP requests to trigger this vulnerability. *This is the first instance of the incorrect comparison.*

- **CVE-2024-36981**  
  An out-of-bounds read vulnerability exists in the OpenPLC Runtime EtherNet/IP PCCC parser functionality of OpenPLC_v3 `b4702061dc14d1024856f71b4543298d77007b88`. A specially crafted network request can lead to denial of service. An attacker can send a series of EtherNet/IP requests to trigger this vulnerability. *This is the final instance of the incorrect comparison.*

- **CVE-2024-37741**  
  OpenPLC 3 through `9cd8f1b` allows XSS via an SVG document as a profile picture.

- **CVE-2024-39589**  
  Multiple invalid pointer dereference vulnerabilities exist in the OpenPLC Runtime EtherNet/IP parser functionality of OpenPLC_v3 `16bf8bac1a36d95b73e7b8722d0edb8b9c5bb56a`. A specially crafted EtherNet/IP request can lead to denial of service. An attacker can send a series of EtherNet/IP requests to trigger these vulnerabilities. *This instance of the vulnerability occurs within the `Protected_Logical_Read_Reply` function.*

- **CVE-2024-39590**  
  Multiple invalid pointer dereference vulnerabilities exist in the OpenPLC Runtime EtherNet/IP parser functionality of OpenPLC_v3 `16bf8bac1a36d95b73e7b8722d0edb8b9c5bb56a`. A specially crafted EtherNet/IP request can lead to denial of service. An attacker can send a series of EtherNet/IP requests to trigger these vulnerabilities. *This instance of the vulnerability occurs within the `Protected_Logical_Write_Reply` function.*

  
---

## Conclusion

The **OT SIM** environment contains multiple security weaknesses, including outdated software, exposed interfaces, and weak authentication mechanisms. If exploited, these vulnerabilities could lead to:
- **Remote code execution** on critical components.
- **Unauthorized access** to SCADA and PLC systems.
- **Disruption of industrial processes**, potentially causing damage.
