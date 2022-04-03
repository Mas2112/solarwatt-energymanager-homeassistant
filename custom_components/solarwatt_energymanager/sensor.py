"""Platform for SOLARWATT EnergyManager sensors."""
from __future__ import annotations
from datetime import timedelta
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from .const import DOMAIN, ENERGY_MANAGER, POLL_INTERVAL
from .sensor_factory import (create_sensors)
import async_timeout
import logging
import solarwatt_energymanager as em

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
):
    """Add EnergyManager Sensors."""
    hass_data = hass.data[DOMAIN][entry.entry_id]
    em: em.EnergyManager = hass_data[ENERGY_MANAGER]
    poll_interval: int = hass_data[POLL_INTERVAL]

    async def async_get_data():
        """Fetch data from EnergyManager."""
        try:
            # Note: asyncio.TimeoutError and aiohttp.ClientError are already
            # handled by the data update coordinator.
            async with async_timeout.timeout(poll_interval):
                return await em.get_data()
        except HomeAssistantError as err:
            raise UpdateFailed(f"Error communicating with EnergyManager: {err}")

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="Process EnergyManager Data",
        update_interval=timedelta(seconds=10),
        update_method=async_get_data,
    )
    await coordinator.async_config_entry_first_refresh()

    em_data: em.EnergyManagerData = coordinator.data
    entities = create_sensors(coordinator, em_data)
    async_add_entities(entities)