"""Binary sensor entities for Anycubic Cloud Connect."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity, BinarySensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import AnycubicCloudDataUpdateCoordinator
from .entity import AnycubicCloudEntity


@dataclass(frozen=True, kw_only=True)
class AnycubicBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Describes an Anycubic binary sensor."""

    value_fn: Callable[[Any], bool | None]


BINARY_SENSOR_DESCRIPTIONS: tuple[AnycubicBinarySensorEntityDescription, ...] = (
    AnycubicBinarySensorEntityDescription(
        key="online",
        translation_key="online",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        value_fn=lambda p: p.printer_online,
    ),
    AnycubicBinarySensorEntityDescription(
        key="busy",
        translation_key="busy",
        device_class=BinarySensorDeviceClass.RUNNING,
        value_fn=lambda p: p.is_busy,
    ),
    AnycubicBinarySensorEntityDescription(
        key="printing",
        translation_key="printing",
        device_class=BinarySensorDeviceClass.RUNNING,
        value_fn=lambda p: p.latest_project_print_in_progress,
    ),
    AnycubicBinarySensorEntityDescription(
        key="paused",
        translation_key="paused",
        icon="mdi:pause-circle",
        value_fn=lambda p: p.latest_project_print_is_paused,
    ),
    AnycubicBinarySensorEntityDescription(
        key="ace_drying",
        translation_key="ace_drying",
        device_class=BinarySensorDeviceClass.RUNNING,
        icon="mdi:hair-dryer",
        value_fn=lambda p: p.primary_drying_status_is_drying,
    ),
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up Anycubic binary sensors from a config entry."""
    coordinator: AnycubicCloudDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[AnycubicBinarySensor] = []
    for printer_id in coordinator.data or {}:
        entities.extend(AnycubicBinarySensor(coordinator, printer_id, description) for description in BINARY_SENSOR_DESCRIPTIONS)
    async_add_entities(entities)


class AnycubicBinarySensor(AnycubicCloudEntity, BinarySensorEntity):
    """Anycubic Cloud binary sensor."""

    entity_description: AnycubicBinarySensorEntityDescription

    def __init__(
        self,
        coordinator: AnycubicCloudDataUpdateCoordinator,
        printer_id: int,
        description: AnycubicBinarySensorEntityDescription,
    ) -> None:
        super().__init__(coordinator, printer_id, description.key)
        self.entity_description = description

    @property
    def is_on(self) -> bool | None:
        """Return binary sensor state."""
        printer = self.printer
        if printer is None:
            return None
        return self.entity_description.value_fn(printer)
