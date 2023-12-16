"""The Nanoleaf Panels integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_TOKEN, Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .nanoleaf_controller import NanoleafController

PLATFORMS: list[Platform] = [Platform.LIGHT]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Nanoleaf Panels from a config entry."""

    nanoleaf_controller = NanoleafController(
        hass,
        entry.data[CONF_HOST],
        entry.data[CONF_TOKEN],
    )
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = nanoleaf_controller

    # hass.config_entries.async_setup_platforms(entry, PLATFORMS)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
