"""Config flow for Nanoleaf Panels integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries

# from homeassistant.components.ssdp import SsdpServiceInfo
# from homeassistant.components.zeroconf import ZeroconfServiceInfo
from homeassistant.components import ssdp, zeroconf
from homeassistant.const import CONF_HOST, CONF_TOKEN
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN
from .nanoleaf_controller import NanoleafController

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> str:
    """Validate the user input allows us to connect."""

    user_input = data[CONF_HOST]  # 192.168.1.23:16021
    if user_input:
        parts = user_input.split(":")
        host = parts[0]
        port = 16021
        if len(parts) > 1 and parts[1]:
            port = parts[1]
        return f"{host}:{port}"

    return user_input


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Nanoleaf Panels."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize config flow."""
        self.nanoleaf_controller: NanoleafController = NanoleafController(self.hass)

    # async def async_step_homekit(
    #     self, discovery_info: zeroconf.ZeroconfServiceInfo
    # ) -> FlowResult:
    #     """Handle a flow initialized by Homekit discovery."""
    #     _LOGGER.info("X async_step_homekit: %s", discovery_info)
    #     return await self.async_step_user()

    async def async_step_ssdp(self, discovery_info: ssdp.SsdpServiceInfo) -> FlowResult:
        """Handle a flow initialized by SSDP discovery."""
        _LOGGER.info("X async_step_ssdp: %s", discovery_info)
        return await self.async_step_user()

    async def async_step_zeroconf(
        self, discovery_info: zeroconf.ZeroconfServiceInfo
    ) -> FlowResult:
        """Handle a flow initialized by Zeroconf discovery."""
        _LOGGER.info("X async_step_zeroconf: %s", discovery_info)
        return await self.async_step_user()

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""

        zc = await zeroconf.async_get_instance(self.hass)

        discovery_info = await ssdp.async_get_discovery_info_by_st(
            self.hass, "ssdp:all"
        )
        _LOGGER.info("X async_step_user: %s %s", zc, discovery_info)

        # zc = await zeroconf.async_get_instance(self.hass)
        # aiozc = await zeroconf.async_get_async_instance(self.hass)

        # discovery_infos = await ssdp.async_get_discovery_info_by_st(
        #     self.hass, "ssdp:all" // "nanoleaf:nl42"
        # )

        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        host = await validate_input(self.hass, user_input)
        if host is not None:
            self.nanoleaf_controller = NanoleafController(self.hass, host)
            return await self.async_step_link()

        return self.async_show_form(step_id="user", data_schema=STEP_USER_DATA_SCHEMA)

    async def async_step_link(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle Nanoleaf link step."""
        if user_input is None:
            return self.async_show_form(step_id="link")

        info = None
        token = await self.nanoleaf_controller.new_token()
        if token is not None:
            info = await self.nanoleaf_controller.get_info()

        if info is not None:
            await self.async_set_unique_id(info["serialNo"])
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=info["name"],
                data={
                    CONF_HOST: self.nanoleaf_controller.host,
                    CONF_TOKEN: self.nanoleaf_controller.token,
                },
            )

        return self.async_show_form(step_id="link", errors={"base": "unknown"})
