PROGRAM Zone1Logica
  VAR
    (* Pomp 1: Run=Coil 0, Cmd=Coil 1 *)
    Pump_Run   AT %QX0.0 : BOOL;
    Pump_Cmd   AT %QX0.1 : BOOL;

    (* Klep 0: Run=Coil 2, Cmd=Coil 3 *)
    Valve0_Run AT %QX0.2 : BOOL;
    Valve0_Cmd AT %QX0.3 : BOOL;

    (* Klep 1: Run=Coil 4, Cmd=Coil 5 *)
    Valve1_Run AT %QX0.4 : BOOL;
    Valve1_Cmd AT %QX0.5 : BOOL;
  END_VAR

  Pump_Run   := Pump_Cmd;
  Valve0_Run := Valve0_Cmd;
  Valve1_Run := Valve1_Cmd;

END_PROGRAM

CONFIGURATION Config0
  RESOURCE Res0 ON PLC
    TASK TaskMain(INTERVAL := T#50ms,PRIORITY := 0);
    PROGRAM Inst0 WITH TaskMain : Zone1Logica;
  END_RESOURCE
END_CONFIGURATION