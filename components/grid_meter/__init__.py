import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import sensor
from esphome.const import CONF_ID

AUTO_LOAD = ["sensor"]
CODEOWNERS = []

grid_meter_ns = cg.esphome_ns.namespace("grid_meter")
GridMeterComponent = grid_meter_ns.class_("GridMeterComponent", cg.Component)

# Single-phase config keys
CONF_POWER_IMPORT = "power_import"
CONF_POWER_EXPORT = "power_export"
CONF_VOLTAGE = "voltage"
CONF_CURRENT = "current"

# Three-phase config keys
CONF_POWER_IMPORT_L1 = "power_import_l1"
CONF_POWER_IMPORT_L2 = "power_import_l2"
CONF_POWER_IMPORT_L3 = "power_import_l3"
CONF_POWER_EXPORT_L1 = "power_export_l1"
CONF_POWER_EXPORT_L2 = "power_export_l2"
CONF_POWER_EXPORT_L3 = "power_export_l3"
CONF_VOLTAGE_L1 = "voltage_l1"
CONF_VOLTAGE_L2 = "voltage_l2"
CONF_VOLTAGE_L3 = "voltage_l3"
CONF_CURRENT_L1 = "current_l1"
CONF_CURRENT_L2 = "current_l2"
CONF_CURRENT_L3 = "current_l3"

# Common config keys
CONF_ENERGY_IMP_T1 = "energy_import_t1"
CONF_ENERGY_IMP_T2 = "energy_import_t2"
CONF_ENERGY_EXP_T1 = "energy_export_t1"
CONF_ENERGY_EXP_T2 = "energy_export_t2"
CONF_PHASE_SEQUENCE = "phase_sequence"

PHASE_SEQUENCES = {
    "l1_l2_l3": 0,
    "l1_l3_l2": -1,
}

SINGLE_PHASE_KEYS = (
    CONF_POWER_IMPORT,
    CONF_POWER_EXPORT,
    CONF_VOLTAGE,
    CONF_CURRENT,
)

THREE_PHASE_KEYS = (
    CONF_POWER_IMPORT_L1,
    CONF_POWER_IMPORT_L2,
    CONF_POWER_IMPORT_L3,
    CONF_POWER_EXPORT_L1,
    CONF_POWER_EXPORT_L2,
    CONF_POWER_EXPORT_L3,
    CONF_VOLTAGE_L1,
    CONF_VOLTAGE_L2,
    CONF_VOLTAGE_L3,
    CONF_CURRENT_L1,
    CONF_CURRENT_L2,
    CONF_CURRENT_L3,
)

# Single-phase schema
SINGLE_PHASE_SCHEMA = cv.Schema(
    {
        cv.Optional(CONF_POWER_IMPORT): cv.use_id(sensor.Sensor),
        cv.Optional(CONF_POWER_EXPORT): cv.use_id(sensor.Sensor),
        cv.Optional(CONF_VOLTAGE): cv.use_id(sensor.Sensor),
        cv.Optional(CONF_CURRENT): cv.use_id(sensor.Sensor),
    }
)

# Three-phase schema
THREE_PHASE_SCHEMA = cv.Schema(
    {
        cv.Optional(CONF_POWER_IMPORT_L1): cv.use_id(sensor.Sensor),
        cv.Optional(CONF_POWER_IMPORT_L2): cv.use_id(sensor.Sensor),
        cv.Optional(CONF_POWER_IMPORT_L3): cv.use_id(sensor.Sensor),
        cv.Optional(CONF_POWER_EXPORT_L1): cv.use_id(sensor.Sensor),
        cv.Optional(CONF_POWER_EXPORT_L2): cv.use_id(sensor.Sensor),
        cv.Optional(CONF_POWER_EXPORT_L3): cv.use_id(sensor.Sensor),
        cv.Optional(CONF_VOLTAGE_L1): cv.use_id(sensor.Sensor),
        cv.Optional(CONF_VOLTAGE_L2): cv.use_id(sensor.Sensor),
        cv.Optional(CONF_VOLTAGE_L3): cv.use_id(sensor.Sensor),
        cv.Optional(CONF_CURRENT_L1): cv.use_id(sensor.Sensor),
        cv.Optional(CONF_CURRENT_L2): cv.use_id(sensor.Sensor),
        cv.Optional(CONF_CURRENT_L3): cv.use_id(sensor.Sensor),
    }
)


def validate_config(config):
    """Validate that either a complete single-phase or three-phase config is present."""
    single_phase_keys = [key for key in SINGLE_PHASE_KEYS if key in config]
    three_phase_keys = [key for key in THREE_PHASE_KEYS if key in config]
    
    if single_phase_keys and three_phase_keys:
        raise cv.Invalid(
            "Cannot configure both single-phase and three-phase sensors. "
            "Use either (power_import/power_export/voltage/current) "
            "or (power_import_l1/l2/l3, power_export_l1/l2/l3, voltage_l1/l2/l3, current_l1/l2/l3)"
        )
    
    if not single_phase_keys and not three_phase_keys:
        raise cv.Invalid(
            "Must configure either single-phase or three-phase sensors. "
            "Use either (power_import/power_export/voltage/current) "
            "or (power_import_l1/l2/l3, power_export_l1/l2/l3, voltage_l1/l2/l3, current_l1/l2/l3)"
        )

    if single_phase_keys:
        if config[CONF_PHASE_SEQUENCE] != PHASE_SEQUENCES["l1_l2_l3"]:
            raise cv.Invalid("phase_sequence can only be set for three-phase configurations")

        missing = [key for key in SINGLE_PHASE_KEYS if key not in config]
        if missing:
            raise cv.Invalid(
                "Single-phase configuration is incomplete. Missing: "
                + ", ".join(missing)
            )

    if three_phase_keys:
        missing = [key for key in THREE_PHASE_KEYS if key not in config]
        if missing:
            raise cv.Invalid(
                "Three-phase configuration is incomplete. Missing: "
                + ", ".join(missing)
            )
    
    return config


CONFIG_SCHEMA = cv.All(
    cv.Schema(
        {
            cv.GenerateID(): cv.declare_id(GridMeterComponent),
            cv.Required(CONF_ENERGY_IMP_T1): cv.use_id(sensor.Sensor),
            cv.Required(CONF_ENERGY_IMP_T2): cv.use_id(sensor.Sensor),
            cv.Required(CONF_ENERGY_EXP_T1): cv.use_id(sensor.Sensor),
            cv.Required(CONF_ENERGY_EXP_T2): cv.use_id(sensor.Sensor),
            cv.Optional(CONF_PHASE_SEQUENCE, default="l1_l2_l3"): cv.enum(
                PHASE_SEQUENCES, lower=True
            ),
        }
    )
    .extend(SINGLE_PHASE_SCHEMA)
    .extend(THREE_PHASE_SCHEMA)
    .extend(cv.COMPONENT_SCHEMA),
    cv.only_on_esp32,
    validate_config,
)


async def to_code(config):
    energy_import_t1 = await cg.get_variable(config[CONF_ENERGY_IMP_T1])
    energy_import_t2 = await cg.get_variable(config[CONF_ENERGY_IMP_T2])
    energy_export_t1 = await cg.get_variable(config[CONF_ENERGY_EXP_T1])
    energy_export_t2 = await cg.get_variable(config[CONF_ENERGY_EXP_T2])

    # Check if three-phase sensors are configured
    if CONF_POWER_IMPORT_L1 in config:
        # Three-phase configuration
        power_import_l1 = await cg.get_variable(config[CONF_POWER_IMPORT_L1])
        power_import_l2 = await cg.get_variable(config[CONF_POWER_IMPORT_L2])
        power_import_l3 = await cg.get_variable(config[CONF_POWER_IMPORT_L3])
        power_export_l1 = await cg.get_variable(config[CONF_POWER_EXPORT_L1])
        power_export_l2 = await cg.get_variable(config[CONF_POWER_EXPORT_L2])
        power_export_l3 = await cg.get_variable(config[CONF_POWER_EXPORT_L3])
        voltage_l1 = await cg.get_variable(config[CONF_VOLTAGE_L1])
        voltage_l2 = await cg.get_variable(config[CONF_VOLTAGE_L2])
        voltage_l3 = await cg.get_variable(config[CONF_VOLTAGE_L3])
        current_l1 = await cg.get_variable(config[CONF_CURRENT_L1])
        current_l2 = await cg.get_variable(config[CONF_CURRENT_L2])
        current_l3 = await cg.get_variable(config[CONF_CURRENT_L3])

        var = cg.new_Pvariable(
            config[CONF_ID],
            power_import_l1,
            power_import_l2,
            power_import_l3,
            power_export_l1,
            power_export_l2,
            power_export_l3,
            voltage_l1,
            voltage_l2,
            voltage_l3,
            current_l1,
            current_l2,
            current_l3,
            energy_import_t1,
            energy_import_t2,
            energy_export_t1,
            energy_export_t2,
        )
    else:
        # Single-phase configuration
        power_import = await cg.get_variable(config[CONF_POWER_IMPORT])
        power_export = await cg.get_variable(config[CONF_POWER_EXPORT])
        voltage = await cg.get_variable(config[CONF_VOLTAGE])
        current = await cg.get_variable(config[CONF_CURRENT])

        var = cg.new_Pvariable(
            config[CONF_ID],
            power_import,
            power_export,
            voltage,
            current,
            energy_import_t1,
            energy_import_t2,
            energy_export_t1,
            energy_export_t2,
        )

    cg.add(var.set_phase_sequence(config[CONF_PHASE_SEQUENCE]))
    await cg.register_component(var, config)
