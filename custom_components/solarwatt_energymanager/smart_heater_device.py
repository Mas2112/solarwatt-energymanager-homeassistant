"""SmartHeater device wrapper.

The upstream solarwatt-energymanager-py library does not model the SmartHeater
device, so we implement the wrapper here, following the same pattern used by
the library's other device classes (e.g. EVStationDevice).
"""

from __future__ import annotations

from typing import Final, Optional

import solarwatt_energymanager as em


class SmartHeaterDevice:
    """Wrapper for the E.G.O. SmartHeater device."""

    DEVICE_CLASS: Final[str] = "com.kiwigrid.devices.smartheater.SmartHeater"

    # Tag name constants
    TAG_POWER_AC_IN: Final[str] = "PowerACIn"
    TAG_POWER_AC_IN_MAX: Final[str] = "PowerACInMax"
    TAG_POWER_AC_IN_LIMIT: Final[str] = "PowerACInLimit"
    TAG_WORK_AC_IN: Final[str] = "WorkACIn"
    TAG_TEMPERATURE: Final[str] = "Temperature"
    TAG_TEMPERATURE_BOILER: Final[str] = "TemperatureBoiler"
    TAG_TEMPERATURE_SET: Final[str] = "TemperatureSet"
    TAG_TEMPERATURE_SET_MIN: Final[str] = "TemperatureSetMin"
    TAG_TEMPERATURE_SET_MAX: Final[str] = "TemperatureSetMax"

    def __init__(self, device: em.Device):
        """Wrap a raw Device as a SmartHeaterDevice."""
        self.device = device

    @property
    def power_ac_in(self) -> Optional[float]:
        """Current AC power being consumed (W)."""
        return self.device.get_tag_value_as_float(SmartHeaterDevice.TAG_POWER_AC_IN)

    @property
    def power_ac_in_max(self) -> Optional[float]:
        """Maximum AC power rating (W)."""
        return self.device.get_tag_value_as_float(SmartHeaterDevice.TAG_POWER_AC_IN_MAX)

    @property
    def power_ac_in_limit(self) -> Optional[float]:
        """Current AC power limit (W)."""
        return self.device.get_tag_value_as_float(SmartHeaterDevice.TAG_POWER_AC_IN_LIMIT)

    @property
    def work_ac_in(self) -> Optional[float]:
        """Total AC energy consumed (Wh)."""
        return self.device.get_tag_value_as_float(SmartHeaterDevice.TAG_WORK_AC_IN)

    @property
    def temperature(self) -> Optional[float]:
        """Current temperature (°C)."""
        return self.device.get_tag_value_as_float(SmartHeaterDevice.TAG_TEMPERATURE)

    @property
    def temperature_boiler(self) -> Optional[float]:
        """Boiler water temperature (°C)."""
        return self.device.get_tag_value_as_float(SmartHeaterDevice.TAG_TEMPERATURE_BOILER)

    @property
    def temperature_set(self) -> Optional[float]:
        """Target temperature setpoint (°C)."""
        return self.device.get_tag_value_as_float(SmartHeaterDevice.TAG_TEMPERATURE_SET)

    @property
    def temperature_set_min(self) -> Optional[float]:
        """Minimum allowed temperature setpoint (°C)."""
        return self.device.get_tag_value_as_float(SmartHeaterDevice.TAG_TEMPERATURE_SET_MIN)

    @property
    def temperature_set_max(self) -> Optional[float]:
        """Maximum allowed temperature setpoint (°C)."""
        return self.device.get_tag_value_as_float(SmartHeaterDevice.TAG_TEMPERATURE_SET_MAX)
