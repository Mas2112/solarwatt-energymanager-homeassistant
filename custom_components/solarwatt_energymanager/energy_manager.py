"""Code to query and parse data from the EnergyManager."""

import logging
from typing import Optional

import aiohttp

from custom_components.solarwatt_energymanager.devices import (
    EnergyManagerDevices,
)
from homeassistant.exceptions import HomeAssistantError

_LOGGER = logging.getLogger(__name__)


class EnergyManager:
    """The energy manager accessor class."""

    _URL = ""

    def __init__(self, host):
        """Iinitialize class, generate URL."""
        self.host = host
        self._URL = f"http://{self.host}/rest/kiwigrid/wizard/devices"

    async def test_connection(self) -> str:
        """Test the connection. Return value is the EnergyManager serial number."""
        try:
            json_data = await self.query_json_data()
        except Exception:
            raise CannotConnect

        devices = EnergyManagerDevices()
        devices.read_json(json_data)
        energy_manager = devices.get_energy_manager_device()
        try:
            if energy_manager is None:
                raise CannotParseData
        except Exception:
            raise CannotParseData
        return energy_manager.guid

    async def query_devices(self) -> Optional[EnergyManagerDevices]:
        """Query the EnergyManager and return the parsed data."""
        try:
            json = await self.query_json_data()
        except Exception as e:
            _LOGGER.error("Error querying EnergyManager at %s: %s", self._URL, e)
            return None

        try:
            devices = EnergyManagerDevices()
            devices.read_json(json)
            return devices
        except Exception as e:
            _LOGGER.error("Error parsing JSON data from EnergyManager: %s", e)
            return None

    async def query_json_data(self):
        """Query the JSON data from the EnergyManager."""
        _LOGGER.debug("Querying EnergyManager at %s", self._URL)
        async with aiohttp.ClientSession() as session:
            async with session.get(self._URL) as response:
                _LOGGER.debug("Received response status code %s", response.status)
                return await response.json()


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class CannotParseData(HomeAssistantError):
    """Error to indicate that the data cannot be parsed."""
