"""Config flow for 1Komma5Grad."""

import base64
import hashlib
import logging
import secrets
from urllib.parse import urlencode

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.components import persistent_notification
from homeassistant.helpers import config_entry_oauth2_flow
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import OneKomma5GradApi
from .const import DOMAIN, OAUTH2_AUTHORIZE, OAUTH2_TOKEN
from .options_flow import OneKomma5GradOptionsFlowHandler


def generate_code_verifier() -> str:
    """Generate a secure random code verifier string.

    Returns:
        str: A URL-safe string to be used as a code verifier in PKCE.

    """
    return secrets.token_urlsafe(32)


def generate_code_challenge(verifier: str) -> str:
    """Generate a code challenge from the provided code verifier using SHA256 and base64 encoding.

    Args:
        verifier (str): The code verifier string.

    Returns:
        str: A URL-safe base64-encoded string without padding, representing the code challenge.

    """
    digest = hashlib.sha256(verifier.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode("utf-8")


def generate_nonce() -> str:
    """Generate a secure random nonce string.

    Returns:
        str: A URL-safe string to be used as a nonce.

    """
    return secrets.token_urlsafe(16)


class OAuth2FlowHandler(
    config_entry_oauth2_flow.AbstractOAuth2FlowHandler, domain=DOMAIN
):
    """Config flow to handle 1Komma5Grad OAuth2 authentication."""

    DOMAIN = DOMAIN

    def __init__(self):
        # Generate once per flow instance and store in self.
        # You might also persist these to disk if you expect the flow to be interrupted.
        self.code_verifier = generate_code_verifier()
        self.oauth_url = None

    @property
    def logger(self) -> logging.Logger:
        """Return logger."""
        return logging.getLogger(__name__)

    @staticmethod
    def async_get_options_flow(config_entry):
        return OneKomma5GradOptionsFlowHandler(config_entry)

    async def async_generate_authorize_url(self):
        params = {
            "response_type": "code",
            "client_id": "zJTm6GFGM5zHcmpl07xTsi6MP0TwRAw6",
            "redirect_uri": "io.onecommafive.my.production.app://auth.1komma5grad.com/android/io.onecommafive.my.production.app/callback",  # Update this accordingly
            "state": self.flow_id,  # or another valid state value
            "audience": "https://1komma5grad.com/api",
            "auth0Client": "eyJuYW1lIjoiYXV0aDAtZmx1dHRlciIsImVudiI6eyJhbmRyb2lkIjoiMzMifSwidmVyc2lvbiI6IjEuNy4yIn0=",
            "nonce": generate_nonce(),
            "code_challenge": generate_code_challenge(self.code_verifier),
            "code_challenge_method": "S256",
            "scope": "openid profile email offline_access",
        }
        auth_url = f"{OAUTH2_AUTHORIZE}?{urlencode(params)}"
        self.logger.debug(
            "\nOAuth URL: %s\nParameter: %s\nVerifier: %s",
            auth_url,
            params,
            self.code_verifier,
        )
        return auth_url

    async def async_step_user(self, user_input=None):
        """Generating the Input Field and Notification for 1Komma5Grad Login."""
        if user_input is None:
            # Generate OAuth URL only once per flow.
            if not self.oauth_url:
                self.oauth_url = await self.async_generate_authorize_url()

            # Create a persistent notification with the clickable link
            persistent_notification.async_create(
                self.hass,
                f"Click [here]({self.oauth_url}) to open the authorization page in your browser. "
                "After logging in, copy the code from the redirected URL and paste it below.",
                title="1Komma5Grad OAuth",
                notification_id="1komma5grad_oauth",
            )
            return self.async_show_form(
                data_schema=vol.Schema(
                    {
                        vol.Required("Authorization Code"): str,
                    }
                ),
                description_placeholders="After you authorize, copy the code from the URL and paste it below.",
            )
        # Dismiss the notification if the user has provided the code
        persistent_notification.async_dismiss(self.hass, "1komma5grad_oauth")
        self.logger.debug(user_input)
        code = user_input["Authorization Code"]
        token_data = await self._exchange_code_for_token(code)
        token_data["auth_implementation"] = DOMAIN

        # Now that you have a valid token, create an API client.
        self.api = OneKomma5GradApi(self.hass, token_data["access_token"])
        self._refresh_token = token_data["refresh_token"]

        # Move to the system selection step.
        return await self.async_step_system()

    async def _exchange_code_for_token(self, code: str) -> dict:
        """Exchange the authorization code for an access token."""
        session = async_get_clientsession(self.hass)
        token_url = OAUTH2_TOKEN
        payload = {
            "grant_type": "authorization_code",
            "client_id": "zJTm6GFGM5zHcmpl07xTsi6MP0TwRAw6",
            "code": code,
            "redirect_uri": "io.onecommafive.my.production.app://auth.1komma5grad.com/android/io.onecommafive.my.production.app/callback",
            "code_verifier": self.code_verifier,
        }

        async with session.post(token_url, json=payload) as response:
            result = await response.json()
            if response.status != 200:
                self.logger.info("Token exchange failed: %s", result)
                raise Exception("Token exchange failed: %s", result)
            return result

    async def async_oauth_create_entry(self, data: dict) -> config_entries.ConfigEntry:
        data["auth_implementation"] = DOMAIN  # Add the required key
        return self.async_create_entry(title="1Komma5Grad Account", data=data)

    async def async_step_system(self, user_input=None):
        """Step to select a system to monitor."""
        if user_input is None:
            # Fetch available systems from the API.
            try:
                response = await self.api.async_get_systems()  # See API client below.
            except Exception:
                return self.async_abort(reason="Cannot Fetch Systems!")

            # Build a dict of system_id: system_name for the dropdown.
            systems = response.get("data", [])
            if not systems:
                return self.async_abort(reason="No Systems Found!")
            self.system_options = {
                system["id"]: system["systemName"] for system in systems
            }

            schema = vol.Schema(
                {
                    vol.Required("System ID"): vol.In(self.system_options),
                }
            )
            return self.async_show_form(step_id="system", data_schema=schema)

        # User has selected a system.
        selected_system = user_input["System ID"]
        # You can add the system id to your token data or separate config data.
        token_data = {
            "access_token": self.api.access_token,
            "refresh_token": self._refresh_token,
            "system_id": selected_system,
            "auth_implementation": DOMAIN,
        }
        return self.async_create_entry(
            title="1Komma5Grad Account",
            description=f"Connected as {self.system_options[selected_system]}",
            data=token_data,
        )
