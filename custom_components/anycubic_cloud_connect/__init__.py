"""Anycubic Cloud Connect integration for Home Assistant."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall, SupportsResponse
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv

from .const import (
    ATTR_ORDER_MESSAGE_ID,
    CONF_BLUE,
    CONF_BOX_ID,
    CONF_DURATION,
    CONF_GREEN,
    CONF_MATERIAL_TYPE,
    CONF_PRINTER_ID,
    CONF_RED,
    CONF_SLOT_INDEX,
    CONF_TARGET_TEMP,
    DEFAULT_DRYING_DURATION,
    DEFAULT_DRYING_TEMP,
    DOMAIN,
    PLATFORMS,
    SERVICE_ACE_DRY_START,
    SERVICE_ACE_DRY_STOP,
    SERVICE_ACE_FEED_FILAMENT,
    SERVICE_ACE_RETRACT_FILAMENT,
    SERVICE_ACE_SET_AUTO_FEED,
    SERVICE_ACE_SET_SLOT,
    SERVICE_CANCEL_PRINT,
    SERVICE_PAUSE_PRINT,
    SERVICE_RESUME_PRINT,
)
from .coordinator import AnycubicCloudDataUpdateCoordinator

COMMON_PRINTER_SERVICE_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_PRINTER_ID): vol.Coerce(int),
        vol.Optional("config_entry_id"): cv.string,
    }
)

ACE_BOX_SCHEMA = COMMON_PRINTER_SERVICE_SCHEMA.extend(
    {
        vol.Optional(CONF_BOX_ID, default=0): vol.Coerce(int),
    }
)


def _coordinators(hass: HomeAssistant) -> dict[str, AnycubicCloudDataUpdateCoordinator]:
    return hass.data.setdefault(DOMAIN, {})


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Anycubic Cloud Connect from a config entry."""
    coordinator = AnycubicCloudDataUpdateCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    _coordinators(hass)[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    await _async_setup_services(hass)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        _coordinators(hass).pop(entry.entry_id, None)
    return unload_ok


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload integration when options change."""
    await hass.config_entries.async_reload(entry.entry_id)


def _find_coordinator_and_printer(
    hass: HomeAssistant,
    call: ServiceCall,
) -> tuple[AnycubicCloudDataUpdateCoordinator, Any]:
    printer_id = int(call.data[CONF_PRINTER_ID])
    entry_id = call.data.get("config_entry_id")
    coordinators = _coordinators(hass)

    if entry_id:
        coordinator = coordinators.get(entry_id)
        if coordinator is None:
            raise HomeAssistantError(f"Anycubic config entry not found: {entry_id}")
        printer = coordinator.get_printer(printer_id)
        if printer is None:
            raise HomeAssistantError(f"Anycubic printer not found in entry {entry_id}: {printer_id}")
        return coordinator, printer

    for coordinator in coordinators.values():
        printer = coordinator.get_printer(printer_id)
        if printer is not None:
            return coordinator, printer

    raise HomeAssistantError(f"Anycubic printer not found: {printer_id}")


async def _run_printer_command(hass: HomeAssistant, call: ServiceCall, command: str) -> dict[str, Any]:
    coordinator, printer = _find_coordinator_and_printer(hass, call)
    project = printer.latest_project
    if command == SERVICE_PAUSE_PRINT:
        msg_id = await coordinator.api.pause_print(printer, project)
    elif command == SERVICE_RESUME_PRINT:
        msg_id = await coordinator.api.resume_print(printer, project)
    elif command == SERVICE_CANCEL_PRINT:
        msg_id = await coordinator.api.cancel_print(printer, project)
    else:
        raise HomeAssistantError(f"Unsupported command: {command}")
    await coordinator.async_request_refresh()
    return {ATTR_ORDER_MESSAGE_ID: msg_id}


async def _async_setup_services(hass: HomeAssistant) -> None:
    """Register integration services once per Home Assistant instance."""
    if hass.services.has_service(DOMAIN, SERVICE_PAUSE_PRINT):
        return

    async def handle_pause(call: ServiceCall) -> dict[str, Any]:
        return await _run_printer_command(hass, call, SERVICE_PAUSE_PRINT)

    async def handle_resume(call: ServiceCall) -> dict[str, Any]:
        return await _run_printer_command(hass, call, SERVICE_RESUME_PRINT)

    async def handle_cancel(call: ServiceCall) -> dict[str, Any]:
        return await _run_printer_command(hass, call, SERVICE_CANCEL_PRINT)

    async def handle_ace_feed(call: ServiceCall) -> dict[str, Any]:
        coordinator, printer = _find_coordinator_and_printer(hass, call)
        msg_id = await coordinator.api.multi_color_box_feed_filament(
            printer=printer,
            slot_index=int(call.data[CONF_SLOT_INDEX]),
            box_id=int(call.data.get(CONF_BOX_ID, 0)),
            finish=bool(call.data.get("finish", False)),
        )
        await coordinator.async_request_refresh()
        return {ATTR_ORDER_MESSAGE_ID: msg_id}

    async def handle_ace_retract(call: ServiceCall) -> dict[str, Any]:
        coordinator, printer = _find_coordinator_and_printer(hass, call)
        msg_id = await coordinator.api.multi_color_box_retract_filament(
            printer=printer,
            box_id=int(call.data.get(CONF_BOX_ID, 0)),
        )
        await coordinator.async_request_refresh()
        return {ATTR_ORDER_MESSAGE_ID: msg_id}

    async def handle_ace_auto_feed(call: ServiceCall) -> dict[str, Any]:
        coordinator, printer = _find_coordinator_and_printer(hass, call)
        msg_id = await coordinator.api.multi_color_box_set_auto_feed(
            printer=printer,
            enabled=bool(call.data["enabled"]),
            box_id=int(call.data.get(CONF_BOX_ID, 0)),
        )
        await coordinator.async_request_refresh()
        return {ATTR_ORDER_MESSAGE_ID: msg_id}

    async def handle_ace_set_slot(call: ServiceCall) -> dict[str, Any]:
        coordinator, printer = _find_coordinator_and_printer(hass, call)
        msg_id = await coordinator.api.multi_color_box_set_slot(
            printer=printer,
            slot_index=int(call.data[CONF_SLOT_INDEX]),
            slot_material_type=str(call.data[CONF_MATERIAL_TYPE]),
            slot_color_red=int(call.data[CONF_RED]),
            slot_color_green=int(call.data[CONF_GREEN]),
            slot_color_blue=int(call.data[CONF_BLUE]),
            box_id=int(call.data.get(CONF_BOX_ID, 0)),
        )
        await coordinator.async_request_refresh()
        return {ATTR_ORDER_MESSAGE_ID: msg_id}

    async def handle_ace_dry_start(call: ServiceCall) -> dict[str, Any]:
        coordinator, printer = _find_coordinator_and_printer(hass, call)
        msg_id = await coordinator.api.multi_color_box_drying_start(
            printer=printer,
            duration=int(call.data.get(CONF_DURATION, DEFAULT_DRYING_DURATION)),
            target_temp=int(call.data.get(CONF_TARGET_TEMP, DEFAULT_DRYING_TEMP)),
            box_id=int(call.data.get(CONF_BOX_ID, 0)),
        )
        await coordinator.async_request_refresh()
        return {ATTR_ORDER_MESSAGE_ID: msg_id}

    async def handle_ace_dry_stop(call: ServiceCall) -> dict[str, Any]:
        coordinator, printer = _find_coordinator_and_printer(hass, call)
        msg_id = await coordinator.api.multi_color_box_drying_stop(
            printer=printer,
            box_id=int(call.data.get(CONF_BOX_ID, -1)),
        )
        await coordinator.async_request_refresh()
        return {ATTR_ORDER_MESSAGE_ID: msg_id}

    hass.services.async_register(DOMAIN, SERVICE_PAUSE_PRINT, handle_pause, schema=COMMON_PRINTER_SERVICE_SCHEMA, supports_response=SupportsResponse.OPTIONAL)
    hass.services.async_register(DOMAIN, SERVICE_RESUME_PRINT, handle_resume, schema=COMMON_PRINTER_SERVICE_SCHEMA, supports_response=SupportsResponse.OPTIONAL)
    hass.services.async_register(DOMAIN, SERVICE_CANCEL_PRINT, handle_cancel, schema=COMMON_PRINTER_SERVICE_SCHEMA, supports_response=SupportsResponse.OPTIONAL)
    hass.services.async_register(
        DOMAIN,
        SERVICE_ACE_FEED_FILAMENT,
        handle_ace_feed,
        schema=ACE_BOX_SCHEMA.extend(
            {
                vol.Required(CONF_SLOT_INDEX): vol.All(vol.Coerce(int), vol.Range(min=1, max=8)),
                vol.Optional("finish", default=False): cv.boolean,
            }
        ),
        supports_response=SupportsResponse.OPTIONAL,
    )
    hass.services.async_register(DOMAIN, SERVICE_ACE_RETRACT_FILAMENT, handle_ace_retract, schema=ACE_BOX_SCHEMA, supports_response=SupportsResponse.OPTIONAL)
    hass.services.async_register(
        DOMAIN,
        SERVICE_ACE_SET_AUTO_FEED,
        handle_ace_auto_feed,
        schema=ACE_BOX_SCHEMA.extend({vol.Required("enabled"): cv.boolean}),
        supports_response=SupportsResponse.OPTIONAL,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_ACE_SET_SLOT,
        handle_ace_set_slot,
        schema=ACE_BOX_SCHEMA.extend(
            {
                vol.Required(CONF_SLOT_INDEX): vol.All(vol.Coerce(int), vol.Range(min=1, max=8)),
                vol.Required(CONF_MATERIAL_TYPE): cv.string,
                vol.Required(CONF_RED): vol.All(vol.Coerce(int), vol.Range(min=0, max=255)),
                vol.Required(CONF_GREEN): vol.All(vol.Coerce(int), vol.Range(min=0, max=255)),
                vol.Required(CONF_BLUE): vol.All(vol.Coerce(int), vol.Range(min=0, max=255)),
            }
        ),
        supports_response=SupportsResponse.OPTIONAL,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_ACE_DRY_START,
        handle_ace_dry_start,
        schema=ACE_BOX_SCHEMA.extend(
            {
                vol.Optional(CONF_TARGET_TEMP, default=DEFAULT_DRYING_TEMP): vol.All(vol.Coerce(int), vol.Range(min=30, max=70)),
                vol.Optional(CONF_DURATION, default=DEFAULT_DRYING_DURATION): vol.All(vol.Coerce(int), vol.Range(min=60, max=86400)),
            }
        ),
        supports_response=SupportsResponse.OPTIONAL,
    )
    hass.services.async_register(DOMAIN, SERVICE_ACE_DRY_STOP, handle_ace_dry_stop, schema=ACE_BOX_SCHEMA, supports_response=SupportsResponse.OPTIONAL)
