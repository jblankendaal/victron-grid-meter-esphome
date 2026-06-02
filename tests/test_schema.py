"""
Schema validation tests — run without hardware, requires esphome installed.
Run: pytest tests/test_schema.py -v
"""
import pytest
import sys
import os

# Make the component importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def _load_schema():
    """Load CONFIG_SCHEMA from the component __init__.py."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "grid_meter",
        os.path.join(os.path.dirname(__file__), '..', 'components', 'grid_meter', '__init__.py')
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.CONFIG_SCHEMA


def test_single_phase_sensor_keys_are_required_when_single_phase_configured():
    """A single-phase config must include all single-phase sensor keys."""
    import esphome.config_validation as cv
    schema = _load_schema()
    config = {
        "power_import": "power_delivered",
        "power_export": "power_returned",
        "voltage": "voltage_l1",
        "current": "current_l1",
        "energy_import_t1": "energy_delivered_tariff1",
        "energy_import_t2": "energy_delivered_tariff2",
        "energy_export_t1": "energy_returned_tariff1",
        "energy_export_t2": "energy_returned_tariff2",
    }
    for key in ["power_import", "power_export", "voltage", "current"]:
        partial = {k: v for k, v in config.items() if k != key}
        with pytest.raises(cv.Invalid, match=key):
            schema(partial)


def test_common_energy_sensor_keys_are_required():
    """Common energy sensor keys are always required."""
    import esphome.config_validation as cv
    schema = _load_schema()
    config = {
        "power_import", "power_export", "voltage", "current",
        "energy_import_t1", "energy_import_t2",
        "energy_export_t1", "energy_export_t2",
    }
    config = {key: "some_sensor_id" for key in config}
    for key in [
        "energy_import_t1",
        "energy_import_t2",
        "energy_export_t1",
        "energy_export_t2",
    ]:
        partial = {k: v for k, v in config.items() if k != key}
        with pytest.raises(cv.Invalid, match=key):
            schema(partial)


def test_valid_single_phase_config_accepted():
    """CONFIG_SCHEMA must accept a complete single-phase config."""
    schema = _load_schema()
    config = {
        "power_import":    "power_delivered",
        "power_export":    "power_returned",
        "voltage":         "voltage_l1",
        "current":         "current_l1",
        "energy_import_t1": "energy_delivered_tariff1",
        "energy_import_t2": "energy_delivered_tariff2",
        "energy_export_t1": "energy_returned_tariff1",
        "energy_export_t2": "energy_returned_tariff2",
    }
    result = schema(config)
    assert result is not None


def test_valid_three_phase_config_accepted():
    """CONFIG_SCHEMA must accept a complete three-phase config."""
    schema = _load_schema()
    config = {
        "power_import_l1": "power_delivered_l1",
        "power_import_l2": "power_delivered_l2",
        "power_import_l3": "power_delivered_l3",
        "power_export_l1": "power_returned_l1",
        "power_export_l2": "power_returned_l2",
        "power_export_l3": "power_returned_l3",
        "voltage_l1": "voltage_l1",
        "voltage_l2": "voltage_l2",
        "voltage_l3": "voltage_l3",
        "current_l1": "current_l1",
        "current_l2": "current_l2",
        "current_l3": "current_l3",
        "energy_import_t1": "energy_delivered_tariff1",
        "energy_import_t2": "energy_delivered_tariff2",
        "energy_export_t1": "energy_returned_tariff1",
        "energy_export_t2": "energy_returned_tariff2",
    }
    result = schema(config)
    assert result is not None


def test_incomplete_three_phase_config_rejected():
    """A partial three-phase config must name the missing keys."""
    import esphome.config_validation as cv
    schema = _load_schema()
    config = {
        "power_import_l1": "power_delivered_l1",
        "power_import_l2": "power_delivered_l2",
        "power_export_l1": "power_returned_l1",
        "power_export_l2": "power_returned_l2",
        "power_export_l3": "power_returned_l3",
        "voltage_l1": "voltage_l1",
        "voltage_l2": "voltage_l2",
        "voltage_l3": "voltage_l3",
        "current_l1": "current_l1",
        "current_l2": "current_l2",
        "current_l3": "current_l3",
        "energy_import_t1": "energy_delivered_tariff1",
        "energy_import_t2": "energy_delivered_tariff2",
        "energy_export_t1": "energy_returned_tariff1",
        "energy_export_t2": "energy_returned_tariff2",
    }
    with pytest.raises(cv.Invalid, match="power_import_l3"):
        schema(config)


def test_mixed_single_and_three_phase_config_rejected():
    """Single-phase and three-phase keys cannot be mixed."""
    import esphome.config_validation as cv
    schema = _load_schema()
    config = {
        "power_import": "power_delivered",
        "power_export": "power_returned",
        "voltage": "voltage_l1",
        "current": "current_l1",
        "power_import_l1": "power_delivered_l1",
        "energy_import_t1": "energy_delivered_tariff1",
        "energy_import_t2": "energy_delivered_tariff2",
        "energy_export_t1": "energy_returned_tariff1",
        "energy_export_t2": "energy_returned_tariff2",
    }
    with pytest.raises(cv.Invalid, match="Cannot configure both"):
        schema(config)
