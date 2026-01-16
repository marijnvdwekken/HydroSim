PROGRAM program0
  VAR
    StartSwitch AT %IX0.0 : BOOL := TRUE;
    LowPressureSensor AT %IX0.1 : BOOL;
    HighPressureSensor AT %IX0.2 : BOOL;
    FaultSensor AT %IX0.3 : BOOL;
    EmergencyStop AT %IX0.4 : BOOL;
    MainPump AT %QX0.0 : BOOL;
    Alarm AT %QX0.1 : BOOL;
    PumpSpeed AT %MD1000 : REAL;
    PumpSpeedBits AT %MD1006 : DWORD;
    Pump1SpeedHigh AT %QW1000 : WORD;
    Pump1SpeedLow AT %QW1001 : WORD;
    Pump2SpeedHigh AT %QW1002 : WORD;
    Pump2SpeedLow AT %QW1003 : WORD;
    Pump3SpeedHigh AT %QW1004 : WORD;
    Pump3SpeedLow AT %QW1005 : WORD;
  END_VAR

  MainPump := StartSwitch;
  Alarm := FaultSensor OR EmergencyStop;

  IF MainPump THEN
    PumpSpeed := 1.0;
  ELSE
    PumpSpeed := 0.0;
  END_IF;

  PumpSpeedBits := REAL_TO_DWORD(PumpSpeed);
  Pump1SpeedHigh := DWORD_TO_WORD(SHR(IN := PumpSpeedBits, N := 16));
  Pump1SpeedLow := DWORD_TO_WORD(PumpSpeedBits AND DWORD#16#0000FFFF);
  Pump2SpeedHigh := Pump1SpeedHigh;
  Pump2SpeedLow := Pump1SpeedLow;
  Pump3SpeedHigh := Pump1SpeedHigh;
  Pump3SpeedLow := Pump1SpeedLow; 
END_PROGRAM

CONFIGURATION Config0

  RESOURCE Res0 ON PLC
    TASK task0(INTERVAL := T#20ms, PRIORITY := 0);
    PROGRAM instance0 WITH task0 : program0;
  END_RESOURCE
END_CONFIGURATION