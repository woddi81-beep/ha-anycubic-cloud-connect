"""Config flow for Anycubic Cloud Connect."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import AnycubicCloudClient
from .const import (
    AUTH_MODES,
    CONF_AUTH_MODE,
    CONF_DEVICE_ID,
    CONF_INCLUDE_PROJECT,
    CONF_SCAN_INTERVAL,
    CONF_TOKEN,
    DEFAULT_AUTH_MODE,
    DEFAULT_INCLUDE_PROJECT,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    MIN_SCAN_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)


class CannotConnect(Exception):
    """Unable to connect or authenticate."""


async def _validate_input(hass, user_input: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    client = AnycubicCloudClient(
        session=async_get_clientsession(hass),
        logger=_LOGGER,
        token=user_input[CONF_TOKEN],
        auth_mode=user_input[CONF_AUTH_MODE],
        device_id=user_input.get(CONF_DEVICE_ID) or None,
    )
    try:
        async with asyncio.timeout(30):
            result = await client.async_validate()
    except Exception as err:  # noqa: BLE001
        raise CannotConnect from err

    title = f"Anycubic Cloud ({len(result.printers)} printers)"
    if result.printers:
        title = result.printers[0].name or title

    return {"title": title, "user_identifier": result.user_identifier}


class AnycubicCloudConnectConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Anycubic Cloud Connect."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            cleaned = dict(user_input)
            cleaned[CONF_TOKEN] = cleaned[CONF_TOKEN].strip()
            cleaned[CONF_AUTH_MODE] = cleaned.get(CONF_AUTH_MODE, DEFAULT_AUTH_MODE)
            cleaned[CONF_DEVICE_ID] = (cleaned.get(CONF_DEVICE_ID) or "").strip()
            cleaned[CONF_SCAN_INTERVAL] = max(int(cleaned.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)), MIN_SCAN_INTERVAL)
            cleaned[CONF_INCLUDE_PROJECT] = bool(cleaned.get(CONF_INCLUDE_PROJECT, DEFAULT_INCLUDE_PROJECT))

            try:
                info = await _validate_input(self.hass, cleaned)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(info["user_identifier"])
                self._abort_if_unique_id_configured(updates=cleaned)
                return self.async_create_entry(title=info["title"], data=cleaned)

        schema = vol.Schema(
            {
                vol.Required(CONF_AUTH_MODE, default=DEFAULT_AUTH_MODE): vol.In(AUTH_MODES),
                vol.Required(CONF_TOKEN): str,
                vol.Optional(CONF_DEVICE_ID, default=""): str,
                vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(vol.Coerce(int), vol.Range(min=MIN_SCAN_INTERVAL)),
                vol.Optional(CONF_INCLUDE_PROJECT, default=DEFAULT_INCLUDE_PROJECT): bool,
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Create the options flow."""
        return AnycubicCloudConnectOptionsFlow(config_entry)


class AnycubicCloudConnectOptionsFlow(config_entries.OptionsFlow):
    """Handle Anycubic Cloud Connect options."""

    def __init__(self, config_entry) -> None:
        self.config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        """Manage options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        data = self.config_entry.data
        options = self.config_entry.options
        schema = vol.Schema(
            {
                vol.Optional(
                    CONF_SCAN_INTERVAL,
                    default=options.get(CONF_SCAN_INTERVAL, data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)),
                ): vol.All(vol.Coerce(int), vol.Range(min=MIN_SCAN_INTERVAL)),
                vol.Optional(
                    CONF_INCLUDE_PROJECT,
                    default=options.get(CONF_INCLUDE_PROJECT, data.get(CONF_INCLUDE_PROJECT, DEFAULT_INCLUDE_PROJECT)),
                ): bool,
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
