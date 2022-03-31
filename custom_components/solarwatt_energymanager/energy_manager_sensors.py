"""Energy Manager sensor definitions."""
import solarwatt_energymanager as em
from __future__ import annotations

from datetime import timedelta
from typing import (Any, Callable)

import async_timeout

from homeassistant.components.sensor import DEVICE_CLASSES, STATE_CLASS_MEASUREMENT, STATE_CLASS_TOTAL, STATE_CLASS_TOTAL_INCREASING, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from custom_components.solarwatt_energymanager.helper import get_energy_manager_data

from .const import DOMAIN, ENERGY_MANAGER, POLL_INTERVAL

class EnergyManagerDataSensor(CoordinatorEntity, SensorEntity):
    """Base class for an EnergyManager data Sensor."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        name: str,
        device_class: str | None,
        unit: str,
        device_info: DeviceInfo,
        em_device_id: str,
    ):
        """Create a new Sensor Entity for EnergyManager process data."""
        super().__init__(coordinator)
        self._name = name
        self._device_class = device_class
        self._unit = unit
        self._device_info = device_info
        self._em_device_id = em_device_id

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
        return f"{self._em_device_id}.{self._name}"

    @property
    def name(self) -> str:
        """Return the name of this Sensor Entity."""
        return f"EnergyManager {self._name}"

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
        """Get the data value."""
        return "need to implement"


class EnergyManagerPowerSensor(EnergyManagerDataSensor):
    """The EnergyManager power sensor."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        name: str,
        device_info: DeviceInfo,
        em_device_id: str,
        em_value_func: Callable[[em.EnergyManagerData], float],
    ):
        """Create a new Power Sensor Entity."""
        super().__init__(
            coordinator,
            name,
            "power",
            "W",
            device_info,
            em_device_id,
        )
        self._em_value_func = em_value_func
        self._attr_state_class = STATE_CLASS_MEASUREMENT

    def get_data(self) -> Any | None:
        """Get the data from the coordinator as int. Power data is reported as int."""
        try:
            return self._em_value_func(get_energy_manager_data(self.coordinator))
        except Exception:
            return None


class EnergyManagerNetPowerSensor(EnergyManagerDataSensor):
    """The EnergyManager power sensor that calculates the net power between two values."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        name: str,
        device_info: DeviceInfo,
        em_device_id,
        em_value_func1: Callable[[em.EnergyManagerData], float],
        em_value_func2: Callable[[em.EnergyManagerData], float],
    ):
        """Create a new Net Power Sensor Entity."""
        super().__init__(
            coordinator,
            name,
            "power",
            "W",
            device_info,
            em_device_id,
        )
        self._em_value_func1 = em_value_func1
        self._em_value_func2 = em_value_func2
        self._attr_state_class = STATE_CLASS_MEASUREMENT

    def get_data(self) -> Any | None:
        """Get the data from the coordinator as int. Power data is reported as int."""
        try:
            data = get_energy_manager_data(self.coordinator)
            value1 = self._em_value_func1(data)
            value2 = self._em_value_func2(data)
            return value1 - value2
        except Exception:
            return None


class EnergyManagerWorkSensor(EnergyManagerDataSensor):
    """The EnergyManager work (energy) sensor."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        name: str,
        device_info: DeviceInfo,
        em_device_id: str,
        em_value_func: Callable[[em.EnergyManagerData], float],
    ):
        """Create a new Power Sensor Entity."""
        super().__init__(
            coordinator,
            name,
            "energy",
            "kWh",
            device_info,
            em_device_id,
        )
        self._em_value_func = em_value_func
        self._attr_state_class = STATE_CLASS_TOTAL_INCREASING

    def get_data(self) -> Any | None:
        """Get the data from the coordinator as float in kWh. Data is originally Wh."""
        try:
            return self.em_value_func(get_energy_manager_data(self.coordinator))
        except Exception:
            return None


class EnergyManagerStateOfChargeSensor(EnergyManagerDataSensor):
    """The EnergyManager battery state of charge sensor."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        name: str,
        device_info: DeviceInfo,
        em_device_id: str,
        em_value_func: Callable[[em.EnergyManagerData], float],
    ):
        """Create a new Power Sensor Entity."""
        super().__init__(
            coordinator,
            name,
            "battery",
            "%",
            device_info,
            em_device_id,
        )
        self._em_value_func = em_value_func
        self._attr_state_class = STATE_CLASS_MEASUREMENT

    def get_data(self) -> Any | None:
        """Get the data from the coordinator as float."""
        try:
            return self.em_value_func(get_energy_manager_data(self.coordinator))
        except Exception:
            return None


class EnergyManagerStateOfHealthSensor(EnergyManagerDataSensor):
    """The EnergyManager battery state of health sensor."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        name: str,
        device_info: DeviceInfo,
        em_device_id: str,
        em_value_func: Callable[[em.EnergyManagerData], float],
    ):
        """Create a new Sensor Entity."""
        super().__init__(
            coordinator,
            name,
            None,
            "%",
            device_info,
            em_device_id,
        )
        self._em_value_func = em_value_func
        self._attr_state_class = STATE_CLASS_MEASUREMENT

    def get_data(self) -> Any | None:
        """Get the data from the coordinator as float."""
        try:
            return self.em_value_func(get_energy_manager_data(self.coordinator))
        except Exception:
            return None


class EnergyManagerTemperatureSensor(EnergyManagerDataSensor):
    """The EnergyManager battery temperature sensor."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        name: str,
        device_info: DeviceInfo,
        em_device_id: str,
        em_value_func: Callable[[em.EnergyManagerData], float],
    ):
        """Create a new Sensor Entity."""
        super().__init__(
            coordinator,
            name,
            "temperature",
            "°C",
            device_info,
            em_device_id,
        )
        self._em_value_func = em_value_func
        self._attr_state_class = STATE_CLASS_MEASUREMENT

    def get_data(self) -> Any | None:
        """Get the data from the coordinator as float."""
        try:
            return self.em_value_func(get_energy_manager_data(self.coordinator))
        except Exception:
            return None