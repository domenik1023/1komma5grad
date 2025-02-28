"""Constants for the 1Komma5Grad integration."""

DOMAIN = "1komma5grad"

# TODO Update with your own urls
OAUTH2_AUTHORIZE = "https://auth.1komma5grad.com/authorize"
OAUTH2_TOKEN = "https://auth.1komma5grad.com/oauth/token"

API_BASE_URL = "https://heartbeat.1komma5grad.com/"

SENSOR_CONFIG = {
    "consumption": {
        "name": "House Consumption",
        "unit": "W",  # Customize unit here
        "device_class": "power",
        "state_class": "measurement",
    },
    "gridFeedIn": {
        "name": "Grid Feed-In",
        "unit": "W",
        "device_class": "power",
        "state_class": "measurement",
    },
    "gridConsumption": {
        "name": "Grid Consumption",
        "unit": "W",
        "device_class": "power",
        "state_class": "measurement",
    },
    "production": {
        "name": "Solar Production",
        "unit": "W",
        "device_class": "power",
        "state_class": "measurement",
    },
    # Add additional sensors if needed.
}

INTEGRATION_SENSORS = {
    "consumption": {
        "key": "consumption",
        "name": "Total Consumption Energy",
        "unit": "kWh",
    },
    "production": {
        "key": "production",
        "name": "Total Production Energy",
        "unit": "kWh",
    },
    "gridFeedIn": {
        "key": "gridFeedIn",
        "name": "Total Grid Feed-In Energy",
        "unit": "kWh",
    },
    # Add other integration sensors as needed.
}
