"""Diagnostics support for Anycubic Cloud Connect."""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntry
from homeassistant.components.diagnostics import async_redact_data

from .const import CONF_TOKEN, DOMAIN

TO_REDACT = {CONF_TOKEN, "auth_token", "auth_access_token", "device_id", "key"}


async def async_get_config_entry_diagnostics(hass: HomeAssistant, entry: ConfigEntry) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator = hass.data[DOMAIN].get(entry.entry_id)
    printers = []
    if coordinator and coordinator.data:
        for printer in coordinator.data.values():
            fw = printer.fw_version
            printers.append(
                {
                    "id": printer.id,
                    "name": printer.name,
                    "model": printer.model,
                    "online": printer.printer_online,
                    "status": printer.current_status,
                    "firmware": fw.firmware_version if fw else None,
                    "ace_connected_units": printer.connected_ace_units,
                    "peripherals": printer.connected_peripherals,
                }
            )
    return {
        "entry": async_redact_data(entry.as_dict(), TO_REDACT),
        "printers": async_redact_data(printers, TO_REDACT),
    }


async def async_get_device_diagnostics(hass: HomeAssistant, entry: ConfigEntry, device: DeviceEntry) -> dict[str, Any]:
    """Return diagnostics for a device."""
    coordinator = hass.data[DOMAIN].get(entry.entry_id)
    if coordinator is None or not coordinator.data:
        return {"error": "coordinator_not_loaded"}

    printer_id: int | None = None
    for domain, identifier in device.identifiers:
        if domain == DOMAIN:
            printer_id = int(identifier)
            break

    if printer_id is None or printer_id not in coordinator.data:
        return {"error": "printer_not_found"}

    printer = coordinator.data[printer_id]
    return async_redact_data(
        {
            "id": printer.id,
            "name": printer.name,
            "model": printer.model,
            "online": printer.printer_online,
            "status": printer.current_status,
            "attributes": coordinator.client.printer_extra_state_attributes(printer),
        },
        TO_REDACT,
    )
