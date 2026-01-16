PROGRAM Zone0Logica
  VAR
    Pump0_Run AT %QX0.0 : BOOL;
    Pump1_Run AT %QX0.1 : BOOL;
    Pump2_Run AT %QX0.2 : BOOL;
    Pump3_Run AT %QX0.3 : BOOL;

    Pump0_Cmd AT %QX0.4 : BOOL;
    Pump1_Cmd AT %QX0.5 : BOOL;
    Pump2_Cmd AT %QX0.6 : BOOL;
    Pump3_Cmd AT %QX0.7 : BOOL;

    Valve0_Run AT %QX1.0 : BOOL;
    Valve1_Run AT %QX1.1 : BOOL;
    Valve2_Run AT %QX1.2 : BOOL;
    Valve3_Run AT %QX1.3 : BOOL;
    Valve4_Run AT %QX1.4 : BOOL;
    Valve5_Run AT %QX1.5 : BOOL;
    Valve6_Run AT %QX1.6 : BOOL;
    Valve7_Run AT %QX1.7 : BOOL;
    Valve8_Run AT %QX2.0 : BOOL;

    Valve0_Cmd AT %QX2.1 : BOOL;
    Valve1_Cmd AT %QX2.2 : BOOL;
    Valve2_Cmd AT %QX2.3 : BOOL;
    Valve3_Cmd AT %QX2.4 : BOOL;
    Valve4_Cmd AT %QX2.5 : BOOL;
    Valve5_Cmd AT %QX2.6 : BOOL;
    Valve6_Cmd AT %QX2.7 : BOOL;
    Valve7_Cmd AT %QX3.0 : BOOL;
    Valve8_Cmd AT %QX3.1 : BOOL;

    T0_Low AT %IX0.0 : BOOL;
    T0_High AT %IX0.1 : BOOL;

    T1_High AT %IX0.2 : BOOL;
    T1_Low AT %IX0.3 : BOOL;

    T2_High AT %IX0.4 : BOOL;
    T2_Low AT %IX0.5 : BOOL;

    T3_High AT %IX0.6 : BOOL;
    T3_Low AT %IX0.7 : BOOL;



  END_VAR



  Valve0_Run := Valve0_Cmd;
  Valve1_Run := Valve1_Cmd;
  Valve2_Run := Valve2_Cmd;
  Valve3_Run := Valve3_Cmd;
  Valve4_Run := Valve4_Cmd;
  Valve5_Run := Valve5_Cmd;
  Valve6_Run := Valve6_Cmd;
  Valve7_Run := Valve7_Cmd;
  Valve8_Run := Valve8_Cmd;
  IF Valve0_Run = 0 THEN
    Pump0_Cmd := 0;
    Pump1_Cmd := 0;
    Pump2_Cmd := 0;
    Pump3_Cmd := 0;
  END_IF;

  Pump0_Run := Pump0_Cmd;
  Pump1_Run := Pump1_Cmd;
  Pump2_Run := Pump2_Cmd;
  Pump3_Run := Pump3_Cmd;
END_PROGRAM

CONFIGURATION Config0
  RESOURCE Res0 ON PLC
    TASK TaskMain(INTERVAL := T#50ms,PRIORITY := 0);
    PROGRAM Inst0 WITH TaskMain : Zone0Logica;
  END_RESOURCE
END_CONFIGURATION