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

With the compromised employee credentials, an attacker can gain access to the **ScadaLTS environment**, which runs **`ScadaLTS v2.7.5.2`**. This version is vulnerable to **CVE-2023-33472**, a security flaw that allows:
- **Privilege escalation** from an unprivileged account.
- **Arbitrary code execution**.
- **Extraction of sensitive information** via the **Event Handlers** function.

### HMI Manipulation Attack
Once an attacker gains administrative privileges, they can manipulate key values, alarms, and views within the **HMI (Human-Machine Interface)**. This could lead to:
- Displaying **false alarms** or **suppressing critical alarms**, misleading operators.
- Direct manipulation of the **water control system**, potentially causing damage or disruption.
- Unauthorized changes to **process values**, leading to incorrect decision-making by operators.

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

---

## Conclusion

The **OT SIM** environment contains multiple security weaknesses, including outdated software, exposed interfaces, and weak authentication mechanisms. If exploited, these vulnerabilities could lead to:
- **Remote code execution** on critical components.
- **Unauthorized access** to SCADA and PLC systems.
- **Disruption of industrial processes**, potentially causing damage.
