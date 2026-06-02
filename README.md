# ESPHome Victron Grid Meter — DSMR P1 to Cerbo GX via Modbus TCP

**Turn a Dutch DSMR P1 smart meter into a Victron grid energy meter — no extra hardware required.**

An ESPHome external component that emulates a Carlo Gavazzi EM24 Ethernet energy meter over Modbus TCP (port 502). It bridges Dutch P1 smart meter data (read by an ESP32) to a Victron Cerbo GX, which recognizes it as a compatible grid meter.

**Supports both single-phase and three-phase configurations.**

**Keywords:** ESPHome Victron grid meter, DSMR P1 Cerbo GX, ESP32 Modbus TCP grid meter, Carlo Gavazzi EM24 emulator, Victron ESS P1 meter, victron-grid-meter-esphome, three-phase

## How it works

The component runs a Modbus TCP server directly on the ESP32. On each loop iteration it reads live sensor values from the ESPHome DSMR P1 component and writes them into a register array matching the Carlo Gavazzi EM24 format. The Victron Cerbo GX probes the device via Modbus function codes 03 (read holding registers) and 04 (read input registers), then polls it for grid power/voltage/current updates.

### Why EM24, not ET112?

The Victron Cerbo GX uses `dbus-modbus-client` for TCP energy meters. That driver's `carlo_gavazzi.py` only recognises Carlo Gavazzi EM24 Ethernet model IDs (1648–1653) over TCP — ET112 model IDs only work via RS485.

## Register map (Carlo Gavazzi EM24 — three-phase)

All multi-register values use **little-endian word order** (low word at lower address, `Reg_s32l`).

| Address       | Field                   | Type   | Scale        | Notes                          |
|---------------|-------------------------|--------|--------------|--------------------------------|
| 0x0000–0x0001 | L1 Voltage              | int32  | ÷10 V        | hold-on-NaN                    |
| 0x0002–0x0003 | L2 Voltage              | int32  | ÷10 V        | hold-on-NaN                    |
| 0x0004–0x0005 | L3 Voltage              | int32  | ÷10 V        | hold-on-NaN                    |
| 0x000B        | Model ID                | uint16 | —            | 1648 (EM24DINAV23XE1X)         |
| 0x000C–0x000D | L1 Current              | int32  | ÷1000 A      | positive magnitude; hold-on-NaN |
| 0x000E–0x000F | L2 Current              | int32  | ÷1000 A      | positive magnitude; hold-on-NaN |
| 0x0010–0x0011 | L3 Current              | int32  | ÷1000 A      | positive magnitude; hold-on-NaN |
| 0x0012–0x0013 | L1 Active power         | int32  | ÷10 W        | positive = import              |
| 0x0014–0x0015 | L2 Active power         | int32  | ÷10 W        | positive = import              |
| 0x0016–0x0017 | L3 Active power         | int32  | ÷10 W        | positive = import              |
| 0x0028–0x0029 | Total active power      | int32  | ÷10 W        | sum of L1+L2+L3                |
| 0x0033        | Frequency               | uint16 | ÷10 Hz       | hardcoded 50.0 Hz              |
| 0x0034–0x0035 | Energy import total     | int32  | ÷10 kWh      | T1+T2                          |
| 0x004E–0x004F | Energy export total     | int32  | ÷10 kWh      | T1+T2                          |
| 0x0302        | HW version              | uint16 | —            | 0x0100 (1.0.0)                 |
| 0x0304        | FW version              | uint16 | —            | 0x0100 (1.0.0)                 |
| 0x1002        | Phase config            | uint16 | —            | 0 = 3P (three-phase), 3 = 1P (single-phase) |
| 0xa000        | Application             | uint16 | —            | 7 = H mode (required by Cerbo) |

- Power is signed: positive = importing from grid, negative = exporting
- Current is always positive magnitude (direction inferred from power sign)
- Both FC03 and FC04 are supported
- FC06/FC16 writes are accepted as no-ops (required for Cerbo init sequence)
- Any register not listed above returns 0x0000

## Usage

### Three-phase configuration

Add to your ESPHome YAML (e.g. `p1.yaml`):

```yaml
external_components:
  - source:
      type: git
      url: https://github.com/jblankendaal/victron-grid-meter-esphome
      ref: three-phase
    refresh: 1h
    components:
      - grid_meter

sensor:
  - platform: dsmr
    energy_delivered_tariff1:
      name: "Energy Consumed Tariff 1"
      state_class: total_increasing
      id: energy_delivered_tariff1
    energy_delivered_tariff2:
      name: "Energy Consumed Tariff 2"
      state_class: total_increasing
      id: energy_delivered_tariff2
    energy_returned_tariff1:
      name: "Energy Produced Tariff 1"
      state_class: total_increasing
      id: energy_returned_tariff1
    energy_returned_tariff2:
      name: "Energy Produced Tariff 2"
      state_class: total_increasing
      id: energy_returned_tariff2
    power_delivered_l1:
      name: "Power Consumed L1"
      id: power_delivered_l1
      unit_of_measurement: "W"
      state_class: "measurement"
      accuracy_decimals: 0
      filters:
        - multiply: 1000
    power_delivered_l2:
      name: "Power Consumed L2"
      id: power_delivered_l2
      unit_of_measurement: "W"
      state_class: "measurement"
      accuracy_decimals: 0
      filters:
        - multiply: 1000
    power_delivered_l3:
      name: "Power Consumed L3"
      id: power_delivered_l3
      unit_of_measurement: "W"
      state_class: "measurement"
      accuracy_decimals: 0
      filters:
        - multiply: 1000
    power_returned_l1:
      name: "Power Produced L1"
      id: power_returned_l1
      unit_of_measurement: "W"
      state_class: "measurement"
      accuracy_decimals: 0
      filters:
        - multiply: 1000
    power_returned_l2:
      name: "Power Produced L2"
      id: power_returned_l2
      unit_of_measurement: "W"
      state_class: "measurement"
      accuracy_decimals: 0
      filters:
        - multiply: 1000
    power_returned_l3:
      name: "Power Produced L3"
      id: power_returned_l3
      unit_of_measurement: "W"
      state_class: "measurement"
      accuracy_decimals: 0
      filters:
        - multiply: 1000
    voltage_l1:
      name: "Voltage Phase 1"
      id: voltage_l1
    voltage_l2:
      name: "Voltage Phase 2"
      id: voltage_l2
    voltage_l3:
      name: "Voltage Phase 3"
      id: voltage_l3
    current_l1:
      name: "Current Phase 1"
      id: current_l1
    current_l2:
      name: "Current Phase 2"
      id: current_l2
    current_l3:
      name: "Current Phase 3"
      id: current_l3

grid_meter:
  power_import_l1: power_delivered_l1
  power_import_l2: power_delivered_l2
  power_import_l3: power_delivered_l3
  power_export_l1: power_returned_l1
  power_export_l2: power_returned_l2
  power_export_l3: power_returned_l3
  voltage_l1: voltage_l1
  voltage_l2: voltage_l2
  voltage_l3: voltage_l3
  current_l1: current_l1
  current_l2: current_l2
  current_l3: current_l3
  energy_import_t1: energy_delivered_tariff1
  energy_import_t2: energy_delivered_tariff2
  energy_export_t1: energy_returned_tariff1
  energy_export_t2: energy_returned_tariff2
```

### Single-phase configuration (backwards compatible)

All twelve three-phase sensor keys are replaced with eight single-phase keys:

```yaml
grid_meter:
  power_import: power_delivered
  power_export: power_returned
  voltage: voltage_l1
  current: current_l1
  energy_import_t1: energy_delivered_tariff1
  energy_import_t2: energy_delivered_tariff2
  energy_export_t1: energy_returned_tariff1
  energy_export_t2: energy_returned_tariff2
```

The component auto-detects which mode to use based on which sensor keys are present.

## Victron Cerbo GX setup

1. Go to **Settings → Energy Meters → Add**
2. Select **Carlo Gavazzi EM24**
3. Enter the ESP32's IP address, port **502**
4. Save — the Cerbo will start polling immediately

## Requirements

- ESP-IDF framework (not Arduino)
- DSMR P1 component providing the sensor data
- `id:` fields on all sensor references used in the `grid_meter:` block

## Running tests

Integration tests require the device to be flashed and reachable on the network.

```bash
pip install -r requirements.txt
pytest tests/test_grid_meter.py --device-ip=<ESP32_IP> -v
```

Schema tests (no hardware required):

```bash
pytest tests/test_schema.py -v
```
