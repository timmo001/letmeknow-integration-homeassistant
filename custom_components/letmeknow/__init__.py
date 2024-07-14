"""The LetMeKnow integration."""

from __future__ import annotations

from letmeknowclient import LMKClient, LMKClientType, LMKWSResponseType

from homeassistant.const import CONF_HOST, CONF_PORT, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN, LMKConfigEntry
from .services import async_setup_services

PLATFORMS: list[Platform] = []
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup(
    hass: HomeAssistant,
    config: ConfigType, # pylint: disable=unused-argument
) -> bool:
    """Set up LetMeKnow services."""

    async_setup_services(hass)

    return True


async def async_setup_entry(
    hass: HomeAssistant,
    entry: LMKConfigEntry,
) -> bool:
    """Set up LetMeKnow from a config entry."""

    # Store an instance of the LetMeKnow client in the runtime data
    entry.runtime_data = LMKClient(
        lmk_host=entry.data[CONF_HOST],
        lmk_port=entry.data[CONF_PORT],
        lmk_client_type=LMKClientType.HEADLESS,
        lmk_user_id=f"{LMKClientType.HEADLESS}-homeassistant-{entry.entry_id}",
        session=async_get_clientsession(hass),
    )

    if not (await entry.runtime_data.ws_connect()):
        raise ConfigEntryNotReady(
            translation_domain=DOMAIN,
            translation_key="could_not_connect",
        )

    if (await entry.runtime_data.ws_register()).type != LMKWSResponseType.REGISTER:
        raise ConfigEntryNotReady(
            translation_domain=DOMAIN,
            translation_key="could_not_register",
        )

    hass.async_create_background_task(
        entry.runtime_data.ws_keep_alive(),
        name="LetMeKnow Keep Alive",
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: LMKConfigEntry,
) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
