"""Constants for the 1Komma5Grad integration."""

DOMAIN = "1komma5grad"

# TODO Update with your own urls
OAUTH2_AUTHORIZE = "https://auth.1komma5grad.com/authorize"
OAUTH2_TOKEN = "https://auth.1komma5grad.com/oauth/token"

API_BASE_URL = "https://heartbeat.1komma5grad.com"

SENSOR_CONFIG = {
    "solar_production": {
        "name": "1k5 Solar Production",
        "unit": "W",
        "device_class": "power",
        "state_class": "measurement",
    },
    "battery_in": {
        "name": "1k5 Battery In",
        "unit": "W",
        "device_class": "power",
        "state_class": "measurement",
    },
    "battery_out": {
        "name": "1k5 Battery Out",
        "unit": "W",
        "device_class": "power",
        "state_class": "measurement",
    },
    "battery_charge": {
        "name": "1k5 Battery Charge",
        "unit": "%",
        "device_class": "battery",
        "state_class": "measurement",
    },
    "battery_energy": {
        "name": "1k5 Battery Energy",
        "unit": "kWh",
        "device_class": "energy",
        "state_class": "measurement",
        "battery_capacity": 15.52,  # Example capacity in kWh.
    },
    "grid_feed_in": {
        "name": "1k5 Grid Feed-In",
        "unit": "W",
        "device_class": "power",
        "state_class": "measurement",
    },
    "grid_consumption": {
        "name": "1k5 Grid Consumption",
        "unit": "W",
        "device_class": "power",
        "state_class": "measurement",
    },
    "house_consumption": {
        "name": "1k5 House Consumption",
        "unit": "W",
        "device_class": "power",
        "state_class": "measurement",
    },
    "market_price": {
        "name": "1k5 Market Price",
        "unit": "EUR/kWh",  # Value is converted from ct/kWh in the sensor.
        "state_class": "measurement",
    },
}
