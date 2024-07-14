"""The LetMeKnow services."""

from __future__ import annotations

from functools import partial
from typing import Final

from letmeknowclient import LMKClient, LMKNotification, LMKNotificationImage
import voluptuous as vol

from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import (
    HomeAssistant,
    ServiceCall,
    ServiceResponse,
    SupportsResponse,
    callback,
)
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import selector

from .const import DOMAIN, LMKConfigEntry

ATTR_CONFIG_ENTRY: Final[str] = "config_entry"
ATTR_TITLE: Final[str] = "title"
ATTR_SUBTITLE: Final[str] = "subtitle"
ATTR_CONTENT: Final[str] = "content"
ATTR_IMAGE_URL: Final[str] = "image_url"
ATTR_TARGETS: Final[str] = "targets"
ATTR_TIMEOUT: Final[str] = "timeout"

SEND_NOTIFICATION_SERVICE_NAME: Final[str] = "send_notification"
SEND_NOTIFICATION_SERVICE_SCHEMA: Final = vol.Schema(
    {
        vol.Required(ATTR_CONFIG_ENTRY): selector.ConfigEntrySelector(
            {
                "integration": DOMAIN,
            }
        ),
        vol.Optional(ATTR_TITLE): str,
        vol.Optional(ATTR_SUBTITLE): str,
        vol.Optional(ATTR_CONTENT): str,
        vol.Optional(ATTR_IMAGE_URL): str,
        vol.Optional(ATTR_TIMEOUT): int,
        vol.Optional(ATTR_TARGETS): list[str],
    }
)


def __get_lmk_client(
    hass: HomeAssistant,
    call: ServiceCall,
) -> LMKClient:
    """Get the coordinator from the entry."""
    entry_id: str = call.data[ATTR_CONFIG_ENTRY]
    entry: LMKConfigEntry | None = hass.config_entries.async_get_entry(entry_id)

    if not entry:
        raise ServiceValidationError(
            translation_domain=DOMAIN,
            translation_key="invalid_config_entry",
            translation_placeholders={
                "config_entry": entry_id,
            },
        )
    if entry.state != ConfigEntryState.LOADED:
        raise ServiceValidationError(
            translation_domain=DOMAIN,
            translation_key="unloaded_config_entry",
            translation_placeholders={
                "config_entry": entry.title,
            },
        )

    return entry.runtime_data


async def __send_notification(
    call: ServiceCall,
    *,
    hass: HomeAssistant,
) -> ServiceResponse:
    """Send a notification."""
    lmk_client = __get_lmk_client(hass, call)

    notification_response = await lmk_client.ws_send_notification(
        LMKNotification(
            title=call.data.get(ATTR_TITLE),
            subtitle=call.data.get(ATTR_SUBTITLE),
            content=call.data.get(ATTR_CONTENT),
            image=LMKNotificationImage(
                url=call.data[ATTR_IMAGE_URL],
            )
            if call.data.get(ATTR_IMAGE_URL)
            else None,
            timeout=call.data.get(ATTR_TIMEOUT),
        ),
        targets=call.data.get(ATTR_TARGETS),
    )

    return notification_response.to_dict()


@callback
def async_setup_services(hass: HomeAssistant) -> None:
    """Set up LetMeKnow services."""

    hass.services.async_register(
        DOMAIN,
        SEND_NOTIFICATION_SERVICE_NAME,
        partial(__send_notification, hass=hass),
        schema=SEND_NOTIFICATION_SERVICE_SCHEMA,
        supports_response=SupportsResponse.ONLY,
    )
