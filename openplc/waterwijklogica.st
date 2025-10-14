PROGRAM program0
  VAR
    StartSwitch AT %IX0.0 : BOOL;
    LowPressureSensor AT %IX0.1 : BOOL;
    HighPressureSensor AT %IX0.2 : BOOL;
    FaultSensor AT %IX0.3 : BOOL;
    EmergencyStop AT %IX0.4 : BOOL;
    MainPump AT %QX0.0 : BOOL;
    Alarm AT %QX0.1 : BOOL;
  END_VAR

  MainPump := StartSwitch AND LowPressureSensor AND NOT(HighPressureSensor) AND NOT(FaultSensor) AND NOT(EmergencyStop);
  Alarm := FaultSensor OR EmergencyStop;
END_PROGRAM

CONFIGURATION Config0

  RESOURCE Res0 ON PLC
    TASK task0(INTERVAL := T#20ms, PRIORITY := 0);
    PROGRAM instance0 WITH task0 : program0;
  END_RESOURCE
END_CONFIGURATION
