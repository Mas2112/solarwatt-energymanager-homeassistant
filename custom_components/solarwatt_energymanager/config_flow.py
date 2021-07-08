"""Config flow for solarwatt_energymanager integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from custom_components.solarwatt_energymanager.energy_manager import (
    CannotConnect,
    CannotParseData,
    EnergyManager,
)
from homeassistant.data_entry_flow import FlowResult

from .const import CONFIG_HOST, DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required("host"): str,
    }
)


async def validate_input(data: dict[str, Any]) -> str:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    host = data[CONFIG_HOST]
    eman = EnergyManager(host)

    # Return info that you want to store in the config entry.
    serial_number = await eman.test_connection()
    _LOGGER.info(f"Validate input host='{host}', found serial number '{serial_number}'")
    return serial_number


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Solarwatt EnergyManager."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        errors = {}

        serial_number = ""
        try:
            serial_number = await validate_input(user_input)
        except CannotConnect:
            errors["base"] = "cannot_connect"
        except CannotParseData:
            errors["base"] = "cannot_parse_data"
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"
        else:
            return self.async_create_entry(
                title=f"EnergyManager {serial_number}", data=user_input
            )

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )
