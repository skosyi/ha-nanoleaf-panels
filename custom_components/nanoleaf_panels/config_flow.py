"""Config flow for Nanoleaf Panels integration."""
from __future__ import annotations

import logging
from typing import Any
from urllib.parse import urlparse

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

    # 2023-12-12 20:30:16.273 INFO (MainThread) [custom_components.nanoleaf_panels.config_flow] X async_step_ssdp: SsdpServiceInfo(
    # ssdp_usn='uuid:3d703f8a-0160-44fc-a77e-4404cda23136',
    # ssdp_st='nanoleaf:nl42',
    # upnp={'UDN': 'uuid:3d703f8a-0160-44fc-a77e-4404cda23136'},
    # ssdp_location='http://192.168.1.23:16021',
    # ssdp_nt=None,
    # ssdp_udn='uuid:3d703f8a-0160-44fc-a77e-4404cda23136',
    # ssdp_ext='',
    # ssdp_server=None,
    # ssdp_headers={
    #   'S': 'uuid:3d703f8a-0160-44fc-a77e-4404cda23136',
    #   'Ext': '',
    #   'Cache-Control': 'no-cache="Ext",
    #   max-age = 60',
    #   'ST': 'nanoleaf:nl42',
    #   'USN': 'uuid:3d703f8a-0160-44fc-a77e-4404cda23136',
    #   'Location': 'http://192.168.1.23:16021',
    #   'nl-deviceid': '1A:25:70:12:4F:A6',
    #   'nl-devicename': 'Shapes 07E7',
    #   '_host': '192.168.1.23',
    #   '_udn': 'uuid:3d703f8a-0160-44fc-a77e-4404cda23136',
    #   '_location_original': 'http://192.168.1.23:16021',
    #   'location': 'http://192.168.1.23:16021',
    #   '_timestamp': datetime.datetime(2023, 12, 12, 20, 28, 25, 696262),
    #   '_remote_addr': ('192.168.1.23', 1900),
    #   '_port': 1900,
    #   '_local_addr': ('0.0.0.0', 0),
    #   '_source': <SsdpSource.SEARCH: 'search'>
    # },
    # ssdp_all_locations={'http://192.168.1.23:16021'},
    # x_homeassistant_matching_domains={'nanoleaf_panels', 'nanoleaf'})
    async def async_step_ssdp(self, discovery_info: ssdp.SsdpServiceInfo) -> FlowResult:
        """Handle a flow initialized by SSDP discovery."""
        _LOGGER.info("X async_step_ssdp: %s", discovery_info)
        netloc = str(urlparse(discovery_info.ssdp_location).netloc)
        # host = discovery_info.ssdp_headers["_host"]  # '192.168.1.23'
        name = discovery_info.ssdp_headers["nl-devicename"]  # 'Shapes 07E7'
        device_id = discovery_info.ssdp_headers["nl-deviceid"]  # '1A:25:70:12:4F:A6'
        _LOGGER.info("X netloc: %s name: %s id: %s", netloc, name, device_id)
        await self.async_set_unique_id(name)
        self._abort_if_unique_id_configured()
        self.nanoleaf_controller = NanoleafController(self.hass, netloc)
        return await self.async_step_link()

    # 2023-12-12 20:30:07.951 INFO (MainThread) [custom_components.nanoleaf_panels.config_flow] X async_step_zeroconf: ZeroconfServiceInfo(ip_address=IPv4Address('192.168.1.23'), ip_addresses=[IPv4Address('192.168.1.23'), IPv6Address('fdd0:ee30:5608:c35a:255:daff:fe5e:7e7'), IPv6Address('fe80::255:daff:fe5e:7e7')], port=16021, hostname='Shapes-07E7.local.', type='_nanoleafapi._tcp.local.', name='Shapes 07E7._nanoleafapi._tcp.local.', properties={'srcvers': '9.2.4', 'md': 'NL42', 'id': '1A:25:70:12:4F:A6'})
    # 2023-12-12 20:30:07.967 INFO (MainThread) [custom_components.nanoleaf_panels.config_flow] X async_step_zeroconf: ZeroconfServiceInfo(ip_address=IPv4Address('192.168.1.23'), ip_addresses=[IPv4Address('192.168.1.23'), IPv6Address('fdd0:ee30:5608:c35a:255:daff:fe5e:7e7'), IPv6Address('fe80::255:daff:fe5e:7e7')], port=6517, hostname='Shapes-07E7.local.', type='_nanoleafms._tcp.local.', name='Shapes 07E7._nanoleafms._tcp.local.', properties={'sf': '1', 'sh': 'oopLKA==', 'pv': '1.1', 'ci': '5', 's#': '1', 'c#': '12', 'ff': '1', 'md': 'NL42', 'id': '1A:25:70:12:4F:A6'})
    # 2023-12-12 20:30:07.968 INFO (MainThread) [custom_components.nanoleaf_panels.config_flow] X async_step_zeroconf: ZeroconfServiceInfo(ip_address=IPv4Address('192.168.1.23'), ip_addresses=[IPv4Address('192.168.1.23'), IPv6Address('fdd0:ee30:5608:c35a:255:daff:fe5e:7e7'), IPv6Address('fe80::255:daff:fe5e:7e7'), IPv6Address('fdd0:ee30:5608:c35a:255:daff:fe5e:7e7'), IPv6Address('fe80::255:daff:fe5e:7e7')], port=16021, hostname='Shapes-07E7.local.', type='_nanoleafapi._tcp.local.', name='Shapes 07E7._nanoleafapi._tcp.local.', properties={'srcvers': '9.2.4', 'md': 'NL42', 'id': '1A:25:70:12:4F:A6'})
    # 2023-12-12 20:30:07.972 INFO (MainThread) [custom_components.nanoleaf_panels.config_flow] X async_step_zeroconf: ZeroconfServiceInfo(
    # ip_address=IPv4Address('192.168.1.23'),
    # ip_addresses=[IPv4Address('192.168.1.23'), IPv6Address('fdd0:ee30:5608:c35a:255:daff:fe5e:7e7'), IPv6Address('fe80::255:daff:fe5e:7e7'), IPv6Address('fdd0:ee30:5608:c35a:255:daff:fe5e:7e7'), IPv6Address('fe80::255:daff:fe5e:7e7')],
    # port=6517,
    # hostname='Shapes-07E7.local.',
    # type='_nanoleafms._tcp.local.',
    # name='Shapes 07E7._nanoleafms._tcp.local.',
    # properties={'sf': '1', 'sh': 'oopLKA==', 'pv': '1.1', 'ci': '5', 's#': '1', 'c#': '12', 'ff': '1', 'md': 'NL42', 'id': '1A:25:70:12:4F:A6'})
    async def async_step_zeroconf(
        self, discovery_info: zeroconf.ZeroconfServiceInfo
    ) -> FlowResult:
        """Handle a flow initialized by Zeroconf discovery."""
        _LOGGER.info("X async_step_zeroconf: %s", discovery_info)
        host = str(discovery_info.ip_address)
        netloc = f"{host}:16021"
        name = discovery_info.name.split(".")[
            0
        ]  # 'Shapes 07E7._nanoleafms._tcp.local.'
        device_id = discovery_info.properties["id"]  # '1A:25:70:12:4F:A6'
        _LOGGER.info("X netloc: %s name: %s id: %s", netloc, name, device_id)
        await self.async_set_unique_id(name)
        self._abort_if_unique_id_configured()
        self.nanoleaf_controller = NanoleafController(self.hass, netloc)
        return await self.async_step_link()

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""

        # errors: Dict[str, str] = {}
        # errors["base"] = "auth"

        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=STEP_USER_DATA_SCHEMA,
                # , errors
            )

        netloc = await validate_input(self.hass, user_input)
        if netloc is not None:
            self.nanoleaf_controller = NanoleafController(self.hass, netloc)
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
            await self.async_set_unique_id(info["name"])
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=info["name"],
                data={
                    CONF_HOST: self.nanoleaf_controller.netloc,
                    CONF_TOKEN: self.nanoleaf_controller.token,
                },
            )

        return self.async_show_form(step_id="link", errors={"base": "unknown"})
