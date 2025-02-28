import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import OneKomma5GradApi
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class OneKomma5GradOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle an options flow for the 1Komma5Grad integration."""

    def __init__(self, config_entry):
        # Instead of storing the entire config_entry, store just the data we need.
        self._config_entry_data = config_entry.data.copy()
        self._config_entry_options = config_entry.options.copy()
        # Do not store the full config_entry, as that's deprecated.
        # self._config_entry = config_entry  <-- Removed.

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        # Create an API client to fetch available systems.
        access_token = self._config_entry_data.get("access_token")
        refresh_token = self._config_entry_data.get("refresh_token")
        session = async_get_clientsession(self.hass)
        api_client = OneKomma5GradApi(self.hass, access_token)

        # First, fetch available systems from the API.
        try:
            systems_response = await api_client.async_get_systems()
        except Exception as err:
            _LOGGER.error("Error fetching systems: %s", err)
            # Fallback: allow a free-text input.
            available_systems = None
        else:
            systems_list = systems_response.get("data", [])
            available_systems = {}
            for system in systems_list:
                system_id = system.get("id")
                system_name = system.get("systemName", system_id)
                if system_id:
                    available_systems[system_id] = system_name

        # Build a schema that always includes the system_id and a refresh_tokens checkbox.
        # If available_systems is set, use vol.In to create a dropdown.
        if available_systems:
            system_schema = vol.In(available_systems)
        else:
            system_schema = str

        # Use the current system id from options or config data as the default.
        current_system_id = self._config_entry_options.get(
            "system_id", self._config_entry_data.get("system_id", "")
        )

        schema = vol.Schema(
            {
                vol.Required("system_id", default=current_system_id): system_schema,
                vol.Optional("refresh_tokens", default=False): bool,
            }
        )

        if user_input is not None:
            # If refresh is requested, refresh the tokens.
            if user_input.get("refresh_tokens"):
                try:
                    new_token_data = await api_client.async_token_refresh(refresh_token)
                    _LOGGER.debug("Token refreshed successfully")
                    # Update the config entry using the helper method to get the actual entry.
                    if self.config_entry is not None:
                        self.hass.config_entries.async_update_entry(
                            self.config_entry,
                            data={**self._config_entry_data, **new_token_data},
                        )
                    else:
                        _LOGGER.error("Config entry not found for updating tokens")
                except Exception as err:
                    _LOGGER.error("Error refreshing tokens: %s", err)
                    return self.async_show_form(
                        step_id="init",
                        data_schema=schema,
                        errors={"base": "refresh_failed"},
                    )
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(step_id="init", data_schema=schema)
