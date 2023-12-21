# SOLARWATT EnergyManager Home Assistant Custom Component

| Platform        | Description                         |
| --------------- | ----------------------------------- |
| `sensor`        | EnergyManager power and energy sensors. |

⚠️ **EnergyManager Flex** is not supported by this integration, as it uses a completely different OS.

## Installation

Add this repository to HACS.
* In the HACS GUI, select "Custom repositories"
* Enter the following repository URL: https://github.com/Mas2112/solarwatt-energymanager-homeassistant/releases/
* Category: Integration
* After adding the integration, restart Home Assistant.
* Now under Configuration -> Integrations, SOLARWATT EnergyManager should be available.

## Configuration

The configuration is done in the Home Assistant UI.
* Go to Settings -> Devices & Services
* Click on the ADD INTEGRATION button
* Search for SOLARWATT EnergyManager
* Enter the energy manager IP address in the host field
* Enter the desired poll interval (in seconds)
* Click Submit
