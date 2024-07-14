"""Config flow for LetMeKnow integration."""

from __future__ import annotations

import logging
from typing import Any
from uuid import uuid4

from letmeknowclient import LMKClient, LMKClientType
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import CONF_DEFAULT_PORT, DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_PORT, default=CONF_DEFAULT_PORT): int,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    lmk_client = LMKClient(
        lmk_host=data[CONF_HOST],
        lmk_port=data[CONF_PORT],
        lmk_client_type=LMKClientType.HEADLESS,
        lmk_user_id=f"{LMKClientType.HEADLESS}-homeassistant-{uuid4()}",
        session=async_get_clientsession(hass),
    )

    if not (await lmk_client.ws_connect()):
        raise CannotConnect

    return {
        "title": data[CONF_HOST],
    }


class LMKConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for LetMeKnow."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                info = await validate_input(
                    self.hass,
                    user_input,
                )
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(
                    title=info["title"],
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""
