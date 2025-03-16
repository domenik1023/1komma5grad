"""The 1Komma5Grad integration."""

from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from . import api
from .const import DOMAIN

# Define supported platforms.
_PLATFORMS: list[Platform] = [Platform.SENSOR]

# Define a type alias for our ConfigEntry if desired.
# type OneKommaFive_NameConfigEntry = ConfigEntry[api.AsyncConfigEntryAuth]

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up 1Komma5Grad from a config entry."""
    # --- Extract required data ---
    access_token = config_entry.data.get("access_token")
    refresh_token = config_entry.data.get("refresh_token")
    system_id = config_entry.options.get(
        "system_id", config_entry.data.get("system_id")
    )
    if not access_token or not system_id or not refresh_token:
        _LOGGER.error(
            "Missing access token, refresh token or system id or in config entry"
        )
        return False

    async def async_refresh_tokens():
        """Call API to refresh tokens and update the config entry."""
        new_token_data = await api_client.async_token_refresh(refresh_token)
        if new_token_data:
            hass.config_entries.async_update_entry(
                config_entry,
                data={**config_entry.data, **new_token_data},
            )
            api_client.access_token = new_token_data.get("access_token")
        return new_token_data

    # --- Create the API client ---
    api_client = api.OneKomma5GradApi(hass, access_token)

    # Check if the token is still valid.
    try:
        await api_client.async_get_live_overview(system_id)
    except Exception as err:
        _LOGGER.info("Access token invalid or expired, refreshing tokens: %s", err)
        new_token_data = await api_client.async_token_refresh(refresh_token)
        # Update the config entry with the new token data.
        hass.config_entries.async_update_entry(
            config_entry,
            data={**config_entry.data, **new_token_data},
        )
        # Update the API client’s access token.
        api_client.access_token = new_token_data.get("access_token")

    # --- Create DataUpdateCoordinator for Live Overview ---
    coordinator = DataUpdateCoordinator(
        hass,
        logger=_LOGGER,
        name="1Komma5Grad Live Overview",
        update_method=lambda: api_client.async_get_live_overview(system_id),
        update_interval=timedelta(seconds=30),
    )
    await coordinator.async_config_entry_first_refresh()

    # --- Create DataUpdateCoordinator for Market Price ---
    market_price_coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="1Komma5Grad Market Price",
        update_method=lambda: api_client.async_get_market_price(system_id),
        update_interval=timedelta(seconds=30),  # adjust as needed
    )
    await market_price_coordinator.async_config_entry_first_refresh()

    # --- Create Token Refresh via Manually Scheduled Task ---
    async def token_refresh_task(now):
        try:
            await async_refresh_tokens()  # your async refresh function
        except Exception as err:
            _LOGGER.error("Error in scheduled token refresh: %s", err)

    async_track_time_interval(hass, token_refresh_task, timedelta(seconds=43200))

    # --- Store integration data ---
    hass.data.setdefault(DOMAIN, {})[config_entry.entry_id] = {
        "coordinator": coordinator,
        "market_price_coordinator": market_price_coordinator,
        "token_refresh_task": token_refresh_task,
        "api": api_client,
        # You can add additional coordinators here later
    }

    # --- Forward setup to sensor platform ---
    await hass.config_entries.async_forward_entry_setups(config_entry, ["sensor"])

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, _PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok
