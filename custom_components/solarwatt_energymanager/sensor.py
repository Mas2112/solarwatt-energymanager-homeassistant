"""Platform for SOLARWATT EnergyManager sensors."""
from __future__ import annotations
from datetime import timedelta
import asyncio
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

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
):
    """Add EnergyManager Sensors."""
    _LOGGER.info("sensor.async_setup_entry: setting up sensors for entry %s", entry.entry_id)
    
    hass_data = hass.data[DOMAIN][entry.entry_id]
    energy_manager = hass_data[ENERGY_MANAGER]
    poll_interval: int = 10
    if POLL_INTERVAL in hass_data:
        poll_interval: int = hass_data[POLL_INTERVAL]
        _LOGGER.debug("sensor.async_setup_entry: poll_interval=%s", poll_interval)
    else:
        _LOGGER.debug("sensor.async_setup_entry: Using default poll_interval=%s", poll_interval)

    if energy_manager is None:
        _LOGGER.error("sensor.async_setup_entry: EnergyManager is None, cannot create sensors")
        return

    async def async_get_data():
        """Fetch data from EnergyManager."""
        _LOGGER.debug("sensor.async_get_data: fetching data from EnergyManager")
        data = None
        try:
            # Note: asyncio.TimeoutError and aiohttp.ClientError are already
            # handled by the data update coordinator.
            _LOGGER.debug("sensor.async_get_data: calling energy_manager.get_data() with timeout %s seconds", poll_interval)
            async with async_timeout.timeout(poll_interval):
                data = await energy_manager.get_data()
            _LOGGER.debug("sensor.async_get_data: successfully fetched data, type=%s", type(data).__name__)
        except asyncio.TimeoutError as timeout_err:
            _LOGGER.error("sensor.async_get_data: timeout after %s seconds: %s", poll_interval, timeout_err)
            raise UpdateFailed(f"Timeout communicating with EnergyManager: {timeout_err}")
        except HomeAssistantError as err:
            _LOGGER.error("sensor.async_get_data: HomeAssistantError: %s", err, exc_info=err)
            raise UpdateFailed(f"Error communicating with EnergyManager: {err}")
        except Exception as exc:
            _LOGGER.error("sensor.async_get_data: unexpected exception type %s: %s", type(exc).__name__, exc, exc_info=exc)
            raise UpdateFailed(f"Unexpected error communicating with EnergyManager: {exc}")
        
        if data is None:
            _LOGGER.error("sensor.async_get_data: EnergyManager returned None")
            raise UpdateFailed("EnergyManager failed to return data")
        return data

    _LOGGER.debug("sensor.async_setup_entry: creating DataUpdateCoordinator")
    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="Process EnergyManager Data",
        update_interval=timedelta(seconds=poll_interval),
        update_method=async_get_data,
    )
    _LOGGER.debug("sensor.async_setup_entry: calling coordinator.async_config_entry_first_refresh()")
    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as exc:
        _LOGGER.error("sensor.async_setup_entry: first refresh failed: %s", exc, exc_info=exc)
        return

    em_data = coordinator.data
    if em_data is None:
        _LOGGER.error("sensor.async_setup_entry: coordinator.data is None after first refresh")
        return
    
    _LOGGER.info("sensor.async_setup_entry: creating sensors from coordinator data")
    entities = create_sensors(coordinator, em_data)
    _LOGGER.info("sensor.async_setup_entry: created %d sensor entities", len(entities))
    async_add_entities(entities)