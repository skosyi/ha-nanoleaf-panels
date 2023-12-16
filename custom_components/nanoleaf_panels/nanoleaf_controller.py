"""The Nanoleaf controllerintegration."""
from http import HTTPStatus
import json
import logging
from typing import Any

import requests

from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from .const import EVENT

_LOGGER = logging.getLogger(__name__)


class NanoleafController:
    """Set up Nanoleaf Dev from a config entry."""

    def __init__(
        self, hass: HomeAssistant, host: str | None = None, token: str | None = None
    ) -> None:
        """Initialize internal props."""
        self.hass = hass
        self.host = host
        self.token = token
        self.info = None

    async def new_token(self) -> str | None:
        """Generate new token for device access."""
        response = await self.hass.async_add_executor_job(
            requests.post,
            f"http://{self.host}/api/v1/new",
        )
        if response.status_code == HTTPStatus.OK:
            payload = response.json()
            if payload and payload["auth_token"]:
                self.token = payload["auth_token"]
                return self.token
        return None

    async def authenticate(self, new_token: str) -> bool:
        """Check if auth token is valid."""
        # 192.168.1.36:16021 LRMudXYA0hLEZeLAWMGADgnJq14Qx9SY
        token = new_token or self.token
        response = await self.hass.async_add_executor_job(
            requests.get,
            f"http://{self.host}/api/v1/{new_token}",
        )

        if response.status_code == HTTPStatus.OK:
            self.token = token
        else:
            return False

        return True

    # info: {
    # 'name': 'Shapes 07E7',
    # 'serialNo': 'S20530H1600',
    # 'manufacturer': 'Nanoleaf',
    # 'firmwareVersion': '9.2.4',
    # 'hardwareVersion': '1.3-0',
    # 'model': 'NL42',
    # 'discovery': {},
    # 'effects': {'effectsList': ['Beatdrop', 'Blaze', 'Catch a Hedgehog', 'Cocoa Beach', 'Cotton Candy', 'Date Night', 'Dynamic 21-11-2023 12:13', 'Hip Hop', 'Hot Sauce', 'Jungle', 'Lightscape', 'Memory', 'Morning Sky', 'Northern Lights', 'Pop Rocks', 'Prism', 'Starlight', 'Sundown', 'Waterfall', 'Whack A Mole'], 'select': 'Morning Sky'},
    # 'firmwareUpgrade': {},
    # 'panelLayout': {'globalOrientation': {'value': 2, 'max': 360, 'min': 0}, 'layout': {'numPanels': 16, 'sideLength': 67, 'positionData': [{'panelId': 30526, 'x': 25, 'y': 0, 'o': 0, 'shapeType': 9}, {'panelId': 5584, 'x': 59, 'y': 19, 'o': 60, 'shapeType': 9}, {'panelId': 50426, 'x': 59, 'y': 58, 'o': 120, 'shapeType': 9}, {'panelId': 12860, 'x': 92, 'y': 77, 'o': 60, 'shapeType': 9}, {'panelId': 52419, 'x': 92, 'y': 116, 'o': 0, 'shapeType': 9}, {'panelId': 58539, 'x': 126, 'y': 135, 'o': 300, 'shapeType': 9}, {'panelId': 63684, 'x': 126, 'y': 174, 'o': 0, 'shapeType': 9}, {'panelId': 21094, 'x': 159, 'y': 116, 'o': 120, 'shapeType': 9}, {'panelId': 22289, 'x': 92, 'y': 0, 'o': 240, 'shapeType': 9}, {'panelId': 18116, 'x': 126, 'y': 19, 'o': 300, 'shapeType': 9}, {'panelId': 10284, 'x': 159, 'y': 0, 'o': 120, 'shapeType': 9}, {'panelId': 9772, 'x': 193, 'y': 19, 'o': 60, 'shapeType': 9}, {'panelId': 40805, 'x': 193, 'y': 58, 'o': 120, 'shapeType': 9}, {'panelId': 13902, 'x': 159, 'y': 77, 'o': 300, 'shapeType': 9}, {'panelId': 38268, 'x': 226, 'y': 0, 'o': 240, 'shapeType': 9}, {'panelId': 0, 'x': 0, 'y': 15, 'o': 60, 'shapeType': 12}]}},
    # 'qkihnokomhartlnp': {},
    # 'schedules': {},
    # 'state': {'brightness': {'value': 9, 'max': 100, 'min': 0}, 'colorMode': 'effect', 'ct': {'value': 6493, 'max': 6500, 'min': 1200}, 'hue': {'value': 0, 'max': 360, 'min': 0}, 'on': {'value': True}, 'sat': {'value': 0, 'max': 100, 'min': 0}}}
    async def get_info(self) -> dict[str, Any] | None:
        """Fetch device information."""
        if self.info is None:
            response = await self.hass.async_add_executor_job(
                requests.get,
                f"http://{self.host}/api/v1/{self.token}",
            )

            if response.status_code == HTTPStatus.OK:
                self.info = response.json()

        return self.info

    async def set_brightness(self, brightness, transition) -> int | None:
        """Set brightness for all panels."""
        payload = json.dumps(
            {
                "brightness": {
                    "value": int(brightness),
                    "duration": transition,
                }
            }
        )
        response = await self.hass.async_add_executor_job(
            requests.put,
            f"http://{self.host}/api/v1/{self.token}/state/brightness",
            payload,
        )
        result = None
        if int(response.status_code / 100) == 2:
            result = brightness
        return result

    async def display_static_effect(self, panel_id, rgb, transition) -> bool:
        """Set static effect for a single panel."""
        (red, green, blue) = rgb
        white = 0
        payload = json.dumps(
            {
                "write": {
                    "command": "display",
                    "animType": "static",
                    "animData": f"1 {panel_id} 1 {red} {green} {blue} {white} {transition}",
                    "loop": False,
                    "palette": [
                        # {"hue": 0, "saturation": 100, "brightness": brightness},
                        # {"hue": 30, "saturation": 100, "brightness": 200},
                    ],
                    "brightnessRange": {"minValue": 0, "maxValue": 255},
                    "colorType": "HSB",
                },
            }
        )
        response = await self.hass.async_add_executor_job(
            requests.put,
            f"http://{self.host}/api/v1/{self.token}/effects",
            payload,
        )

        return response.status_code == HTTPStatus.NO_CONTENT

    def process_events_stream(self, entry_id) -> None:
        """Read stream and trigger corresponding events."""
        response = requests.get(
            f"http://{self.host}/api/v1/{self.token}/events?id=4",
            stream=True,
            timeout=None,
        )

        for line in response.iter_lines(chunk_size=1):
            if line:
                decoded_line = line.decode("utf-8")
                # print(decoded_line)
                key = "data:"
                if decoded_line.startswith(key):
                    value = decoded_line[len(key) :]
                    obj = json.loads(value)
                    _LOGGER.info(obj)

                    entity_id = obj["events"][0]["panelId"]

                    entity_reg = er.async_get(self.hass)
                    entities = er.async_entries_for_config_entry(entity_reg, entry_id)
                    entry_found = None
                    for entity in entities:
                        if entity.domain != "light":
                            continue
                        if entity.unique_id == entity_id:
                            entry_found = entity
                            break

                    if entry_found is not None:
                        if obj["events"][0]["gesture"] == 0:
                            event_data = {
                                "device_id": entry_found.device_id,
                                "entity_id": entry_found.entity_id,
                                "type": "single_tap",
                            }
                            self.hass.bus.fire(EVENT, event_data)
                            _LOGGER.info("Single tap %s", event_data)
                            # hass.bus.async_fire(EVENT, event_data)
                        if obj["events"][0]["gesture"] == 1:
                            event_data = {
                                "device_id": entry_found.device_id,
                                "entity_id": entry_found.entity_id,
                                "type": "double_tap",
                            }
                            self.hass.bus.fire(EVENT, event_data)
                            _LOGGER.info("Double tap %s", event_data)

        _LOGGER.info("Stream ended")
