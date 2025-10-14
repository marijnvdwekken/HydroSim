PROGRAM program0
  VAR
    LowLevelSensor AT %IX0.5 : BOOL;
    ZoneAButton AT %IX0.6 : BOOL;
    ZoneBButton AT %IX0.7 : BOOL;
    ZoneCButton AT %IX1.0 : BOOL;
    ZoneDButton AT %IX1.1 : BOOL;
    HighLevelSensor AT %IX0.4 : BOOL;
    OverFlowSensor AT %IX0.3 : BOOL;
    Pump AT %QX0.1 : BOOL;
    Alarm AT %QX0.0 : BOOL;
    StartButton AT %IX0.0 : BOOL;
    StopButton AT %IX0.1 : BOOL;
    DrainButton AT %IX0.2 : BOOL;
    DrainValve AT %QX0.3 : BOOL;
    ValveZoneA AT %QX0.4 : BOOL;
    ValveZoneB AT %QX0.5 : BOOL;
    ValveZoneC AT %QX0.6 : BOOL;
    ValveZoneD AT %QX0.7 : BOOL;
  END_VAR

  Pump := NOT(StopButton) AND (Pump OR (LowLevelSensor AND StartButton));
  Alarm := OverFlowSensor;
  DrainValve := DrainButton AND NOT(LowLevelSensor);
  ValveZoneA := ZoneAButton;
  ValveZoneB := ZoneBButton;
  ValveZoneC := ZoneCButton;
  ValveZoneD := ZoneDButton;
END_PROGRAM

CONFIGURATION Config0

  RESOURCE Res0 ON PLC
    TASK task0(INTERVAL := T#20ms, PRIORITY := 0);
    PROGRAM instance0 WITH task0 : program0;
  END_RESOURCE
END_CONFIGURATION
