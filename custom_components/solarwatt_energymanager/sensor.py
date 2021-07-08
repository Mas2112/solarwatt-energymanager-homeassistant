"""Platform for SOLARWATT EnergyManager sensors."""
from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

import async_timeout

from homeassistant.components.sensor import SensorEntity
from custom_components.solarwatt_energymanager.devices import (
    BatteryConverterDevice,
    LocationDevice,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import DOMAIN
from .energy_manager import EnergyManager, EnergyManagerDevices

_LOGGER = logging.getLogger(__name__)


def get_device_info(devices: EnergyManagerDevices) -> DeviceInfo:
    """Get the device info for the EnergyManager."""
    energy_manager = devices.get_energy_manager_device()
    guid = energy_manager.guid if energy_manager else ""
    model = energy_manager.get_model() if energy_manager else ""
    firmware = energy_manager.get_firmware() if energy_manager else ""
    return DeviceInfo(
        name=guid,
        manufacturer="SOLARWATT",
        identifiers={(DOMAIN, guid)},
        model=model,
        sw_version=firmware,
    )


def create_location_sensors(
    coordinator: DataUpdateCoordinator,
    device_info: DeviceInfo,
    location_device: LocationDevice,
) -> list[EnergyManagerDataSensor]:
    """Create the sensors for the location device."""
    return [
        EnergyManagerPowerSensor(
            coordinator,
            LocationDevice.TAG_POWER_BUFFERED,
            device_info,
            LocationDevice.DEVICE_CLASS,
            location_device.guid,
            LocationDevice.TAG_POWER_BUFFERED,
        ),
        EnergyManagerPowerSensor(
            coordinator,
            LocationDevice.TAG_POWER_CONSUMED,
            device_info,
            LocationDevice.DEVICE_CLASS,
            location_device.guid,
            LocationDevice.TAG_POWER_CONSUMED,
        ),
        EnergyManagerPowerSensor(
            coordinator,
            LocationDevice.TAG_POWER_IN,
            device_info,
            LocationDevice.DEVICE_CLASS,
            location_device.guid,
            LocationDevice.TAG_POWER_IN,
        ),
        EnergyManagerPowerSensor(
            coordinator,
            LocationDevice.TAG_POWER_OUT,
            device_info,
            LocationDevice.DEVICE_CLASS,
            location_device.guid,
            LocationDevice.TAG_POWER_OUT,
        ),
        EnergyManagerPowerSensor(
            coordinator,
            LocationDevice.TAG_POWER_PRODUCED,
            device_info,
            LocationDevice.DEVICE_CLASS,
            location_device.guid,
            LocationDevice.TAG_POWER_PRODUCED,
        ),
        EnergyManagerPowerSensor(
            coordinator,
            LocationDevice.TAG_POWER_RELEASED,
            device_info,
            LocationDevice.DEVICE_CLASS,
            location_device.guid,
            LocationDevice.TAG_POWER_RELEASED,
        ),
        EnergyManagerWorkSensor(
            coordinator,
            LocationDevice.TAG_WORK_BUFFERED,
            device_info,
            LocationDevice.DEVICE_CLASS,
            location_device.guid,
            LocationDevice.TAG_WORK_BUFFERED,
        ),
        EnergyManagerWorkSensor(
            coordinator,
            LocationDevice.TAG_WORK_CONSUMED,
            device_info,
            LocationDevice.DEVICE_CLASS,
            location_device.guid,
            LocationDevice.TAG_WORK_CONSUMED,
        ),
        EnergyManagerWorkSensor(
            coordinator,
            LocationDevice.TAG_WORK_IN,
            device_info,
            LocationDevice.DEVICE_CLASS,
            location_device.guid,
            LocationDevice.TAG_WORK_IN,
        ),
        EnergyManagerWorkSensor(
            coordinator,
            LocationDevice.TAG_WORK_OUT,
            device_info,
            LocationDevice.DEVICE_CLASS,
            location_device.guid,
            LocationDevice.TAG_WORK_OUT,
        ),
        EnergyManagerWorkSensor(
            coordinator,
            LocationDevice.TAG_WORK_PRODUCED,
            device_info,
            LocationDevice.DEVICE_CLASS,
            location_device.guid,
            LocationDevice.TAG_WORK_PRODUCED,
        ),
        EnergyManagerWorkSensor(
            coordinator,
            LocationDevice.TAG_WORK_RELEASED,
            device_info,
            LocationDevice.DEVICE_CLASS,
            location_device.guid,
            LocationDevice.TAG_WORK_RELEASED,
        ),
    ]


def create_battery_converter_sensors(
    coordinator: DataUpdateCoordinator,
    device_info: DeviceInfo,
    batter_converter_device: BatteryConverterDevice,
) -> list[EnergyManagerDataSensor]:
    """Create the sensors for the battery converter."""
    return [
        EnergyManagerStateOfChargeSensor(
            coordinator,
            BatteryConverterDevice.TAG_STATE_OF_CHARGE,
            device_info,
            BatteryConverterDevice.DEVICE_CLASS,
            batter_converter_device.guid,
            BatteryConverterDevice.TAG_STATE_OF_CHARGE,
        ),
        EnergyManagerStateOfHealthSensor(
            coordinator,
            BatteryConverterDevice.TAG_STATE_OF_HEALTH,
            device_info,
            BatteryConverterDevice.DEVICE_CLASS,
            batter_converter_device.guid,
            BatteryConverterDevice.TAG_STATE_OF_HEALTH,
        ),
        EnergyManagerTemperatureSensor(
            coordinator,
            BatteryConverterDevice.TAG_TEMPERATURE_BATTERY,
            device_info,
            BatteryConverterDevice.DEVICE_CLASS,
            batter_converter_device.guid,
            BatteryConverterDevice.TAG_TEMPERATURE_BATTERY,
        ),
    ]


def create_sensors(
    coordinator: DataUpdateCoordinator, devices: EnergyManagerDevices
) -> list[EnergyManagerDataSensor]:
    """Create the sensors for the the available devices."""
    device_info = get_device_info(devices)
    location_device = devices.get_location_device()
    entities = []
    if location_device:
        _LOGGER.info("Creating sensor entities for the location device")
        entities.extend(
            create_location_sensors(coordinator, device_info, location_device)
        )
    battery_converter_device = devices.get_battery_converter_device()
    if battery_converter_device:
        _LOGGER.info("Creating sensor entities for the battery converter device")
        entities.extend(
            create_battery_converter_sensors(
                coordinator, device_info, battery_converter_device
            )
        )
    return entities


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
):
    """Add EnergyManager Sensors."""
    em: EnergyManager = hass.data[DOMAIN][entry.entry_id]

    async def async_get_data():
        """Fetch data from EnergyManager."""
        try:
            # Note: asyncio.TimeoutError and aiohttp.ClientError are already
            # handled by the data update coordinator.
            async with async_timeout.timeout(10):
                return await em.query_devices()
        except HomeAssistantError as err:
            raise UpdateFailed(f"Error communicating with EnergyManager: {err}")

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="Process EnergyManager Data",
        update_interval=timedelta(seconds=30),
        update_method=async_get_data,
    )
    await coordinator.async_config_entry_first_refresh()

    devices: EnergyManagerDevices = coordinator.data
    entities = create_sensors(coordinator, devices)
    async_add_entities(entities)


class EnergyManagerDataSensor(CoordinatorEntity, SensorEntity):
    """Base class for an EnergyManager data Sensor."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        name: str,
        device_class: str | None,
        unit: str,
        device_info: DeviceInfo,
        em_device_class: str,
        em_device_id: str,
        em_tag_name: str,
    ):
        """Create a new Sensor Entity for EnergyManager process data."""
        super().__init__(coordinator)
        self._name = name
        self._device_class = device_class
        self._unit = unit
        self._device_info = device_info
        self._em_device_class = em_device_class
        self._em_device_id = em_device_id
        self._em_tag_name = em_tag_name

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return (
            super().available
            and self.coordinator.data is not None
            and self.get_data() is not None
        )

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return self._device_info

    @property
    def unique_id(self) -> str:
        """Return the unique id of this Sensor Entity."""
        return f"{self._em_device_id}.{self._em_tag_name}"

    @property
    def name(self) -> str:
        """Return the name of this Sensor Entity."""
        return self._em_tag_name

    @property
    def unit_of_measurement(self) -> str | None:
        """Return the unit of this Sensor Entity or None."""
        return self._unit

    @property
    def device_class(self) -> str | None:
        """Return the class of this device, from component DEVICE_CLASSES."""
        return self._device_class

    @property
    def entity_registry_enabled_default(self) -> bool:
        """Return if the entity should be enabled when first added to the entity registry."""
        return True

    @property
    def state(self) -> Any | None:
        """Return the state of the sensor."""
        if self.coordinator.data is None:
            # None is translated to STATE_UNKNOWN
            return None

        return self.get_data()

    def get_data(self) -> Any | None:
        """Get the data from the coordinator as string."""
        try:
            devices: EnergyManagerDevices = self.coordinator.data
            return devices.devices[self._em_device_id].get_tag_value_as_str(
                self._em_tag_name
            )
        except Exception:
            return None


class EnergyManagerPowerSensor(EnergyManagerDataSensor):
    """The EnergyManager power sensor."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        name: str,
        device_info: DeviceInfo,
        em_device_class: str,
        em_device_id: str,
        em_tag_name: str,
    ):
        """Create a new Power Sensor Entity."""
        super().__init__(
            coordinator,
            name,
            "power",
            "W",
            device_info,
            em_device_class,
            em_device_id,
            em_tag_name,
        )

    def get_data(self) -> Any | None:
        """Get the data from the coordinator as int. Power data is reported as int."""
        try:
            devices: EnergyManagerDevices = self.coordinator.data
            return devices.devices[self._em_device_id].get_tag_value_as_int(
                self._em_tag_name
            )
        except Exception:
            return None


class EnergyManagerWorkSensor(EnergyManagerDataSensor):
    """The EnergyManager work (energy) sensor."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        name: str,
        device_info: DeviceInfo,
        em_device_class: str,
        em_device_id: str,
        em_tag_name: str,
    ):
        """Create a new Power Sensor Entity."""
        super().__init__(
            coordinator,
            name,
            "energy",
            "kWh",
            device_info,
            em_device_class,
            em_device_id,
            em_tag_name,
        )

    def get_data(self) -> Any | None:
        """Get the data from the coordinator as float in kWh. Data is originally Wh."""
        try:
            devices: EnergyManagerDevices = self.coordinator.data
            return round(
                devices.devices[self._em_device_id].get_tag_value_as_float(
                    self._em_tag_name
                )
                / 1000,
                3,
            )
        except Exception:
            return None


class EnergyManagerStateOfChargeSensor(EnergyManagerDataSensor):
    """The EnergyManager battery state of charge sensor."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        name: str,
        device_info: DeviceInfo,
        em_device_class: str,
        em_device_id: str,
        em_tag_name: str,
    ):
        """Create a new Power Sensor Entity."""
        super().__init__(
            coordinator,
            name,
            "battery",
            "%",
            device_info,
            em_device_class,
            em_device_id,
            em_tag_name,
        )

    def get_data(self) -> Any | None:
        """Get the data from the coordinator as float."""
        try:
            devices: EnergyManagerDevices = self.coordinator.data
            return round(
                devices.devices[self._em_device_id].get_tag_value_as_float(
                    self._em_tag_name
                ),
                1,
            )
        except Exception:
            return None


class EnergyManagerStateOfHealthSensor(EnergyManagerDataSensor):
    """The EnergyManager battery state of health sensor."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        name: str,
        device_info: DeviceInfo,
        em_device_class: str,
        em_device_id: str,
        em_tag_name: str,
    ):
        """Create a new Sensor Entity."""
        super().__init__(
            coordinator,
            name,
            None,
            "%",
            device_info,
            em_device_class,
            em_device_id,
            em_tag_name,
        )

    def get_data(self) -> Any | None:
        """Get the data from the coordinator as float."""
        try:
            devices: EnergyManagerDevices = self.coordinator.data
            return round(
                devices.devices[self._em_device_id].get_tag_value_as_float(
                    self._em_tag_name
                ),
                1,
            )
        except Exception:
            return None


class EnergyManagerTemperatureSensor(EnergyManagerDataSensor):
    """The EnergyManager battery temperature sensor."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        name: str,
        device_info: DeviceInfo,
        em_device_class: str,
        em_device_id: str,
        em_tag_name: str,
    ):
        """Create a new Sensor Entity."""
        super().__init__(
            coordinator,
            name,
            "temperature",
            "°C",
            device_info,
            em_device_class,
            em_device_id,
            em_tag_name,
        )

    def get_data(self) -> Any | None:
        """Get the data from the coordinator as float."""
        try:
            devices: EnergyManagerDevices = self.coordinator.data
            return round(
                devices.devices[self._em_device_id].get_tag_value_as_float(
                    self._em_tag_name
                ),
                1,
            )
        except Exception:
            return None
