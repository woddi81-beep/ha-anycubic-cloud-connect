"""Data coordinator for Anycubic Cloud Connect."""

from __future__ import annotations

import logging
from datetime import timedelta

from anycubic_cloud_api.data_models.printer import AnycubicPrinter

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import AnycubicCloudClient
from .const import (
    CONF_AUTH_MODE,
    CONF_DEVICE_ID,
    CONF_INCLUDE_PROJECT,
    CONF_SCAN_INTERVAL,
    CONF_TOKEN,
    DEFAULT_INCLUDE_PROJECT,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    MIN_SCAN_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)


class AnycubicCloudDataUpdateCoordinator(DataUpdateCoordinator):
    """Poll Anycubic Cloud for printer state."""

    config_entry: ConfigEntry

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.config_entry = entry
        data = entry.data
        options = entry.options
        scan_interval = max(
            int(options.get(CONF_SCAN_INTERVAL, data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL))),
            MIN_SCAN_INTERVAL,
        )
        self.include_project = bool(
            options.get(CONF_INCLUDE_PROJECT, data.get(CONF_INCLUDE_PROJECT, DEFAULT_INCLUDE_PROJECT))
        )
        self.client = AnycubicCloudClient(
            session=async_get_clientsession(hass),
            logger=_LOGGER,
            token=data[CONF_TOKEN],
            auth_mode=data[CONF_AUTH_MODE],
            device_id=data.get(CONF_DEVICE_ID) or None,
        )
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )

    @property
    def api(self):  # noqa: ANN201 - upstream package type is enough in api.py
        """Expose raw Anycubic API for command entities/services."""
        return self.client.api

    async def _async_update_data(self) -> dict[int, AnycubicPrinter]:
        try:
            printers = await self.client.async_list_printers(include_project=self.include_project)
            return {printer.id: printer for printer in printers}
        except Exception as err:  # noqa: BLE001
            raise UpdateFailed(f"Could not update Anycubic Cloud data: {err}") from err

    def get_printer(self, printer_id: int) -> AnycubicPrinter | None:
        """Return a printer from the latest coordinator data."""
        return self.data.get(printer_id) if self.data else None
