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

# Single-phase schema
SINGLE_PHASE_SCHEMA = cv.Schema(
    {
        cv.Required(CONF_POWER_IMPORT): cv.use_id(sensor.Sensor),
        cv.Required(CONF_POWER_EXPORT): cv.use_id(sensor.Sensor),
        cv.Required(CONF_VOLTAGE): cv.use_id(sensor.Sensor),
        cv.Required(CONF_CURRENT): cv.use_id(sensor.Sensor),
    }
)

# Three-phase schema
THREE_PHASE_SCHEMA = cv.Schema(
    {
        cv.Required(CONF_POWER_IMPORT_L1): cv.use_id(sensor.Sensor),
        cv.Required(CONF_POWER_IMPORT_L2): cv.use_id(sensor.Sensor),
        cv.Required(CONF_POWER_IMPORT_L3): cv.use_id(sensor.Sensor),
        cv.Required(CONF_POWER_EXPORT_L1): cv.use_id(sensor.Sensor),
        cv.Required(CONF_POWER_EXPORT_L2): cv.use_id(sensor.Sensor),
        cv.Required(CONF_POWER_EXPORT_L3): cv.use_id(sensor.Sensor),
        cv.Required(CONF_VOLTAGE_L1): cv.use_id(sensor.Sensor),
        cv.Required(CONF_VOLTAGE_L2): cv.use_id(sensor.Sensor),
        cv.Required(CONF_VOLTAGE_L3): cv.use_id(sensor.Sensor),
        cv.Required(CONF_CURRENT_L1): cv.use_id(sensor.Sensor),
        cv.Required(CONF_CURRENT_L2): cv.use_id(sensor.Sensor),
        cv.Required(CONF_CURRENT_L3): cv.use_id(sensor.Sensor),
    }
)


def validate_config(config):
    """Validate that either single-phase or three-phase is configured, not both or neither."""
    has_single_phase = CONF_POWER_IMPORT in config
    has_three_phase = CONF_POWER_IMPORT_L1 in config
    
    if has_single_phase and has_three_phase:
        raise cv.Invalid(
            "Cannot configure both single-phase and three-phase sensors. "
            "Use either (power_import/power_export/voltage/current) "
            "or (power_import_l1/l2/l3, power_export_l1/l2/l3, voltage_l1/l2/l3, current_l1/l2/l3)"
        )
    
    if not has_single_phase and not has_three_phase:
        raise cv.Invalid(
            "Must configure either single-phase or three-phase sensors. "
            "Use either (power_import/power_export/voltage/current) "
            "or (power_import_l1/l2/l3, power_export_l1/l2/l3, voltage_l1/l2/l3, current_l1/l2/l3)"
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

    await cg.register_component(var, config)
