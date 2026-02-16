"""The solarwatt_energymanager integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import CONFIG_HOST, DOMAIN, ENERGY_MANAGER, POLL_INTERVAL

# Do a lazy import of the upstream client inside runtime functions to avoid
# failing module import when the dependency is not installed. Importing the
# client at module level can cause Home Assistant to mark the integration's
# config flow as an invalid handler if the package is missing.

PLATFORMS = ["sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up solarwatt_energymanager from a config entry."""
    import logging
    _LOGGER = logging.getLogger(__name__)

    # Store API object
    host = entry.data[CONFIG_HOST]
    poll_interval: int = 10
    if POLL_INTERVAL in entry.data:
        try:
            poll_interval = int(entry.data[POLL_INTERVAL])
        except:
            poll_interval = 10

    _LOGGER.info("async_setup_entry: setting up SOLARWATT EnergyManager for host=%s, poll_interval=%s", host, poll_interval)
    
    hass.data.setdefault(DOMAIN, {})
    try:
        _LOGGER.debug("async_setup_entry: importing solarwatt_energymanager")
        import solarwatt_energymanager as em
        _LOGGER.debug("async_setup_entry: creating EnergyManager instance for host %s", host)
        hass.data[DOMAIN][entry.entry_id] = { ENERGY_MANAGER: em.EnergyManager(host), POLL_INTERVAL: poll_interval }
        _LOGGER.info("async_setup_entry: successfully created EnergyManager for host %s", host)
    except Exception as exc:
        # If the upstream package is not available the config entry can
        # still be created, but platform setup will fail later with a clear
        # import error. Store None so other code can handle missing client.
        _LOGGER.error("async_setup_entry: failed to create EnergyManager for host %s: %s", host, exc, exc_info=exc)
        hass.data[DOMAIN][entry.entry_id] = { ENERGY_MANAGER: None, POLL_INTERVAL: poll_interval }
    
    _LOGGER.debug("async_setup_entry: calling async_forward_entry_setups for platforms %s", PLATFORMS)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry. No need to call any cleanup for the EnergyManager object."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
