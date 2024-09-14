"""Contains the functions to create sensors."""

from __future__ import annotations

import solarwatt_energymanager as em
import logging

import solarwatt_energymanager as em

from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
)

from .const import DOMAIN
from .energy_manager_sensors import (
    EnergyManagerCurrentSensor,
    EnergyManagerDataSensor,
    EnergyManagerPowerSensor,
    EnergyManagerNetPowerSensor,
    EnergyManagerStateOfHealthSensor,
    EnergyManagerStateOfChargeSensor,
    EnergyManagerTemperatureSensor,
    EnergyManagerVoltageSensor,
    EnergyManagerWorkSensor,
)

_LOGGER = logging.getLogger(__name__)


def convertToKwh(wh: float) -> float:
    return round(wh / 1000, 3)


def get_battery_device(em: em.EnergyManagerData, guid: str) -> em.BatteryConverterDevice:
    """Get the battery device with the specified guid."""
    devices = list(filter(lambda d: d.device.guid == guid, em.battery_converter_devices))
    return devices[0] if devices else None


def get_ev_station_device(em: em.EnergyManagerData, guid: str) -> em.EVStationDevice:
    """Get the EV station device with the specified guid."""
    devices = list(filter(lambda d: d.device.guid == guid, em.ev_station_devices))
    return devices[0] if devices else None


def get_s0_counter_device(em: em.EnergyManagerData, guid: str) -> em.S0CounterDevice:
    """Get the S0 counter device with the specified guid."""
    devices = list(filter(lambda d: d.device.guid == guid, em.s0_counter_devices))
    return devices[0] if devices else None


def get_power_meter_device(em: em.EnergyManagerData, guid: str) -> em.PowerMeterDevice:
    """Get the Power Meter device with the specified guid."""
    devices = list(filter(lambda d: d.device.guid == guid, em.power_meter_devices))
    return devices[0] if devices else None


def get_device_info(data: em.EnergyManagerData) -> DeviceInfo:
    """Get the device info for the EnergyManager."""
    energy_manager = data.energy_manager_device
    guid = energy_manager.device.guid if energy_manager else ""
    model = energy_manager.model if energy_manager else ""
    firmware = energy_manager.firmware if energy_manager else ""
    return DeviceInfo(
        name=guid,
        manufacturer="SOLARWATT",
        identifiers={(DOMAIN, guid)},
        model=model,
        sw_version=firmware,
    )


def create_sensors(
    coordinator: DataUpdateCoordinator, data: em.EnergyManagerData
) -> list[EnergyManagerDataSensor]:
    """Create the sensors for the the available devices."""
    device_info = get_device_info(data)
    location_device = data.location_device
    entities = []
    if location_device:
        _LOGGER.info("Creating sensor entities for the location device")
        entities.extend(
            create_location_sensors(coordinator, device_info, location_device)
        )
    batteries = data.battery_converter_devices
    batteryCount = len(batteries)
    if batteryCount > 0:
        _LOGGER.info(f"Found {batteryCount} batteries")
        for battery in batteries:
            _LOGGER.info(f"Creating sensor entities for the battery {battery.device.guid}")
            entities.extend(
                create_battery_converter_sensors(
                    coordinator, device_info, battery
                )
            )
    evStations = data.ev_station_devices
    evStationCount = len(evStations)
    if evStationCount > 0:
        _LOGGER.info(f"Found {evStationCount} EV stations")
        for evStation in evStations:
            _LOGGER.info(f"Creating sensor entities for EV station {evStation.device.guid}")
            entities.extend(
                create_ev_station_sensors(
                    coordinator, device_info, evStation
                )
            )
    s0Counters = data.s0_counter_devices
    s0CounterCount = len(s0Counters)
    if s0CounterCount > 0:
        _LOGGER.info(f"Found {s0CounterCount} S0 counters")
        for s0Counter in s0Counters:
            _LOGGER.info(f"Creating sensor entities for S0 counter {s0Counter.device.guid}")
            entities.extend(
                create_s0_counter_sensors(
                    coordinator, device_info, s0Counter
                )
            )
    powerMeters = data.power_meter_devices
    powerMeterCount = len(powerMeters)
    if powerMeterCount > 0:
        _LOGGER.info(f"Found {powerMeterCount} Power Meters")
        for powerMeter in powerMeters:
            _LOGGER.info(f"Creating sensor entities for Power Meter {powerMeter.device.guid}")
            entities.extend(
                create_power_meter_sensors(
                    coordinator, device_info, powerMeter
                )
            )
        
    return entities


def create_location_sensors(
    coordinator: DataUpdateCoordinator,
    device_info: DeviceInfo,
    location_device: em.LocationDevice,
) -> list[EnergyManagerDataSensor]:
    """Create the sensors for the location device."""
    guid = location_device.device.guid
    device_name = location_device.device.get_device_name()
    return [
        EnergyManagerPowerSensor(
            coordinator,
            em.LocationDevice.TAG_POWER_BUFFERED,
            device_info,
            guid,
            device_name,
            lambda d: d.location_device.power_buffered,
        ),
        EnergyManagerPowerSensor(
            coordinator,
            em.LocationDevice.TAG_POWER_BUFFERED_FROM_GRID,
            device_info,
            guid,
            device_name,
            lambda d: d.location_device.power_buffered_from_grid,
        ),
        EnergyManagerPowerSensor(
            coordinator,
            em.LocationDevice.TAG_POWER_BUFFERED_FROM_PRODUCERS,
            device_info,
            guid,
            device_name,
            lambda d: d.location_device.power_buffered_from_producers,
        ),
        EnergyManagerPowerSensor(
            coordinator,
            em.LocationDevice.TAG_POWER_CONSUMED,
            device_info,
            guid,
            device_name,
            lambda d: d.location_device.power_consumed,
        ),
        EnergyManagerPowerSensor(
            coordinator,
            em.LocationDevice.TAG_POWER_CONSUMED_FROM_GRID,
            device_info,
            guid,
            device_name,
            lambda d: d.location_device.power_consumed_from_grid,
        ),
        EnergyManagerPowerSensor(
            coordinator,
            em.LocationDevice.TAG_POWER_CONSUMED_FROM_PRODUCERS,
            device_info,
            guid,
            device_name,
            lambda d: d.location_device.power_consumed_from_producers,
        ),
        EnergyManagerPowerSensor(
            coordinator,
            em.LocationDevice.TAG_POWER_CONSUMED_FROM_STORAGE,
            device_info,
            guid,
            device_name,
            lambda d: d.location_device.power_consumed_from_storage,
        ),
        EnergyManagerPowerSensor(
            coordinator,
            em.LocationDevice.TAG_POWER_IN,
            device_info,
            guid,
            device_name,
            lambda d: d.location_device.power_in,
        ),
        EnergyManagerPowerSensor(
            coordinator,
            em.LocationDevice.TAG_POWER_OUT,
            device_info,
            guid,
            device_name,
            lambda d: d.location_device.power_out,
        ),
        EnergyManagerPowerSensor(
            coordinator,
            em.LocationDevice.TAG_POWER_OUT_FROM_PRODUCERS,
            device_info,
            guid,
            device_name,
            lambda d: d.location_device.power_out_from_producers,
        ),
        EnergyManagerPowerSensor(
            coordinator,
            em.LocationDevice.TAG_POWER_OUT_FROM_STORAGE,
            device_info,
            guid,
            device_name,
            lambda d: d.location_device.power_out_from_storage,
        ),
        EnergyManagerPowerSensor(
            coordinator,
            em.LocationDevice.TAG_POWER_PRODUCED,
            device_info,
            guid,
            device_name,
            lambda d: d.location_device.power_produced,
        ),
        EnergyManagerPowerSensor(
            coordinator,
            em.LocationDevice.TAG_POWER_RELEASED,
            device_info,
            guid,
            device_name,
            lambda d: d.location_device.power_released,
        ),
        EnergyManagerPowerSensor(
            coordinator,
            em.LocationDevice.TAG_POWER_SELF_CONSUMED,
            device_info,
            guid,
            device_name,
            lambda d: d.location_device.power_self_consumed,
        ),
        EnergyManagerPowerSensor(
            coordinator,
            em.LocationDevice.TAG_POWER_SELF_SUPPLIED,
            device_info,
            guid,
            device_name,
            lambda d: d.location_device.power_self_supplied,
        ),
        EnergyManagerNetPowerSensor(
            coordinator,
            "PowerNet",
            device_info,
            guid,
            device_name,
            lambda d: d.location_device.power_in,
            lambda d: d.location_device.power_out,
        ),
        EnergyManagerNetPowerSensor(
            coordinator,
            "PowerNetBuffered",
            device_info,
            guid,
            device_name,
            lambda d: d.location_device.power_buffered,
            lambda d: d.location_device.power_released,
        ),
        EnergyManagerWorkSensor(
            coordinator,
            em.LocationDevice.TAG_WORK_BUFFERED,
            device_info,
            guid,
            device_name,
            lambda d: convertToKwh(d.location_device.work_buffered),
        ),
        EnergyManagerWorkSensor(
            coordinator,
            em.LocationDevice.TAG_WORK_BUFFERED_FROM_GRID,
            device_info,
            guid,
            device_name,
            lambda d: convertToKwh(d.location_device.work_buffered_from_grid),
        ),
        EnergyManagerWorkSensor(
            coordinator,
            em.LocationDevice.TAG_WORK_BUFFERED_FROM_PRODUCERS,
            device_info,
            guid,
            device_name,
            lambda d: convertToKwh(d.location_device.work_buffered_from_producers),
        ),
        EnergyManagerWorkSensor(
            coordinator,
            em.LocationDevice.TAG_WORK_CONSUMED,
            device_info,
            guid,
            device_name,
            lambda d: convertToKwh(d.location_device.work_consumed),
        ),
        EnergyManagerWorkSensor(
            coordinator,
            em.LocationDevice.TAG_WORK_CONSUMED_FROM_GRID,
            device_info,
            guid,
            device_name,
            lambda d: convertToKwh(d.location_device.work_consumed_from_grid),
        ),
        EnergyManagerWorkSensor(
            coordinator,
            em.LocationDevice.TAG_WORK_CONSUMED_FROM_PRODUCERS,
            device_info,
            guid,
            device_name,
            lambda d: convertToKwh(d.location_device.work_consumed_from_producers),
        ),
        EnergyManagerWorkSensor(
            coordinator,
            em.LocationDevice.TAG_WORK_CONSUMED_FROM_STORAGE,
            device_info,
            guid,
            device_name,
            lambda d: convertToKwh(d.location_device.work_consumed_from_storage),
        ),
        EnergyManagerWorkSensor(
            coordinator,
            em.LocationDevice.TAG_WORK_IN,
            device_info,
            guid,
            device_name,
            lambda d: convertToKwh(d.location_device.work_in),
        ),
        EnergyManagerWorkSensor(
            coordinator,
            em.LocationDevice.TAG_WORK_OUT,
            device_info,
            guid,
            device_name,
            lambda d: convertToKwh(d.location_device.work_out),
        ),
        EnergyManagerWorkSensor(
            coordinator,
            em.LocationDevice.TAG_WORK_PRODUCED,
            device_info,
            guid,
            device_name,
            lambda d: convertToKwh(d.location_device.work_produced),
        ),
        EnergyManagerWorkSensor(
            coordinator,
            em.LocationDevice.TAG_WORK_RELEASED,
            device_info,
            guid,
            device_name,
            lambda d: convertToKwh(d.location_device.work_released),
        ),
        EnergyManagerWorkSensor(
            coordinator,
            em.LocationDevice.TAG_WORK_SELF_CONSUMED,
            device_info,
            guid,
            device_name,
            lambda d: convertToKwh(d.location_device.work_self_consumed),
        ),
        EnergyManagerWorkSensor(
            coordinator,
            em.LocationDevice.TAG_WORK_SELF_SUPPLIED,
            device_info,
            guid,
            device_name,
            lambda d: convertToKwh(d.location_device.work_self_supplied),
        ),
    ]


def create_battery_converter_sensors(
    coordinator: DataUpdateCoordinator,
    device_info: DeviceInfo,
    battery_converter_device: em.BatteryConverterDevice,
) -> list[EnergyManagerDataSensor]:
    """Create the sensors for the battery converter."""
    guid = battery_converter_device.device.guid
    device_name = battery_converter_device.device.get_device_name()
    return [
        EnergyManagerStateOfChargeSensor(
            coordinator,
            em.BatteryConverterDevice.TAG_STATE_OF_CHARGE,
            device_info,
            guid,
            device_name,
            lambda d: get_battery_device(d, guid).state_of_charge,
        ),
        EnergyManagerStateOfHealthSensor(
            coordinator,
            em.BatteryConverterDevice.TAG_STATE_OF_HEALTH,
            device_info,
            guid,
            device_name,
            lambda d: get_battery_device(d, guid).state_of_health,
        ),
        EnergyManagerTemperatureSensor(
            coordinator,
            em.BatteryConverterDevice.TAG_TEMPERATURE_BATTERY,
            device_info,
            guid,
            device_name,
            lambda d: get_battery_device(d, guid).temperature_battery,
        ),
        EnergyManagerCurrentSensor(
            coordinator,
            em.BatteryConverterDevice.TAG_CURRENT_BATTERY_IN,
            device_info,
            guid,
            device_name,
            lambda d: get_battery_device(d, guid).current_battery_in,
        ),
        EnergyManagerCurrentSensor(
            coordinator,
            em.BatteryConverterDevice.TAG_CURRENT_BATTERY_OUT,
            device_info,
            guid,
            device_name,
            lambda d: get_battery_device(d, guid).current_battery_out,
        ),
        EnergyManagerCurrentSensor(
            coordinator,
            em.BatteryConverterDevice.TAG_CURRENT_GRM_IN,
            device_info,
            guid,
            device_name,
            lambda d: get_battery_device(d, guid).TAG_CURRENT_GRM_IN,
        ),
        EnergyManagerCurrentSensor(
            coordinator,
            em.BatteryConverterDevice.TAG_CURRENT_GRM_OUT,
            device_info,
            guid,
            device_name,
            lambda d: get_battery_device(d, guid).TAG_CURRENT_GRM_OUT,
        ),
        EnergyManagerCurrentSensor(
            coordinator,
            em.BatteryConverterDevice.TAG_CURRENT_STRING_DC_IN,
            device_info,
            guid,
            device_name,
            lambda d: get_battery_device(d, guid).TAG_CURRENT_STRING_DC_IN,
        ),
        EnergyManagerPowerSensor(
            coordinator,
            em.BatteryConverterDevice.TAG_POWER_AC_IN,
            device_info,
            guid,
            device_name,
            lambda d: get_battery_device(d, guid).power_ac_in,
        ),
        EnergyManagerPowerSensor(
            coordinator,
            em.BatteryConverterDevice.TAG_POWER_AC_OUT,
            device_info,
            guid,
            device_name,
            lambda d: get_battery_device(d, guid).power_ac_out,
        ),
        EnergyManagerVoltageSensor(
            coordinator,
            em.BatteryConverterDevice.TAG_VOLTAGE_GRM_IN,
            device_info,
            guid,
            device_name,
            lambda d: get_battery_device(d, guid).voltage_grm_in,
        ),
        EnergyManagerVoltageSensor(
            coordinator,
            em.BatteryConverterDevice.TAG_VOLTAGE_GRM_OUT,
            device_info,
            guid,
            device_name,
            lambda d: get_battery_device(d, guid).voltage_grm_out,
        ),
        EnergyManagerVoltageSensor(
            coordinator,
            em.BatteryConverterDevice.TAG_VOLTAGE_BATTERY_CELL_MEAN,
            device_info,
            guid,
            device_name,
            lambda d: get_battery_device(d, guid).voltage_battery_cell_mean,
        ),
        EnergyManagerVoltageSensor(
            coordinator,
            em.BatteryConverterDevice.TAG_VOLTAGE_BATTERY_STRING,
            device_info,
            guid,
            device_name,
            lambda d: get_battery_device(d, guid).voltage_battery_string,
        ),
        EnergyManagerWorkSensor(
            coordinator,
            em.BatteryConverterDevice.TAG_WORK_AC_IN,
            device_info,
            guid,
            device_name,
            lambda d: convertToKwh(get_battery_device(d, guid).work_ac_in),
        ),
        EnergyManagerWorkSensor(
            coordinator,
            em.BatteryConverterDevice.TAG_WORK_AC_OUT,
            device_info,
            guid,
            device_name,
            lambda d: convertToKwh(get_battery_device(d, guid).work_ac_out),
        ),        
    ]


def create_ev_station_sensors(
    coordinator: DataUpdateCoordinator,
    device_info: DeviceInfo,
    ev_station_device: em.EVStationDevice,
) -> list[EnergyManagerDataSensor]:
    """Create the sensors for the EV station."""
    guid = ev_station_device.device.guid
    device_name = ev_station_device.device.get_device_name()
    return [
        EnergyManagerStateOfChargeSensor(
            coordinator,
            em.EVStationDevice.TAG_STATE_OF_CHARGE,
            device_info,
            guid,
            device_name,
            lambda d: get_ev_station_device(d, guid).state_of_charge,
        ),
        EnergyManagerTemperatureSensor(
            coordinator,
            em.EVStationDevice.TAG_TEMPERATURE_BATTERY,
            device_info,
            guid,
            device_name,
            lambda d: get_ev_station_device(d, guid).temperature_battery,
        ),
        EnergyManagerPowerSensor(
            coordinator,
            em.EVStationDevice.TAG_POWER_AC_IN,
            device_info,
            guid,
            device_name,
            lambda d: get_ev_station_device(d, guid).power_ac_in,
        ),
        EnergyManagerPowerSensor(
            coordinator,
            em.EVStationDevice.TAG_POWER_AC_OUT,
            device_info,
            guid,
            device_name,
            lambda d: get_ev_station_device(d, guid).power_ac_out,
        ),
        EnergyManagerNetPowerSensor(
            coordinator,
            "PowerACNet",
            device_info,
            guid,
            device_name,
            lambda d: get_ev_station_device(d, guid).power_ac_in,
            lambda d: get_ev_station_device(d, guid).power_ac_out,
        ),
        EnergyManagerWorkSensor(
            coordinator,
            em.EVStationDevice.TAG_WORK_AC_IN,
            device_info,
            guid,
            device_name,
            lambda d: convertToKwh(get_ev_station_device(d, guid).work_ac_in),
        ),
        EnergyManagerWorkSensor(
            coordinator,
            em.EVStationDevice.TAG_WORK_AC_OUT,
            device_info,
            guid,
            device_name,
            lambda d: convertToKwh(get_ev_station_device(d, guid).work_ac_out),
        ),
        EnergyManagerWorkSensor(
            coordinator,
            em.EVStationDevice.TAG_WORK_AC_IN_SESSION,
            device_info,
            guid,
            device_name,
            lambda d: convertToKwh(get_ev_station_device(d, guid).work_ac_in_session),
        ),
    ]


def create_s0_counter_sensors(
    coordinator: DataUpdateCoordinator,
    device_info: DeviceInfo,
    s0_counter_device: em.S0CounterDevice,
) -> list[EnergyManagerDataSensor]:
    """Create the sensors for the s0 counter."""
    guid = s0_counter_device.device.guid
    device_name = s0_counter_device.device.get_device_name()
    return [
        EnergyManagerPowerSensor(
            coordinator,
            em.S0CounterDevice.TAG_POWER_IN,
            device_info,
            guid,
            device_name,
            lambda d: get_s0_counter_device(d, guid).power_in,
        ),
        EnergyManagerPowerSensor(
            coordinator,
            em.S0CounterDevice.TAG_POWER_OUT,
            device_info,
            guid,
            device_name,
            lambda d: get_s0_counter_device(d, guid).power_out,
        ),
        EnergyManagerNetPowerSensor(
            coordinator,
            "PowerNet",
            device_info,
            guid,
            device_name,
            lambda d: get_s0_counter_device(d, guid).power_in,
            lambda d: get_s0_counter_device(d, guid).power_out,
        ),
        EnergyManagerWorkSensor(
            coordinator,
            em.S0CounterDevice.TAG_WORK_IN,
            device_info,
            guid,
            device_name,
            lambda d: convertToKwh(get_s0_counter_device(d, guid).work_in),
        ),
        EnergyManagerWorkSensor(
            coordinator,
            em.S0CounterDevice.TAG_WORK_OUT,
            device_info,
            guid,
            device_name,
            lambda d: convertToKwh(get_s0_counter_device(d, guid).work_out),
        ),
    ]


def create_power_meter_sensors(
    coordinator: DataUpdateCoordinator,
    device_info: DeviceInfo,
    power_meter_device: em.PowerMeterDevice,
) -> list[EnergyManagerDataSensor]:
    """Create the sensors for the power meter."""
    guid = power_meter_device.device.guid
    device_name = power_meter_device.device.get_device_name()
    return [
        EnergyManagerPowerSensor(
            coordinator,
            em.PowerMeterDevice.TAG_POWER_IN,
            device_info,
            guid,
            device_name,
            lambda d: get_power_meter_device(d, guid).power_in,
        ),
        EnergyManagerPowerSensor(
            coordinator,
            em.PowerMeterDevice.TAG_POWER_OUT,
            device_info,
            guid,
            device_name,
            lambda d: get_power_meter_device(d, guid).power_out,
        ),
        EnergyManagerNetPowerSensor(
            coordinator,
            "PowerNet",
            device_info,
            guid,
            device_name,
            lambda d: get_power_meter_device(d, guid).power_in,
            lambda d: get_power_meter_device(d, guid).power_out,
        ),
        EnergyManagerWorkSensor(
            coordinator,
            em.PowerMeterDevice.TAG_WORK_IN,
            device_info,
            guid,
            device_name,
            lambda d: convertToKwh(get_power_meter_device(d, guid).work_in),
        ),
        EnergyManagerWorkSensor(
            coordinator,
            em.PowerMeterDevice.TAG_WORK_OUT,
            device_info,
            guid,
            device_name,
            lambda d: convertToKwh(get_power_meter_device(d, guid).work_out),
        ),
    ]
