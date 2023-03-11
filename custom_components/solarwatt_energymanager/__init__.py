"""The solarwatt_energymanager integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import CONFIG_HOST, DOMAIN, ENERGY_MANAGER, POLL_INTERVAL

import solarwatt_energymanager as em

PLATFORMS = ["sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up solarwatt_energymanager from a config entry."""

    # Store API object
    host = entry.data[CONFIG_HOST]
    poll_interval: int = 10
    if POLL_INTERVAL in entry.data:
        try:
            poll_interval = int(entry.data[POLL_INTERVAL])
        except:
            poll_interval = 10

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = { ENERGY_MANAGER: em.EnergyManager(host), POLL_INTERVAL: poll_interval }
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry. No need to call any cleanup for the EnergyManager object."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
