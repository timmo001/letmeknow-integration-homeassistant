"""Constants for the LetMeKnow integration."""

from typing import Final

from letmeknowclient import LMKClient

from homeassistant.config_entries import ConfigEntry

DOMAIN = "letmeknow"

CONF_DEFAULT_PORT: Final[int] = 8080

type LMKConfigEntry = ConfigEntry[LMKClient] # pylint: disable=unsubscriptable-object
