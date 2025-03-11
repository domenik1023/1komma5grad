import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, SENSOR_CONFIG

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up sensor platform for 1Komma5Grad."""
    entry_id = config_entry.entry_id
    coordinator = hass.data[DOMAIN][entry_id]["coordinator"]
    market_coordinator = hass.data[DOMAIN][entry_id]["market_price_coordinator"]

    sensors = []

    # Create Battery Sensors.
    sensors.append(BatteryInSensor(coordinator, entry_id))
    sensors.append(BatteryOutSensor(coordinator, entry_id))
    sensors.append(BatteryChargeSensor(coordinator, entry_id))
    sensors.append(BatteryEnergySensor(coordinator, entry_id))

    # Create solar panel sensors.
    sensors.append(SolarPanelSensor(coordinator, entry_id))

    # Create grid sensors.
    sensors.append(GridFeedInSensor(coordinator, entry_id))
    sensors.append(GridConsumptionSensor(coordinator, entry_id))

    # House Sensors.
    sensors.append(HouseConsumptionSensor(coordinator, entry_id))

    # Create Market Price sensors.
    sensors.append(MarketPriceSensor(market_coordinator, entry_id))

    async_add_entities(sensors, update_before_add=True)


class BatteryInSensor(CoordinatorEntity, SensorEntity):
    """Sensor for Battery In (charging).

    Reports the charging power (W) when the battery is receiving power.
    """

    def __init__(self, coordinator, entry_id):
        """Initialize the Battery In sensor."""
        super().__init__(coordinator)
        conf = SENSOR_CONFIG.get("battery_in", {})
        self._entry_id = entry_id
        self._attr_name = conf.get("name")
        self._attr_unique_id = f"{entry_id}_battery_in"
        self._attr_device_class = conf.get("device_class")
        self._attr_state_class = conf.get("state_class")
        self._attr_unit_of_measurement = conf.get("unit")

    @property
    def device_info(self):
        """Return device information for the battery group."""
        return {
            "identifiers": {(DOMAIN, self._entry_id, "battery")},
            "name": "1Komma5Grad Battery",
            "manufacturer": "1Komma5Grad",
            "model": "Battery",
        }

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
            return value * -1
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
        conf = SENSOR_CONFIG.get("battery_out", {})
        self._entry_id = entry_id
        self._attr_name = conf.get("name")
        self._attr_unique_id = f"{entry_id}_battery_out"
        self._attr_device_class = conf.get("device_class")
        self._attr_state_class = conf.get("state_class")
        self._attr_unit_of_measurement = conf.get("unit")

    @property
    def device_info(self):
        """Return device information for the battery group."""
        # Use the same device identifiers as BatteryInSensor so they appear under one device.
        return {
            "identifiers": {(DOMAIN, self._entry_id, "battery")},
            "name": "1Komma5Grad Battery",
            "manufacturer": "1Komma5Grad",
            "model": "Battery",
        }

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


class BatteryChargeSensor(CoordinatorEntity, SensorEntity):
    """Sensor for current battery charge as a percentage."""

    def __init__(self, coordinator, entry_id):
        super().__init__(coordinator)
        conf = SENSOR_CONFIG.get("battery_charge", {})
        self._entry_id = entry_id
        self._attr_name = conf.get("name")
        self._attr_unique_id = f"{entry_id}_battery_charge"
        self._attr_device_class = conf.get("device_class")
        self._attr_state_class = conf.get("state_class")
        self._attr_unit_of_measurement = conf.get("unit")

    @property
    def device_info(self):
        """Return device info so that this sensor is grouped under the Battery device."""
        return {
            "identifiers": {(DOMAIN, self._entry_id, "battery")},
            "name": "1Komma5Grad Battery",
            "manufacturer": "1Komma5Grad",
            "model": "Battery",
        }

    @property
    def state(self):
        """Return the battery charge percentage.

        Assumes API data is in:
          coordinator.data["summaryCards"]["battery"]["stateOfCharge"]
        and is given as a fraction (e.g. 0.7).
        """
        summary = self.coordinator.data.get("summaryCards", {})
        battery = summary.get("battery", {})
        soc = battery.get("stateOfCharge")
        try:
            soc = float(soc)
        except (TypeError, ValueError):
            return None
        # Convert fraction to percentage.
        return round(soc * 100, 1)

    @property
    def unit_of_measurement(self):
        """Always return the configured unit, regardless of API data."""
        return "%"


class BatteryEnergySensor(CoordinatorEntity, SensorEntity):
    """Sensor for current battery energy (kWh) calculated from the charge and battery capacity."""

    def __init__(self, coordinator, entry_id):
        super().__init__(coordinator)
        conf = SENSOR_CONFIG.get("battery_energy", {})
        self._entry_id = entry_id
        self._attr_name = conf.get("name")
        self._attr_unique_id = f"{entry_id}_battery_energy"
        self._attr_device_class = conf.get("device_class")
        self._attr_state_class = conf.get("state_class")
        self._attr_unit_of_measurement = conf.get("unit")
        self._battery_capacity = conf.get("battery_capacity")

    @property
    def device_info(self):
        """Return device info so that this sensor is grouped under the Battery device."""
        return {
            "identifiers": {(DOMAIN, self._entry_id, "battery")},
            "name": "1Komma5Grad Battery",
            "manufacturer": "1Komma5Grad",
            "model": "Battery",
        }

    @property
    def state(self):
        """Calculate and return the current battery energy in kWh.

        This is computed as:

            current_energy = state_of_charge * battery_capacity

        Where:
          - state_of_charge is assumed to be a fraction from
            coordinator.data["summaryCards"]["battery"]["stateOfCharge"]
          - battery_capacity is provided in sensor_conf.
        """
        capacity = self._battery_capacity
        if capacity is None:
            _LOGGER.error("Battery capacity is not configured")
            return None

        summary = self.coordinator.data.get("summaryCards", {})
        battery = summary.get("battery", {})
        soc = battery.get("stateOfCharge")
        try:
            soc = float(soc)
        except (TypeError, ValueError):
            return None

        energy = soc * capacity
        return round(energy, 2)

    @property
    def unit_of_measurement(self):
        """Always return the configured unit, regardless of API data."""
        return "kWh"


class SolarPanelSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Solar Panel sensor for 1Komma5Grad."""

    def __init__(self, coordinator, entry_id):
        """Initialize the Solar Panel sensor."""
        super().__init__(coordinator)
        conf = SENSOR_CONFIG.get("solar_production", {})
        self._entry_id = entry_id
        self._attr_name = conf.get("name")
        self._attr_unique_id = f"{entry_id}_solar_production"
        self._attr_device_class = conf.get("device_class", "power")
        self._attr_state_class = conf.get("state_class", "measurement")
        self._attr_unit_of_measurement = conf.get("unit", "W")

    @property
    def device_info(self):
        """Return device information for the solar panel group."""
        return {
            "identifiers": {(DOMAIN, self._entry_id, "solarpanel")},
            "name": "1Komma5Grad Solar Panel",
            "manufacturer": "1Komma5Grad",
            "model": "Solar Panel",
        }

    @property
    def state(self):
        """Return the solar panel sensor state."""
        live_data = self.coordinator.data.get("liveHeroView", {})
        sensor_data = live_data.get("production", {})
        if sensor_data and isinstance(sensor_data, dict) and "value" in sensor_data:
            return sensor_data["value"]
        return sensor_data

    @property
    def unit_of_measurement(self):
        """Return the configured unit."""
        return "W"


class GridFeedInSensor(CoordinatorEntity, SensorEntity):
    """Sensor for Grid Feed-In from liveHeroView."""

    def __init__(self, coordinator, entry_id):
        super().__init__(coordinator)
        conf = SENSOR_CONFIG.get("grid_feed_in", {})
        self._entry_id = entry_id
        self._attr_name = conf.get("name")
        self._attr_unique_id = f"{entry_id}_grid_feed_in"
        self._attr_device_class = conf.get("device_class")
        self._attr_state_class = conf.get("state_class")
        self._attr_unit_of_measurement = conf.get("unit")

    @property
    def device_info(self):
        """Return device information to group this sensor under the Grid device."""
        return {
            "identifiers": {(DOMAIN, self._entry_id, "grid")},
            "name": "1Komma5Grad Grid",
            "manufacturer": "1Komma5Grad",
            "model": "Grid",
        }

    @property
    def state(self):
        """Return the grid feed-in power value from liveHeroView."""
        live_data = self.coordinator.data.get("liveHeroView", {})
        sensor_data = live_data.get("gridFeedIn")
        if sensor_data and isinstance(sensor_data, dict) and "value" in sensor_data:
            return sensor_data["value"]
        return sensor_data

    @property
    def unit_of_measurement(self):
        """Always return the configured unit, regardless of API data."""
        return "W"


class GridConsumptionSensor(CoordinatorEntity, SensorEntity):
    """Sensor for Grid Consumption from liveHeroView."""

    def __init__(self, coordinator, entry_id):
        super().__init__(coordinator)
        conf = SENSOR_CONFIG.get("grid_consumption", {})
        self._entry_id = entry_id
        self._attr_name = conf.get("name")
        self._attr_unique_id = f"{entry_id}_grid_consumption"
        self._attr_device_class = conf.get("device_class")
        self._attr_state_class = conf.get("state_class")
        self._attr_unit_of_measurement = conf.get("unit")

    @property
    def device_info(self):
        """Return device information to group this sensor under the same Grid device."""
        return {
            "identifiers": {(DOMAIN, self._entry_id, "grid")},
            "name": "1Komma5Grad Grid",
            "manufacturer": "1Komma5Grad",
            "model": "Grid",
        }

    @property
    def state(self):
        """Return the grid consumption power value from liveHeroView."""
        live_data = self.coordinator.data.get("liveHeroView", {})
        sensor_data = live_data.get("gridConsumption")
        if sensor_data and isinstance(sensor_data, dict) and "value" in sensor_data:
            return sensor_data["value"]
        return sensor_data

    @property
    def unit_of_measurement(self):
        """Always return the configured unit, regardless of API data."""
        return "W"


class HouseConsumptionSensor(CoordinatorEntity, SensorEntity):
    """Sensor that displays the current household consumption."""

    def __init__(self, coordinator, entry_id):
        super().__init__(coordinator)
        conf = SENSOR_CONFIG.get("house_consumption", {})
        self._entry_id = entry_id
        self._attr_name = conf.get("name")
        self._attr_unique_id = f"{entry_id}_house_consumption"
        self._attr_device_class = conf.get("device_class")
        self._attr_state_class = conf.get("state_class")
        self._attr_unit_of_measurement = conf.get("unit")

    @property
    def device_info(self):
        """Return device information to group this sensor under the House device."""
        return {
            "identifiers": {(DOMAIN, self._entry_id, "house")},
            "name": "1Komma5Grad House",
            "manufacturer": "1Komma5Grad",
            "model": "House Consumption",
        }

    @property
    def state(self):
        """Return the current household consumption from the API data.

        Assumes data is located at summaryCards['household']['power'].
        """
        summary = self.coordinator.data.get("summaryCards", {})
        household = summary.get("household", {})
        power = household.get("power")
        if power and isinstance(power, dict) and "value" in power:
            try:
                return float(power["value"])
            except (TypeError, ValueError):
                _LOGGER.error("Invalid household consumption value: %s", power)
                return None
        return None

    @property
    def unit_of_measurement(self):
        """Always return the configured unit, regardless of API data."""
        return "W"


class MarketPriceSensor(CoordinatorEntity, SensorEntity):
    """Sensor that displays the latest market price (ct/kWh) as a heartbeat device."""

    def __init__(self, coordinator, entry_id):
        super().__init__(coordinator)
        conf = SENSOR_CONFIG.get("market_price", {})
        self._entry_id = entry_id
        self._attr_name = conf.get("name")
        self._attr_unique_id = f"{entry_id}_market_price"
        self._attr_state_class = conf.get("state_class", "measurement")
        self._attr_unit_of_measurement = conf.get("unit")

    @property
    def device_info(self):
        """Return device information to group this sensor as a heartbeat device."""
        return {
            "identifiers": {(DOMAIN, self._entry_id, "heartbeat")},
            "name": "1Komma5Grad Heartbeat",
            "manufacturer": "1Komma5Grad",
            "model": "Heartbeat Device",
        }

    @property
    def state(self):
        """Return the latest market price converted to EUR/kWh.

        Assumes the coordinator returns a value in ct/kWh.
        """
        raw_value = self.coordinator.data
        if raw_value is None:
            return None
        try:
            # Convert from ct/kWh to EUR/kWh by dividing by 100
            eur_value = float(raw_value) / 100
            return round(eur_value, 3)
        except (TypeError, ValueError):
            _LOGGER.error("Invalid market price data: %s", raw_value)
            return None

    @property
    def unit_of_measurement(self):
        """Always return the configured unit, regardless of API data."""
        return "EUR/kWh"
