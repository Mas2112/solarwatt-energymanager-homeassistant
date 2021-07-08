"""
Contains the definition of the EnergyManager devices and the parsing logic.

Not all devices here are modelled. This should be expanded as needed.
This has not been tested with MyReserve battery.

The following assumptions are made, and may need to be adjusted:
- Only one location device exists
- Only one energy manager device exists
- Only one battery may exist - needs to be extended for more batteries


The JSON data has the structure:
result: {
    items: [{
        tagValues: {
            tagName: string,
            guid: string,
            value: Any
        },
        deviceModel: [{
            deviceClass: string
        }, {
            deviceClass: string
        }],
        guid: string
    }]
}
"""

from typing import Any, Dict, Final, List, Optional


class Device:
    """The base definition for an EnergyManager device."""

    # The unique ID of the device.
    guid: str = ""

    # The device classes defined for this device.
    device_classes: List[str] = []

    # The tag items of the device.
    tag_items: Dict[str, Any] = {}

    def read_json_item(self, item):
        """Read the item JSON data into this object."""
        self.guid = item["guid"] if "guid" in item else ""
        self.device_classes = Device.get_item_device_classes(item)
        self.tag_items = Device.get_tag_items(item)

    def get_tag_value_as_str(self, tag_name) -> str:
        """Get the item tag value as a string."""
        try:
            if tag_name in self.tag_items:
                return str(self.tag_items[tag_name])
            return ""
        except Exception:
            return ""

    def get_tag_value_as_int(self, tag_name) -> int:
        """Get the item tag value as an int."""
        try:
            return int(float(self.tag_items[tag_name]))
        except Exception:
            return int(0)

    def get_tag_value_as_float(self, tag_name) -> float:
        """Get the item tag value as a float."""
        try:
            return float(self.tag_items[tag_name])
        except Exception:
            return float(0)

    @staticmethod
    def get_item_device_classes(item: dict) -> List[str]:
        """Get the devices classes of the items."""
        classes: List[str] = []
        if "deviceModel" in item:
            device_model_items = item["deviceModel"]
            for device_model_item in device_model_items:
                if "deviceClass" in device_model_item:
                    classes.append(device_model_item["deviceClass"])
        return classes

    @staticmethod
    def get_tag_items(item: dict) -> Dict[str, Any]:
        """Get the tag items of the item."""
        items: Dict[str, Any] = {}
        if "tagValues" in item:
            tag_values = item["tagValues"]
            for tag_name, tag_value in tag_values.items():
                items[tag_name] = tag_value["value"] if "value" in tag_value else ""
        return items


class LocationDevice(Device):
    """
    The Location EnergyManager device. Contains most of the interesting info.

    The power tags contain the instantaneous power readings.
    The work tags contain the accumulated energy values in Wh.
    """

    DEVICE_CLASS: Final[str] = "com.kiwigrid.devices.location.Location"

    # Tag name constants
    TAG_POWER_BUFFERED: Final[str] = "PowerBuffered"
    TAG_POWER_BUFFERED_FROM_GRID: Final[str] = "PowerBufferedFromGrid"
    TAG_POWER_CONSUMED: Final[str] = "PowerConsumed"
    TAG_POWER_CONSUMED_FROM_GRID: Final[str] = "PowerConsumedFromGrid"
    TAG_POWER_CONSUMED_FROM_PRODUCERS: Final[str] = "PowerConsumedFromProducers"
    TAG_POWER_CONSUMED_FROM_STORAGE: Final[str] = "PowerConsumedFromStorage"
    TAG_POWER_IN: Final[str] = "PowerIn"
    TAG_POWER_OUT: Final[str] = "PowerOut"
    TAG_POWER_OUT_FROM_PRODUCERS: Final[str] = "PowerOutFromProducers"
    TAG_POWER_PRODUCED: Final[str] = "PowerProduced"
    TAG_POWER_RELEASED: Final[str] = "PowerReleased"
    TAG_POWER_SELF_CONSUMED: Final[str] = "PowerSelfConsumed"

    TAG_WORK_BUFFERED: Final[str] = "WorkBuffered"
    TAG_WORK_BUFFERED_FROM_GRID: Final[str] = "WorkBufferedFromGrid"
    TAG_WORK_BUFFERED_FROM_PRODUCERS: Final[str] = "WorkBufferedFromProducers"
    TAG_WORK_CONSUMED: Final[str] = "WorkConsumed"
    TAG_WORK_CONSUMED_FROM_GRID: Final[str] = "WorkConsumedFromGrid"
    TAG_WORK_CONSUMED_FROM_PRODUCERS: Final[str] = "WorkConsumedFromProducers"
    TAG_WORK_CONSUMED_FROM_STORAGE: Final[str] = "WorkConsumedFromStorage"
    TAG_WORK_IN: Final[str] = "WorkIn"
    TAG_WORK_OUT: Final[str] = "WorkOut"
    TAG_WORK_OUT_FROM_STORAGE: Final[str] = "WorkOutFromStorage"
    TAG_WORK_OUT_FROM_PRODUCERS: Final[str] = "WorkOutFromProducers"
    TAG_WORK_PRODUCED: Final[str] = "WorkProduced"
    TAG_WORK_RELEASED: Final[str] = "WorkReleased"
    TAG_WORK_SELF_CONSUMED: Final[str] = "WorkSelfConsumed"
    TAG_WORK_SELF_SUPPLIED: Final[str] = "WorkSelfSupplied"

    def __init__(self, device: Device):
        """Wrap the device with LocationDevice."""
        self.__dict__ = device.__dict__


class BatteryConverterDevice(Device):
    """The battery converter EnergyManager device. Contains info about flow to and from battery."""

    DEVICE_CLASS: Final = "com.kiwigrid.devices.batteryconverter.BatteryConverter"

    # Tag name constants
    TAG_MODE_CONVERTER: Final[str] = "ModeConverter"
    TAG_STATE_OF_CHARGE: Final[str] = "StateOfCharge"
    TAG_STATE_OF_HEALTH: Final[str] = "StateOfHealth"
    TAG_TEMPERATURE_BATTERY: Final[str] = "TemperatureBattery"

    def __init__(self, device: Device):
        """Wrap the device with BatteryConverterDevice."""
        self.__dict__ = device.__dict__


class EnergyManagerDevice(Device):
    """The EnergyManager device itself. Needed to get the device model and serial number."""

    DEVICE_CLASS: Final = "com.kiwigrid.devices.em.EnergyManager"

    # Tag name constants
    TAG_MODEL: Final[str] = "IdModelCode"
    TAG_FIRMWARE: Final[str] = "IdFirmware"

    def __init__(self, device: Device):
        """Wrap the device with EnergyManagerDevice."""
        self.__dict__ = device.__dict__

    def get_model(self) -> str:
        """Get the EnergyManager model."""
        return self.get_tag_value_as_str(EnergyManagerDevice.TAG_MODEL)

    def get_firmware(self) -> str:
        """Get the EnergyManager firmware."""
        return self.get_tag_value_as_str(EnergyManagerDevice.TAG_FIRMWARE)


class EnergyManagerDevices:
    """Contains all of the energy manager devices and the getter methods."""

    devices: Dict[str, Device] = {}

    def read_json(self, json: dict) -> None:
        """Read the json data from the EnergyManager."""
        if "result" in json:
            result = json["result"]
            if "items" in result:
                items = result["items"]
                for item in items:
                    device = Device()
                    device.read_json_item(item)
                    self.devices[device.guid] = device

    def get_device(self, device_class: str) -> Optional[Device]:
        """Get the specified device."""
        return next(
            (d for d in self.devices.values() if device_class in d.device_classes), None
        )

    def get_energy_manager_device(self) -> Optional[EnergyManagerDevice]:
        """Get the EnergyManagerDevice."""
        device = self.get_device(EnergyManagerDevice.DEVICE_CLASS)
        return EnergyManagerDevice(device) if device else None

    def get_location_device(self) -> Optional[LocationDevice]:
        """Get the LocationDevice."""
        device = self.get_device(LocationDevice.DEVICE_CLASS)
        return LocationDevice(device) if device else None

    def get_battery_converter_device(self) -> Optional[BatteryConverterDevice]:
        """Get the BatteryConverterDevice."""
        device = self.get_device(BatteryConverterDevice.DEVICE_CLASS)
        return BatteryConverterDevice(device) if device else None
