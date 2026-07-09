"""Small Home Assistant friendly wrapper around anycubic-cloud-mcp."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import Any

import aiohttp

from anycubic_cloud_api import AnycubicAPI
from anycubic_cloud_api.data_models.printer import AnycubicPrinter
from anycubic_cloud_api.models.auth import AnycubicAuthMode

from .const import AUTH_MODE_ANDROID, AUTH_MODE_SLICER, AUTH_MODE_WEB

_LOGGER = logging.getLogger(__name__)

AUTH_MODE_MAP: dict[str, AnycubicAuthMode] = {
    AUTH_MODE_WEB: AnycubicAuthMode.WEB,
    AUTH_MODE_SLICER: AnycubicAuthMode.SLICER,
    AUTH_MODE_ANDROID: AnycubicAuthMode.ANDROID,
}


@dataclass(slots=True)
class AnycubicAuthResult:
    """Result of validating Anycubic Cloud authentication."""

    user_identifier: str
    printers: list[AnycubicPrinter]


class AnycubicCloudClient:
    """Home Assistant wrapper for Anycubic Cloud API."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        logger: logging.Logger,
        token: str,
        auth_mode: str,
        device_id: str | None = None,
    ) -> None:
        if auth_mode not in AUTH_MODE_MAP:
            raise ValueError(f"Unsupported Anycubic auth mode: {auth_mode}")

        self._api = AnycubicAPI(
            session=session,
            cookie_jar=session.cookie_jar,
            debug_logger=logger,
            auth_token=token,
            auth_mode=AUTH_MODE_MAP[auth_mode],
            device_id=device_id,
        )
        self._auth_lock = asyncio.Lock()
        self._authenticated = False

    @property
    def api(self) -> AnycubicAPI:
        """Return raw Anycubic API object."""
        return self._api

    async def async_ensure_auth(self) -> None:
        """Validate and refresh cloud credentials if required."""
        async with self._auth_lock:
            if self._authenticated and not self._api.tokens_changed:
                return
            if not await self._api.check_api_tokens():
                raise ValueError("Anycubic Cloud authentication failed")
            self._authenticated = True

    async def async_validate(self) -> AnycubicAuthResult:
        """Validate credentials and return account/printer data."""
        await self.async_ensure_auth()
        user_identifier = self._api.anycubic_auth.api_user_identifier
        printers = await self.async_list_printers(include_project=False)
        return AnycubicAuthResult(user_identifier=user_identifier, printers=printers)

    async def async_list_printers(self, include_project: bool) -> list[AnycubicPrinter]:
        """Return all printers visible in the Anycubic Cloud account."""
        await self.async_ensure_auth()
        printers = await self._api.list_my_printers(ignore_init_errors=True)
        valid_printers = [printer for printer in printers if printer is not None]

        for printer in valid_printers:
            try:
                await printer.update_info_from_api(with_project=include_project)
            except Exception as err:  # noqa: BLE001 - surface a partial update in HA
                _LOGGER.debug("Could not refresh full Anycubic printer info for %s: %s", printer.id, err)

        return valid_printers

    async def async_get_printer(self, printer_id: int, include_project: bool = True) -> AnycubicPrinter:
        """Return a single printer, refreshed from the cloud."""
        await self.async_ensure_auth()
        printer = await self._api.printer_info_for_id(printer_id, ignore_init_errors=True)
        if printer is None:
            raise ValueError(f"Anycubic printer not found: {printer_id}")
        if include_project:
            await printer.update_info_from_api(with_project=True)
        return printer

    @staticmethod
    def printer_extra_state_attributes(printer: AnycubicPrinter) -> dict[str, Any]:
        """Return safe diagnostic-ish attributes for a printer."""
        fw = printer.fw_version
        project = printer.latest_project
        return {
            "printer_id": printer.id,
            "name": printer.name,
            "model": printer.model,
            "machine_type": printer.machine_type,
            "firmware_version": fw.firmware_version if fw else None,
            "firmware_update_available": fw.update_available if fw else None,
            "firmware_available_version": fw.available_version if fw else None,
            "connected_peripherals": printer.connected_peripherals,
            "latest_project_id": project.id if project else None,
            "latest_project_name": printer.latest_project_name,
            "latest_project_status": printer.latest_project_print_status,
            "latest_project_status_message": printer.latest_project_print_status_message,
            "ace_connected_units": printer.connected_ace_units,
            "ace_spools": printer.primary_multi_color_box_spool_info_object,
        }
