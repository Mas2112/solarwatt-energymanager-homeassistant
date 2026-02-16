"""Config flow for solarwatt_energymanager integration."""
from __future__ import annotations

from .const import CONFIG_HOST, DEFAULT_POLL_INTERVAL, DOMAIN, POLL_INTERVAL
import logging
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from typing import Any

import voluptuous as vol
import urllib.parse
import asyncio
import re

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
    This normalizes user input (strip scheme/port) and maps low-level network
    errors to the upstream library exceptions used by the config flow.
    """
    # Normalize host input: users may paste `http://` or include a port.
    raw_host = str(data[CONFIG_HOST]).strip()
    parsed = urllib.parse.urlparse(raw_host)
    if parsed.scheme and parsed.netloc:
        host = parsed.netloc
    else:
        host = parsed.path or raw_host

    # Remove trailing slash and optional port to keep host only.
    host = host.rstrip("/")
    if ":" in host:
        host = host.split(":")[0]

    _LOGGER.debug("validate_host: normalized host '%s' from raw input '%s'", host, raw_host)

    try:
        # Lazy import the upstream client so missing dependency does not
        # fail module import (which would make HA treat the config flow as
        # an invalid handler).
        _LOGGER.debug("validate_host: attempting to import solarwatt_energymanager")
        import solarwatt_energymanager as em
        _LOGGER.debug("validate_host: creating EnergyManager for host %s", host)
        eman = em.EnergyManager(host)
        _LOGGER.debug("validate_host: calling test_connection for host %s", host)
        serial_number = await eman.test_connection()
        _LOGGER.info("validate_host: Successfully connected to host='%s', serial=%s", host, serial_number)
        return serial_number
    except Exception as exc:  # pylint: disable=broad-except
        # If the upstream package is present try to map known exception
        # types to preserve specific UI errors; otherwise log and raise
        # the original exception so the caller can map it.
        _LOGGER.debug("validate_host: caught exception type %s: %s", type(exc).__name__, exc, exc_info=exc)
        try:
            import solarwatt_energymanager as em
            if isinstance(exc, em.energy_manager.CannotParseData):
                _LOGGER.error("validate_host: CannotParseData for host %s", host, exc_info=exc)
                raise
            if isinstance(exc, asyncio.TimeoutError):
                _LOGGER.warning("validate_host: Timeout (asyncio.TimeoutError) contacting EnergyManager at %s", host)
                raise em.energy_manager.CannotConnect
            # Fallback: map other errors to CannotConnect
            _LOGGER.debug("validate_host: mapping exception type %s to CannotConnect", type(exc).__name__)
            raise em.energy_manager.CannotConnect
        except ModuleNotFoundError as me:
            # Upstream package missing — log and re-raise original exception
            _LOGGER.error("validate_host: solarwatt_energymanager package not found: %s", me)
            raise
        except Exception:
            # If mapping raised a known upstream exception, re-raise it
            _LOGGER.debug("validate_host: re-raising mapped exception")
            raise


def quick_validate_host_input(data: dict[str, Any]) -> str | None:
    """Perform a short/local validation of the raw host input.

    Returns an error key (string) on failure or `None` when the input looks
    plausibly valid. This avoids attempting a network call for obviously
    invalid inputs (empty, just scheme, contains spaces).
    """
    raw = str(data.get(CONFIG_HOST, "")).strip()
    if not raw:
        return "host_empty"
    # Reject obvious URL-only inputs like 'http://' or 'https://'
    if raw.lower() in ("http://", "https://", "http", "https"):
        return "invalid_host"
    # Reject inputs with spaces; hostnames/IPs should not contain whitespace
    if " " in raw:
        return "host_whitespace"

    # Extract host portion (strip scheme/netloc/port like in validate_host)
    parsed = urllib.parse.urlparse(raw)
    host = parsed.netloc if parsed.scheme and parsed.netloc else parsed.path or raw
    host = host.rstrip("/")
    if ":" in host:
        host = host.split(":")[0]

    # Simple IPv4 check
    ipv4_match = re.fullmatch(r"\d{1,3}(?:\.\d{1,3}){3}", host)
    if ipv4_match:
        parts = host.split(".")
        for p in parts:
            try:
                if not 0 <= int(p) <= 255:
                    return "invalid_host"
            except Exception:
                return "invalid_host"
        return None

    # Hostname regex (labels 1-63 chars, overall up to 253)
    hostname_regex = re.compile(
        r"^(?=.{1,253}$)([a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$"
    )
    if hostname_regex.fullmatch(host):
        return None

    return "invalid_host"


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
            # Quick local validation to catch obvious mistakes before network calls
            quick_err = quick_validate_host_input(user_input)
            if quick_err is not None:
                errors[CONFIG_HOST] = quick_err
                return self.async_show_form(
                    step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
                )

            serial_number = ""
            try:
                serial_number = await validate_host(user_input)
            except Exception as exc:  # pylint: disable=broad-except
                # Map known upstream exceptions to UI error keys if possible
                _LOGGER.debug("async_step_user: caught exception during validate_host, type=%s", type(exc).__name__)
                mapped = False
                try:
                    import solarwatt_energymanager as em
                    if isinstance(exc, em.energy_manager.CannotConnect):
                        _LOGGER.warning("async_step_user: CannotConnect exception caught for host %s", user_input.get(CONFIG_HOST))
                        errors[CONFIG_HOST] = "cannot_connect"
                        mapped = True
                    elif isinstance(exc, em.energy_manager.CannotParseData):
                        _LOGGER.warning("async_step_user: CannotParseData exception caught for host %s", user_input.get(CONFIG_HOST))
                        errors[CONFIG_HOST] = "cannot_parse_data"
                        mapped = True
                except Exception as map_exc:
                    # Upstream not available — fall through to generic handling
                    _LOGGER.debug("async_step_user: could not import upstream to map exception: %s", map_exc)
                    pass

                if not mapped:
                    _LOGGER.error("async_step_user: unmapped exception for validate_host: %s", exc, exc_info=exc)
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
