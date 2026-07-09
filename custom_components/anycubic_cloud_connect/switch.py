"""Switch entities for Anycubic Cloud Connect."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import AnycubicCloudDataUpdateCoordinator
from .entity import AnycubicCloudEntity


@dataclass(frozen=True, kw_only=True)
class AnycubicSwitchEntityDescription(SwitchEntityDescription):
    """Describes an Anycubic switch."""

    box_id: int = 0


SWITCH_DESCRIPTIONS: tuple[AnycubicSwitchEntityDescription, ...] = (
    AnycubicSwitchEntityDescription(
        key="ace_auto_feed_1",
        translation_key="ace_auto_feed_1",
        icon="mdi:autorenew",
        box_id=0,
    ),
    AnycubicSwitchEntityDescription(
        key="ace_auto_feed_2",
        translation_key="ace_auto_feed_2",
        icon="mdi:autorenew",
        box_id=1,
    ),
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up Anycubic switches from a config entry."""
    coordinator: AnycubicCloudDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[AnycubicSwitch] = []
    for printer_id, printer in (coordinator.data or {}).items():
        for description in SWITCH_DESCRIPTIONS:
            if printer.connected_ace_units > description.box_id:
                entities.append(AnycubicSwitch(coordinator, printer_id, description))
    async_add_entities(entities)


class AnycubicSwitch(AnycubicCloudEntity, SwitchEntity):
    """Anycubic Cloud switch."""

    entity_description: AnycubicSwitchEntityDescription

    def __init__(
        self,
        coordinator: AnycubicCloudDataUpdateCoordinator,
        printer_id: int,
        description: AnycubicSwitchEntityDescription,
    ) -> None:
        super().__init__(coordinator, printer_id, description.key)
        self.entity_description = description

    @property
    def available(self) -> bool:
        """Return availability."""
        printer = self.printer
        return bool(super().available and printer and printer.connected_ace_units > self.entity_description.box_id)

    @property
    def is_on(self) -> bool | None:
        """Return switch state."""
        printer = self.printer
        if printer is None or not printer.multi_color_box:
            return None
        try:
            return bool(printer.multi_color_box[self.entity_description.box_id].auto_feed)
        except IndexError:
            return None

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on ACE auto feed."""
        printer = self.printer
        if printer is None:
            return
        await self.coordinator.api.multi_color_box_set_auto_feed(printer, True, self.entity_description.box_id)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off ACE auto feed."""
        printer = self.printer
        if printer is None:
            return
        await self.coordinator.api.multi_color_box_set_auto_feed(printer, False, self.entity_description.box_id)
        await self.coordinator.async_request_refresh()
