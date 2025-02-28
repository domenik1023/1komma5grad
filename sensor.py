# custom_components/1komma5grad/sensor.py
from datetime import datetime
import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, SENSOR_CONFIG

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities) -> None:
    """Set up sensor platform for 1Komma5Grad."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    sensors = []
    for sensor_key, sensor_conf in SENSOR_CONFIG.items():
        sensors.append(
            Custom1Komma5GradSensor(
                coordinator, config_entry.entry_id, sensor_key, sensor_conf
            )
        )

    # Batterie
    sensors.append(BatteryStateOfChargeSensor(coordinator, config_entry.entry_id))
    sensors.append(BatteryPowerSensor(coordinator, config_entry.entry_id))
    sensors.append(BatteryInSensor(coordinator, config_entry.entry_id))
    sensors.append(BatteryOutSensor(coordinator, config_entry.entry_id))

    # Total IntegrationSensor
    # for sensor_conf in IntegrationSensor.values():
    #     sensors.append(
    #         IntegrationSensor(coordinator, config_entry.entry_id, sensor_conf)
    #     )

    async_add_entities(sensors, update_before_add=True)


class Custom1Komma5GradSensor(CoordinatorEntity, SensorEntity):
    """Representation of a specific 1Komma5Grad sensor with customizable attributes."""

    def __init__(self, coordinator, entry_id, sensor_key, sensor_conf):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._entry_id = entry_id
        self._sensor_key = sensor_key
        self._sensor_conf = sensor_conf

        self._attr_name = sensor_conf.get("name", sensor_key)
        self._attr_unique_id = f"{entry_id}_{sensor_key}"
        self._attr_device_class = sensor_conf.get("device_class")
        self._attr_state_class = sensor_conf.get("state_class")
        # Do not set _attr_unit_of_measurement here;
        # instead, we override the property to always return our custom unit.

    @property
    def state(self):
        """Return the sensor state."""
        live_data = self.coordinator.data.get("liveHeroView", {})
        sensor_data = live_data.get(self._sensor_key)
        if sensor_data is None:
            return None
        if isinstance(sensor_data, dict) and "value" in sensor_data:
            return round(
                sensor_data["value"], 1
            )  # Change this Value if you wan't other roundings
        return sensor_data

    @property
    def unit_of_measurement(self):
        """Always return the configured unit, regardless of API data."""
        return self._sensor_conf.get("unit")


# Region BatteryChargePercentage
class BatteryStateOfChargeSensor(CoordinatorEntity, SensorEntity):
    """Sensor to report Battery State of Charge from summaryCards as a percentage."""

    def __init__(self, coordinator, entry_id):
        """Initialize the Battery State of Charge sensor."""
        super().__init__(coordinator)
        self._entry_id = entry_id
        self._attr_name = "Battery State of Charge"
        self._attr_unique_id = f"{entry_id}_battery_state_of_charge"
        # Use a device_class of battery or leave it as None if you prefer.
        self._attr_device_class = "battery"
        self._attr_state_class = "measurement"
        self._attr_unit_of_measurement = "%"

    @property
    def state(self):
        """Return the battery state of charge as a percentage.

        Assumes the API returns a fractional value (e.g., 0.13).
        If the API already returns a percentage (e.g., 13), adjust accordingly.
        """
        summary = self.coordinator.data.get("summaryCards", {})
        battery = summary.get("battery", {})
        soc = battery.get("stateOfCharge")
        if soc is None:
            return None
        try:
            soc = float(soc)
        except (TypeError, ValueError):
            return None
        # If the value is fractional (0-1), convert to percentage.
        if soc <= 1:
            soc *= 100
        return round(soc, 1)

    @property
    def unit_of_measurement(self):
        """Always return the configured unit, regardless of API data."""
        return "%"


# Region BatteryPower
class BatteryPowerSensor(CoordinatorEntity, SensorEntity):
    """Sensor to report Battery Power from summaryCards in watts."""

    def __init__(self, coordinator, entry_id):
        """Initialize the Battery Power sensor."""
        super().__init__(coordinator)
        self._entry_id = entry_id
        self._attr_name = "Battery Power"
        self._attr_unique_id = f"{entry_id}_battery_power"
        self._attr_device_class = "power"
        self._attr_state_class = "measurement"
        self._attr_unit_of_measurement = "W"

    @property
    def state(self):
        """Return the battery power in watts.

        Assumes battery power is provided as a dictionary with a 'value' key.
        """
        summary = self.coordinator.data.get("summaryCards", {})
        battery = summary.get("battery", {})
        power = battery.get("power")
        if isinstance(power, dict) and "value" in power:
            return round(power["value"], 1)
        return power

    @property
    def unit_of_measurement(self):
        """Always return the configured unit, regardless of API data."""
        return "W"


class BatteryInSensor(CoordinatorEntity, SensorEntity):
    """Sensor for Battery In (charging) – reports the power in Watts when battery is charging."""

    def __init__(self, coordinator, entry_id):
        """Initialize the Battery In sensor."""
        super().__init__(coordinator)
        self._entry_id = entry_id
        self._attr_name = "Battery Power In"
        self._attr_unique_id = f"{entry_id}_battery_power_in"
        self._attr_device_class = "power"
        self._attr_state_class = "measurement"
        self._attr_unit_of_measurement = "W"

    @property
    def state(self):
        """Return battery charging power.

        If the battery power value is positive (charging), return that value; otherwise, return 0.
        """
        summary = self.coordinator.data.get("summaryCards", {})
        battery = summary.get("battery", {})
        power = battery.get("power")
        if isinstance(power, dict) and "value" in power:
            try:
                value = float(power["value"])
            except (TypeError, ValueError):
                return None
        else:
            try:
                value = float(power)
            except (TypeError, ValueError):
                return None

        if value < 0:
            return abs(value)
        return 0

    @property
    def unit_of_measurement(self):
        """Always return the configured unit, regardless of API data."""
        return "W"


class BatteryOutSensor(CoordinatorEntity, SensorEntity):
    """Sensor for Battery Out (discharging) – reports the power in Watts when battery is discharging."""

    def __init__(self, coordinator, entry_id):
        """Initialize the Battery Out sensor."""
        super().__init__(coordinator)
        self._entry_id = entry_id
        self._attr_name = "Battery Power Out"
        self._attr_unique_id = f"{entry_id}_battery_power_out"
        self._attr_device_class = "power"
        self._attr_state_class = "measurement"
        self._attr_unit_of_measurement = "W"

    @property
    def state(self):
        """Return battery discharging power.

        If the battery power value is negative (discharging), return its absolute value; otherwise, return 0.
        """
        summary = self.coordinator.data.get("summaryCards", {})
        battery = summary.get("battery", {})
        power = battery.get("power")
        if isinstance(power, dict) and "value" in power:
            try:
                value = float(power["value"])
            except (TypeError, ValueError):
                return None
        else:
            try:
                value = float(power)
            except (TypeError, ValueError):
                return None

        if value > 0:
            return value
        return 0

    @property
    def unit_of_measurement(self):
        """Always return the configured unit, regardless of API data."""
        return "W"


# Region MarketPrice
class MarketPriceSensor(CoordinatorEntity, SensorEntity):
    """Sensor that displays the latest market price (ct/kWh)."""

    def __init__(self, coordinator, entry_id: str) -> None:
        """Initialize the market price sensor."""
        super().__init__(coordinator)
        self._entry_id = entry_id
        self._attr_name = "Market Price"
        self._attr_unique_id = f"{entry_id}_market_price"
        self._attr_state_class = "measurement"
        self._attr_unit_of_measurement = "ct/kWh"

    @property
    def state(self):
        """Return the latest market price."""
        return self.coordinator.data
