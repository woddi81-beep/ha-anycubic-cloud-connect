"""Button entities for Anycubic Cloud Connect."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import AnycubicCloudDataUpdateCoordinator
from .entity import AnycubicCloudEntity


@dataclass(frozen=True, kw_only=True)
class AnycubicButtonEntityDescription(ButtonEntityDescription):
    """Describes an Anycubic button."""

    press_fn: Callable[[AnycubicCloudDataUpdateCoordinator, Any], Awaitable[Any]]
    available_fn: Callable[[Any], bool] | None = None


async def _pause(coordinator: AnycubicCloudDataUpdateCoordinator, printer: Any) -> Any:
    return await coordinator.api.pause_print(printer, printer.latest_project)


async def _resume(coordinator: AnycubicCloudDataUpdateCoordinator, printer: Any) -> Any:
    return await coordinator.api.resume_print(printer, printer.latest_project)


async def _cancel(coordinator: AnycubicCloudDataUpdateCoordinator, printer: Any) -> Any:
    return await coordinator.api.cancel_print(printer, printer.latest_project)


async def _refresh(coordinator: AnycubicCloudDataUpdateCoordinator, printer: Any) -> None:
    await coordinator.async_request_refresh()


BUTTON_DESCRIPTIONS: tuple[AnycubicButtonEntityDescription, ...] = (
    AnycubicButtonEntityDescription(
        key="pause_print",
        translation_key="pause_print",
        icon="mdi:pause",
        press_fn=_pause,
        available_fn=lambda p: bool(p.printer_online and p.latest_project_print_in_progress and not p.latest_project_print_is_paused),
    ),
    AnycubicButtonEntityDescription(
        key="resume_print",
        translation_key="resume_print",
        icon="mdi:play",
        press_fn=_resume,
        available_fn=lambda p: bool(p.printer_online and p.latest_project_print_is_paused),
    ),
    AnycubicButtonEntityDescription(
        key="cancel_print",
        translation_key="cancel_print",
        icon="mdi:stop",
        press_fn=_cancel,
        available_fn=lambda p: bool(p.printer_online and (p.latest_project_print_in_progress or p.latest_project_print_is_paused)),
    ),
    AnycubicButtonEntityDescription(
        key="refresh",
        translation_key="refresh",
        icon="mdi:refresh",
        press_fn=_refresh,
    ),
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up Anycubic buttons from a config entry."""
    coordinator: AnycubicCloudDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[AnycubicButton] = []
    for printer_id in coordinator.data or {}:
        entities.extend(AnycubicButton(coordinator, printer_id, description) for description in BUTTON_DESCRIPTIONS)
    async_add_entities(entities)


class AnycubicButton(AnycubicCloudEntity, ButtonEntity):
    """Anycubic Cloud button."""

    entity_description: AnycubicButtonEntityDescription

    def __init__(
        self,
        coordinator: AnycubicCloudDataUpdateCoordinator,
        printer_id: int,
        description: AnycubicButtonEntityDescription,
    ) -> None:
        super().__init__(coordinator, printer_id, description.key)
        self.entity_description = description

    @property
    def available(self) -> bool:
        """Return availability."""
        if not super().available:
            return False
        printer = self.printer
        if printer is None:
            return False
        if self.entity_description.available_fn is None:
            return True
        return self.entity_description.available_fn(printer)

    async def async_press(self) -> None:
        """Handle button press."""
        printer = self.printer
        if printer is None:
            return
        await self.entity_description.press_fn(self.coordinator, printer)
        await self.coordinator.async_request_refresh()
