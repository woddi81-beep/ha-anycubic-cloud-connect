"""Base entities for Anycubic Cloud Connect."""

from __future__ import annotations

from typing import Any

from anycubic_cloud_api.data_models.printer import AnycubicPrinter

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import AnycubicCloudClient
from .const import DOMAIN
from .coordinator import AnycubicCloudDataUpdateCoordinator


class AnycubicCloudEntity(CoordinatorEntity):
    """Base class for Anycubic Cloud entities."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: AnycubicCloudDataUpdateCoordinator, printer_id: int, key: str) -> None:
        super().__init__(coordinator)
        self.printer_id = printer_id
        self.entity_key = key
        self._attr_unique_id = f"{DOMAIN}_{printer_id}_{key}"

    @property
    def printer(self) -> AnycubicPrinter | None:
        """Return the current printer object."""
        return self.coordinator.get_printer(self.printer_id)

    @property
    def available(self) -> bool:
        """Return entity availability."""
        return self.printer is not None and super().available

    @property
    def device_info(self) -> DeviceInfo:
        """Return Home Assistant device info."""
        printer = self.printer
        identifiers = {(DOMAIN, str(self.printer_id))}
        if printer is None:
            return DeviceInfo(identifiers=identifiers)
        return DeviceInfo(
            identifiers=identifiers,
            name=printer.name or f"Anycubic {self.printer_id}",
            manufacturer="Anycubic",
            model=printer.model,
            sw_version=(printer.fw_version.firmware_version if printer.fw_version else None),
            configuration_url="https://cloud-universe.anycubic.com/file",
        )

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return common attributes."""
        printer = self.printer
        if printer is None:
            return None
        return AnycubicCloudClient.printer_extra_state_attributes(printer)
