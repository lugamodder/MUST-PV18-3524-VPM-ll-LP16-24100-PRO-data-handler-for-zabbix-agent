import minimalmodbus
import time
import os
import json

# Параметры последовательного порта
SERPORT = os.getenv("SERPORT", "/dev/ttyUSB0")
SERTIMEOUT = float(os.getenv("SERTIMEOUT", "1.0"))
SERBAUD = int(os.getenv("SERBAUD", "19200"))
INTERVAL = int(os.getenv("INTERVAL", "10"))
PAUSE_BETWEEN_READS = 0.3

# Карта регистров
register_map = {
    109: ["BMS_Battery_Voltage", "BMS Battery Voltage", 0.1, "V"],
    110: ["BMS_Battery_Current", "BMS Battery Current", 0.1, "A"],
    111: ["BMS_Battery_Temperature", "BMS Battery Temperature", 1, "C"],
    112: ["BMS_Battery_Errors", "BMS Battery Error", 1, ""],
    113: ["BMS_Battery_SOC", "BMS Battery SOC", 1, "%"],
    114: ["BMS_Battery_SOH", "BMS Battery SOH", 1, "%"],
    25201: [
        "workState", "Work state", 1, "map",
        {
            0: "PowerOn", 1: "SelfTest", 2: "OffGrid", 3: "Grid-Tie",
            4: "Bypass", 5: "Stop", 6: "Grid Charging",
        },
    ],
    25205: ["batteryVoltage", "Battery voltage", 0.1, "V"],
    25206: ["inverterVoltageOut", "Inverter voltage", 0.1, "V"],
    25207: ["gridVoltageIn", "Grid voltage", 0.1, "V"],
#    25208: ["busVoltage", "BUS voltage", 0.1, "V"],
#    25209: ["controlCurrent", "Control current", 0.1, "A"],
    25210: ["inverterCurrentOut", "Inverter current", 0.1, "A"],
    25211: ["gridCurrentIn", "Grid current", 0.1, "A"],
    25212: ["loadCurrentOut", "Load current", 0.1, "A"],
    25213: ["inverterPower", "Inverter power(P)", 1, "W"],
    25214: ["gridPowerIn", "Grid power(P)", 1, "W"],
    25215: ["loadPowerOut", "Load power(P)", 1, "W"],
    25216: ["loadPercentTotal", "Load percent", 1, "%"],
    25217: ["inverterComplexPowerSelf", "Inverter complex power(S)", 1, "VA"],
    25218: ["gridComplexPowerIn", "Grid complex power(S)", 1, "VA"],
    25219: ["loadComplexPowerOut", "Load complex power(S)", 1, "VA"],
    25221: ["inverterReactivePower", "Inverter reactive power(Q)", 1, "var"],
    25222: ["gridReactivePower", "Grid reactive power(Q)", 1, "var"],
    25223: ["loadReactivePower", "Load reactive power(Q)", 1, "var"],
    25225: ["inverterFrequencyOut", "Inverter frequency", 0.01, "Hz"],
    25226: ["gridFrequencyIn", "Grid frequency", 0.01, "Hz"],
    25233: ["acRadiatorTemperature", "AC radiator temperature", 1, "C"],
#    25234: ["transformerTemperature", "Transformer temperature", 1, "C"],
    25235: ["dcRadiatorTemperature", "DC radiator temperature", 1, "C"],
#    25237: ["InverterRelayState", "InverterRelayState", 1, "on/off"],
#    25238: ["GridRelayState", "GridRelayState", 1, "on/off"],
#    25239: ["LoadRelayState", "LoadRelayState", 1, "on/off"],
#    25240: ["N_LineRelayState", "N_LineRelayState", 1, "on/off"],
#    25241: ["DCRelayState", "DCRelayState", 1, "on/off"],
#    25242: ["EarthRelayState", "EarthRelayState", 1, "on/off"],
#    25245: ["AccumulatedChargerPowerM", "AccumulatedChargerPowerM", 1, "MWh"],
#    25246: ["AccumulatedChargerPower", "AccumulatedChargerPower", 1, "kWh"],
#    25247: ["AccumulatedDischargerPowerM", "AccumulatedDischargerPowerM", 1, "MWh"],
#    25248: ["AccumulatedDischargerPower", "AccumulatedDischargerPower", 1, "kWh"],
#    25249: ["AccumulatedBuyPowerM", "AccumulatedBuyPowerM", 1, "MWh"],
#    25250: ["AccumulatedBuyPower", "AccumulatedBuyPower", 1, "kWh"],
#    25251: ["AccumulatedSellPowerM", "AccumulatedSellPowerM", 1, "MWh"],
#    25252: ["AccumulatedSellPower", "AccumulatedSellPower", 1, "kWh"],
#    25253: ["AccumulatedLoadPowerM", "AccumulatedLoadPowerM", 1, "MWh"],
#    25254: ["AccumulatedLoadPower", "AccumulatedLoadPower", 1, "kWh"],
#    25255: ["AccumulatedSelfUsePowerM", "AccumulatedSelfUsePowerM", 1, "MWh"],
#    25256: ["AccumulatedSelfUsePower", "AccumulatedSelfUsePower", 1, "kWh"],
#    25257: ["AccumulatedPvSellPowerM", "AccumulatedPvSellPowerM", 1, "MWh"],
#    25258: ["AccumulatedPvSellPower", "AccumulatedPvSellPower", 1, "kWh"],
#    25259: ["AccumulatedGridChargerPowerM", "AccumulatedGridChargerPowerM", 1, "MWh"],
#    25260: ["AccumulatedGridChargerPower", "AccumulatedGridChargerPower", 1, "kWh"],
    25261: ["InverterErrorMessage", "InverterErrorMessage", 1, ""],
    25265: ["InverterWarningMessage", "InverterWarningMessage", 1, ""],
    25273: ["batteryPower", "Battery power", 1, "W"],
    25274: ["batteryCurrent", "Battery current", 1, "A"],
#    25279: ["ArrowFlag", "Arrow Flag", 1, ""],
#    20109: [
#        "EnergyUseMode", "Energy use mode", 1, "map",
#        {0: "-", 1: "SBU", 2: "SUB", 3: "UTI", 4: "SOL"},
#    ],
#    20111: [
#        "Grid_protect_standard", "Grid protect standard", 1, "map",
#        {0: "VDE4105", 1: "UPS", 2: "HOME", 3: "GEN"},
#    ],
#    20112: [
#        "SolarUseAim", "SolarUse Aim", 1, "map",
#        {0: "LBU", 1: "BLU"},
#    ],
#    20113: ["Inv_max_discharger_cur", "Inverter max discharger current", 0.1, "A"],
    20118: ["BatStopDischargingV", "Battery stop discharging voltage", 0.1, "V"],
    20119: ["BatStopChargingV", "Battery stop charging voltage", 0.1, "V"],
    20125: ["GridMaxChargerCurSet", "Grid max charger current set", 0.1, "A"],
    20127: ["BatLowVoltage", "Battery low voltage", 0.1, "V"],
    20128: ["BatHighVoltage", "Battery high voltage", 0.1, "V"],
    15201: [
        "ChargerWorkstate", "Charger Workstate", 1, "map",
        {0: "Initialization", 1: "Selftest", 2: "Work", 3: "Stop"},
    ],
#    15202: [
#        "MpptState", "Mppt State", 1, "map",
#        {0: "Stop", 1: "MPPT", 2: "Current limiting"},
#    ],
    15203: [
        "ChargingState", "Charging State", 1, "map",
        {0: "Stop", 1: "Absorb charge", 2: "Float charge", 3: "Equalization charge"},
    ],
#    15205: ["PvVoltage", "Pv. Voltage", 0.1, "V"],
#    15206: ["chBatteryVoltage", "Ch. Battery Voltage", 0.1, "V"],
    15207: ["chChargerCurrent", "Ch. Charger Current", 0.1, "A"],
    15208: ["ChargerPower", "Ch. Charger Power", 1, "W"],
#    15209: ["RadiatorTemperature", "Ch. Radiator Temperature", 1, "C"],
#    15210: ["ExternalTemperature", "Ch. External Temperature", 1, "C"],
#    15211: ["BatteryRelay", "Battery Relay", 1, ""],
#    15212: ["PvRelay", "Pv. Relay", 1, ""],
#    15213: ["ChargerErrorMessage", "Charger Error Message", 1, ""],
#    15214: ["ChargerWarningMessage", "Charger Warning Message", 1, ""],
#    15215: ["BattVolGrade", "BattVolGrade", 1, "V"],
#    15216: ["RatedCurrent", "Rated Current", 0.1, "A"],
#    15217: ["AccumulatedPowerM", "Accumulated PowerM", 1, "MWh"],
#    15218: ["AccumulatedPower", "Accumulated Power", 1, "kWh"],
#    15219: ["AccumulatedTimeDay", "Accumulated Time day", 1, "d"],
}

def to_signed(value):
    if value >= 0x8000:
        value -= 0x10000
    return value

def read_register_values(i, startreg, count, functioncode=3):
    stats = {}
    results = i.read_registers(startreg, count, functioncode=functioncode)
    register_id = startreg
    for r in results:
        if register_id in register_map:
            r_key = register_map[register_id][0]
            scale = register_map[register_id][2]

            # если ток или мощность — интерпретируем как знаковое значение
            if any(word in r_key.lower() for word in ["current", "power"]):
                r = to_signed(r)

            r_value = round(r * scale, 2)

            if len(register_map[register_id]) > 4 and register_map[register_id][3] == "map":
                map_dict = register_map[register_id][4]
                r_value = map_dict.get(r, f"Unknown({r})")

            stats[r_key] = r_value
        register_id += 1
    return stats


def main():
    try:
        i = minimalmodbus.Instrument(SERPORT, 4)
        i.serial.timeout = SERTIMEOUT
        i.serial.baudrate = SERBAUD

        stats = read_register_values(i, 25201, 125)
        time.sleep(PAUSE_BETWEEN_READS)
        bms = read_register_values(i, 109, 6)
        time.sleep(PAUSE_BETWEEN_READS)
        config = read_register_values(i, 20109, 125)
        time.sleep(PAUSE_BETWEEN_READS)
        other = read_register_values(i, 15201, 125)

        all_stats = {**stats, **bms, **config, **other}

        # выводим JSON
        print(json.dumps(all_stats, ensure_ascii=False, indent=2))

    except Exception as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))

if __name__ == "__main__":
    main()
