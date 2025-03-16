"""API for 1Komma5Grad bound to Home Assistant OAuth."""

from asyncio import run_coroutine_threadsafe
from datetime import datetime, timezone
import logging

from aiohttp import ClientSession

from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_entry_oauth2_flow
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import API_BASE_URL, OAUTH2_TOKEN

# TODO the following two API examples are based on our suggested best practices
# for libraries using OAuth2 with requests or aiohttp. Delete the one you won't use.
# For more info see the docs at https://developers.home-assistant.io/docs/api_lib_auth/#oauth2.

_LOGGER = logging.getLogger(__name__)


class ConfigEntryAuth:
    """Provide 1Komma5Grad authentication tied to an OAuth2 based config entry."""

    def __init__(
        self,
        hass: HomeAssistant,
        oauth_session: config_entry_oauth2_flow.OAuth2Session,
    ) -> None:
        """Initialize 1Komma5Grad Auth."""
        self.hass = hass
        self.session = oauth_session
        super().__init__(self.session.token)

    def refresh_tokens(self) -> str:
        """Refresh and return new 1Komma5Grad tokens using Home Assistant OAuth2 session."""
        run_coroutine_threadsafe(
            self.session.async_ensure_token_valid(), self.hass.loop
        ).result()

        return self.session.token["access_token"]


class AsyncConfigEntryAuth:
    """Provide 1Komma5Grad authentication tied to an OAuth2 based config entry."""

    def __init__(
        self,
        websession: ClientSession,
        oauth_session: config_entry_oauth2_flow.OAuth2Session,
    ) -> None:
        """Initialize 1Komma5Grad auth."""
        super().__init__(websession)
        self._oauth_session = oauth_session

    async def async_get_access_token(self) -> str:
        """Return a valid access token."""
        await self._oauth_session.async_ensure_token_valid()

        return self._oauth_session.token["access_token"]


class OneKomma5GradApi:
    """Client for the 1Komma5Grad API."""

    def __init__(self, hass, access_token: str):
        self.hass = hass
        self.access_token = access_token
        self.session = async_get_clientsession(hass)

    async def async_get_data(self, endpoint: str) -> dict:
        """Make an authenticated GET request to the API."""
        headers = {"Authorization": f"Bearer {self.access_token}"}
        async with self.session.get(endpoint, headers=headers) as response:
            response.raise_for_status()
            return await response.json()

    async def async_post_data(self, endpoint: str, data: dict) -> dict:
        """Make an authenticated POST request to the API."""
        headers = {"Authorization": f"Bearer {self.access_token}"}
        async with self.session.post(endpoint, json=data, headers=headers) as response:
            response.raise_for_status()
            return await response.json()

    async def async_token_refresh(self, refresh_token: str) -> dict:
        """Refresh token using the refresh token and update the config entry with new token data."""
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": "zJTm6GFGM5zHcmpl07xTsi6MP0TwRAw6",
        }
        async with self.session.post(OAUTH2_TOKEN, json=payload) as response:
            response.raise_for_status()
            token_data = await response.json()
            _LOGGER.debug("Token refresh response: %s", token_data)

            # Update the config entry with the new token data.
            # This requires that self._config_entry was saved during __init__.
            return token_data

    async def async_get_live_overview(self, system_id: str) -> dict:
        """Fetch live overview data from the API."""
        headers = {"Authorization": f"Bearer {self.access_token}"}
        async with self.session.get(
            f"{API_BASE_URL}/api/v3/systems/{system_id}/live-overview", headers=headers
        ) as response:
            response.raise_for_status()
            _LOGGER.debug("Get Liveoverview - Response JSON: %s", await response.json())
            return await response.json()

    async def async_get_systems(self) -> dict:
        """Fetch all systems."""
        headers = {"Authorization": f"Bearer {self.access_token}"}
        async with self.session.get(
            f"{API_BASE_URL}/api/v2/systems", headers=headers
        ) as response:
            response.raise_for_status()
            _LOGGER.debug("Get System - Response JSON: %s", await response.json())
            return await response.json()

    # TODO I don't know if this is the correct value, can only check later.
    async def async_get_market_price(self, system_id: str) -> dict:
        """Fetch market prices for the system."""
        headers = {"Authorization": f"Bearer {self.access_token}"}
        async with self.session.get(
            f"{API_BASE_URL}/api/v1/systems/{system_id}/charts/market-prices?from={datetime.now().strftime('%Y-%m-%d')}&resolution=1h",
            headers=headers,
        ) as response:
            response.raise_for_status()
            _LOGGER.debug("Get Market Price - Response JSON: %s", await response.json())
            data = await response.json()
            energy_market = data.get("energyMarket", {})
            data_dict = energy_market.get("data", {})
            if not data_dict:
                return None
            # Timestamps are ISO8601 strings that sort lexicographically.

            sorted_keys = sorted(data_dict.keys())
            now = datetime.now(
                timezone.utc
            )  # .strftime("%Y-%m-%dT%H:%MZ")  # Make now timezone-aware in UTC

            for i, ts in enumerate(sorted_keys):
                # Convert timestamp string to a timezone-aware datetime object.
                ts_dt = datetime.fromisoformat(ts)
                if now < ts_dt:
                    # If this timestamp is in the future, choose the previous one if it exists.
                    if ts_dt > now:
                        # If now is before the first timestamp, return the first price.
                        _LOGGER.debug("Current Price: %s", data_dict[ts].get("price"))
                        return data_dict[sorted_keys[0]].get("price")
            # If now is later than all timestamps, return the last one.
            _LOGGER.debug(
                "Current Price 00:00: %s", {data_dict[sorted_keys[-1]].get("price")}
            )
            return data_dict[sorted_keys[-1]].get("price")
