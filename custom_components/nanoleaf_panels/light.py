"""Platform for light integration."""
import logging
import threading
import time
from typing import Any

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_RGB_COLOR,
    ATTR_TRANSITION,
    ColorMode,
    LightEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .nanoleaf_controller import NanoleafController

_LOGGER = logging.getLogger(__name__)


def nanoleaf_panels_thread(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Thread to listen panel events."""
    while True:
        nanoleaf_controller = hass.data[DOMAIN][entry.entry_id]
        nanoleaf_controller.process_events_stream(entry.entry_id)
        time.sleep(5)
        _LOGGER.info("Reconnect")


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Lights setup entry."""
    nanoleaf_controller: NanoleafController = hass.data[DOMAIN][entry.entry_id]

    entities = None
    info = await nanoleaf_controller.get_info()
    if info is not None:
        entities = []
        panels = info["panelLayout"]["layout"]["positionData"]
        index = 1
        for panel in panels:
            if panel["shapeType"] == 9:
                entity = PanelLight(
                    panel["panelId"],
                    f"Panel{index:02}",
                    nanoleaf_controller,
                    info,
                )
                entities.append(entity)
                index += 1

    if entities is not None:
        async_add_entities(entities)

        thread = threading.Thread(
            target=nanoleaf_panels_thread,
            name="nanoleaf_panels_thread",
            args=(
                hass,
                entry,
            ),
        )
        thread.start()


class PanelLight(LightEntity):
    """Representation of an Awesome Light."""

    _attr_supported_color_modes = {ColorMode.RGB}
    _attr_color_mode = ColorMode.RGB
    # _attr_supported_features = LightEntityFeature.TRANSITION
    _attr_is_on = True
    _attr_brightness = 255
    _attr_rgb_color = (255, 255, 255)
    _transition = 1

    def __init__(self, unique_id, name, nanoleaf_controller, device) -> None:
        """Initialize an PanelLight."""
        self.nanoleaf_controller = nanoleaf_controller
        self.device = device

        self._attr_unique_id = unique_id
        self._attr_name = name

        self._attr_brightness = int(
            255
            * device["state"]["brightness"]["value"]
            / device["state"]["brightness"]["max"]
        )
        self._attr_is_on = device["state"]["on"]["value"]

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Instruct the light to turn on."""
        default_rgb = None
        if not kwargs:
            default_rgb = (255, 255, 255)

        new_transition = kwargs.get(ATTR_TRANSITION)
        if new_transition is not None:
            self._transition = new_transition

        new_brightness = kwargs.get(ATTR_BRIGHTNESS)
        if new_brightness is not None:
            self._attr_brightness = new_brightness
            self._attr_brightness = await self.nanoleaf_controller.set_brightness(
                self._attr_brightness * 100 / 255, self._transition
            )
            self._attr_is_on = bool(self._attr_brightness)

        new_rgb_color = kwargs.get(ATTR_RGB_COLOR, default_rgb)
        if new_rgb_color is not None:
            self._attr_rgb_color = new_rgb_color
            self._attr_is_on = await self.nanoleaf_controller.display_static_effect(
                self._attr_unique_id,
                self._attr_rgb_color,
                self._transition * 10,
            )

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Instruct the light to turn off."""
        self._attr_rgb_color = (0, 0, 0)
        self._attr_is_on = False
        await self.nanoleaf_controller.display_static_effect(
            self._attr_unique_id, self._attr_rgb_color, 1 * 10
        )

    # def update(self) -> None:
    # """Fetch new state data for this light.
    # This is the only method that should fetch new data for Home Assistant.
    # """
    # print("update")
    # self._attr_rgb_color = (0, 128, 0)

    # self._light.update()
    # self._state = self._light.is_on()
    # self._brightness = self._light.brightness

    @property
    def device_info(self) -> DeviceInfo | None:
        """Build device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.device["name"])},
            name=self.device["name"],
            manufacturer=self.device["manufacturer"],
            model=self.device["model"],
            sw_version=self.device["firmwareVersion"],
            hw_version=self.device["hardwareVersion"],
            configuration_url=f"http://{self.nanoleaf_controller.netloc.split(':')[0]}",
        )
