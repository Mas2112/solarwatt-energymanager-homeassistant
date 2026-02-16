<!-- Copilot / AI agent guidance for contributors -->
# Quick instructions for AI coding agents

Purpose: Help an AI agent become productive quickly in this Home Assistant custom integration.

- **Big picture:** This repo implements a Home Assistant integration under `custom_components/solarwatt_energymanager` that polls a local SOLARWATT EnergyManager device and exposes sensors. Key runtime pieces:
  - Integration entry points: `async_setup_entry` in [custom_components/solarwatt_energymanager/__init__.py](custom_components/solarwatt_energymanager/__init__.py#L1-L40) registers `sensor` platform.
  - Polling & coordinator: [custom_components/solarwatt_energymanager/sensor.py](custom_components/solarwatt_energymanager/sensor.py#L1-L120) uses `DataUpdateCoordinator` and `async_get_data()` to call the external library's `get_data()` with a timeout.
  - Sensor construction: sensors are created programmatically from API data by [sensor_factory.create_sensors](custom_components/solarwatt_energymanager/sensor_factory.py#L1-L60) which inspects `EnergyManagerData` and returns entity instances defined in [energy_manager_sensors.py](custom_components/solarwatt_energymanager/energy_manager_sensors.py#L1-L220).

- **Why structure is this way:** The integration relies on the upstream async client `solarwatt_energymanager` (declared in `manifest.json`) to fetch a full snapshot; the code converts that snapshot into multiple Home Assistant sensor entities. The coordinator pattern centralizes polling and error handling.

- **Key patterns & conventions (explicit, project-specific):**
  - Poll interval is stored in the config entry under key `poll_interval` (see `const.py`). Default `DEFAULT_POLL_INTERVAL = 10`.
  - The integration stores an `EnergyManager` instance and the poll interval in `hass.data[DOMAIN][entry.entry_id]` (see `__init__.py`).
  - Entities use `unique_id` of form `{em_device_id}.{sensor_name}` and a human name `EnergyManager {em_device_name} {sensor_name}` (see `energy_manager_sensors.py`).
  - Device identity: uses GUID from upstream data and sets `DeviceInfo.identifiers={(DOMAIN, guid)}` in `sensor_factory.get_device_info`.

- **Important files to consult for changes or examples:**
  - [custom_components/solarwatt_energymanager/manifest.json](custom_components/solarwatt_energymanager/manifest.json#L1-L40) — package requirements (`solarwatt-energymanager-py[aiohttp]==1.4.1`) and integration metadata.
  - [custom_components/solarwatt_energymanager/config_flow.py](custom_components/solarwatt_energymanager/config_flow.py#L1-L200) — config-flow validation and error codes used for UI strings.
  - [custom_components/solarwatt_energymanager/sensor_factory.py](custom_components/solarwatt_energymanager/sensor_factory.py#L1-L120) — shows how device lists map to sensors.
  - [custom_components/solarwatt_energymanager/energy_manager_sensors.py](custom_components/solarwatt_energymanager/energy_manager_sensors.py#L1-L220) — base entity classes and `get_data()` implementation pattern.

- **Developer workflows & quick commands (discoverable here):**
  - This is a Home Assistant custom integration intended for HACS/local install. Typical manual steps to test locally:
    1. Install integration files into HA `custom_components` (repo already structured that way).
    2. Ensure dependency `solarwatt-energymanager-py[aiohttp]==1.4.1` is available in HA environment (manifest enforces it for HACS installs).
    3. Use the HA UI to add integration (Settings → Devices & Services → Add Integration) and supply `host` + `poll_interval` (see `README.md`).
  - Debugging notes: logs are produced via `_LOGGER` in sensor and factory modules. Focus on coordinator exceptions (`UpdateFailed`) and `em` library exceptions (`CannotConnect`, `CannotParseData`) surfaced in `config_flow.py`.

- **Integration points / external dependencies:**
  - Upstream client library: `solarwatt_energymanager` (async API: `EnergyManager(host)`, `get_data()`, `test_connection()`), used across `__init__.py`, `config_flow.py`, `sensor.py`, and factories.

- **Safe change rules for AI agents (do not guess runtime):**
  - Do not change the external library version in `manifest.json` without confirming compatibility with upstream releases.
  - Preserve entity `unique_id` and `DeviceInfo.identifiers` patterns to avoid creating duplicate devices in user installations.
  - When altering data access, prefer adding `try/except` around calls into `coordinator.data` and follow the existing `UpdateFailed` usage.

- **Small examples to follow:**
  - Creating a new power sensor: follow `EnergyManagerPowerSensor` in `energy_manager_sensors.py` (use `SensorDeviceClass.POWER`, `UnitOfPower.WATT`, and `SensorStateClass.MEASUREMENT`).
  - Adding config validation: follow `validate_host()` and `validate_poll_interval()` in `config_flow.py` and reuse existing error keys from `strings.json`.

If any section is unclear or you want this condensed/translated, tell me which parts to iterate on.
