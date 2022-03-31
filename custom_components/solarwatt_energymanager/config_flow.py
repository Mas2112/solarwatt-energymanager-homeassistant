"""Config flow for solarwatt_energymanager integration."""
from __future__ import annotations

from .const import CONFIG_HOST, DEFAULT_POLL_INTERVAL, DOMAIN, POLL_INTERVAL
import logging
import solarwatt_energymanager as em
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from typing import Any

import voluptuous as vol

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONFIG_HOST): str,
        vol.Required(POLL_INTERVAL, default=DEFAULT_POLL_INTERVAL): int,
    }
)


async def validate_host(data: dict[str, Any]) -> str:
    """Validate the host, checks if can connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    host = data[CONFIG_HOST]
    eman = em.EnergyManager(host)

    # Return info that you want to store in the config entry.
    serial_number = await eman.test_connection()
    _LOGGER.info(f"Validate input host='{host}', found serial number '{serial_number}'")

    return serial_number


def validate_poll_interval(data: dict[str, Any]) -> str:
    try:
        poll_interval = int(data[POLL_INTERVAL])
        if poll_interval < 1:
            return "poll_interval_value"
        _LOGGER.info(f"Validate poll interval '{poll_interval}'")
    except Exception:  # pylint: disable=broad-except
        return "poll_interval_num"
    return None


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Solarwatt EnergyManager."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""

        errors = {}
        if user_input is not None:
            serial_number = ""
            try:
                serial_number = await validate_host(user_input)
            except em.CannotConnect:
                errors[CONFIG_HOST] = "cannot_connect"
            except em.CannotParseData:
                errors[CONFIG_HOST] = "cannot_parse_data"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors[CONFIG_HOST] = "unknown"
            else:
                error = validate_poll_interval(user_input)
                if error is not None:
                    errors[POLL_INTERVAL] = error
                else:
                    return self.async_create_entry(
                        title=f"EnergyManager {serial_number}", data=user_input
                    )

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )
