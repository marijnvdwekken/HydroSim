# **Scada-LTS Offsets (Pompen & Kleppen)**

## **Zone 0 (plc-zone0)**

| Naam | Type | Offset (Lezen) | Offset (Schakelaar) | Opmerking |
| :---- | :---- | :---- | :---- | :---- |
| **Pomp 0** | Coil | 0 | 4 |  |
| **Pomp 1** | Coil | 1 | 5 |  |
| **Pomp 2** | Coil | 2 | 6 |  |
| **Pomp 3** | Coil | 3 | 7 |  |
|  |  |  |  |  |
| **Valve** (Reservoir) | Coil | 8 | 17 | %QX1.0 / %QX2.1 |
| **Valve01** (T0 Uit) | Coil | 9 | 18 |  |
| **Valve00** (T0 In) | Coil | 10 | 19 |  |
| **Valve10** (T1 In) | Coil | 11 | 20 |  |
| **Valve11** (T1 Uit) | Coil | 12 | 21 |  |
| **Valve20** (T2 In) | Coil | 13 | 22 |  |
| **Valve21** (T2 Uit) | Coil | 14 | 23 |  |
| **Valve30** (T3 In) | Coil | 15 | 24 |  |
| **Valve31** (T3 Uit) | Coil | 16 | 25 |  |

## **Zone 1, 2, 3 en 4 (plc-zoneX)**

| Naam | Type | Offset (Lezen) | Offset (Schakelaar) | Opmerking |
| :---- | :---- | :---- | :---- | :---- |
| **Pomp 1** | Coil | 0 | 1 |  |
| **Klep 0** (Valve0) | Coil | 2 | 3 | %QX0.2 / %QX0.3 |
| **Klep 1** (Valve1) | Coil | 4 | 5 | %QX0.4 / %QX0.5 |

