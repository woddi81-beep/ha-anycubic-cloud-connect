"""Constants for the Anycubic Cloud Connect Home Assistant integration."""

from __future__ import annotations

from datetime import timedelta
from typing import Final

DOMAIN: Final = "anycubic_cloud_connect"

CONF_AUTH_MODE: Final = "auth_mode"
CONF_TOKEN: Final = "token"
CONF_DEVICE_ID: Final = "device_id"
CONF_SCAN_INTERVAL: Final = "scan_interval"
CONF_INCLUDE_PROJECT: Final = "include_project"
CONF_PRINTER_ID: Final = "printer_id"
CONF_BOX_ID: Final = "box_id"
CONF_SLOT_INDEX: Final = "slot_index"
CONF_MATERIAL_TYPE: Final = "material_type"
CONF_RED: Final = "red"
CONF_GREEN: Final = "green"
CONF_BLUE: Final = "blue"
CONF_TARGET_TEMP: Final = "target_temp"
CONF_DURATION: Final = "duration"

AUTH_MODE_WEB: Final = "web"
AUTH_MODE_SLICER: Final = "slicer"
AUTH_MODE_ANDROID: Final = "android"
AUTH_MODES: Final = [AUTH_MODE_SLICER, AUTH_MODE_WEB, AUTH_MODE_ANDROID]

DEFAULT_AUTH_MODE: Final = AUTH_MODE_SLICER
DEFAULT_SCAN_INTERVAL: Final = 60
MIN_SCAN_INTERVAL: Final = 30
DEFAULT_INCLUDE_PROJECT: Final = True
DEFAULT_DRYING_TEMP: Final = 45
DEFAULT_DRYING_DURATION: Final = 3600

UPDATE_INTERVAL: Final = timedelta(seconds=DEFAULT_SCAN_INTERVAL)

PLATFORMS: Final = ["sensor", "binary_sensor", "button", "switch"]

SERVICE_PAUSE_PRINT: Final = "pause_print"
SERVICE_RESUME_PRINT: Final = "resume_print"
SERVICE_CANCEL_PRINT: Final = "cancel_print"
SERVICE_ACE_FEED_FILAMENT: Final = "ace_feed_filament"
SERVICE_ACE_RETRACT_FILAMENT: Final = "ace_retract_filament"
SERVICE_ACE_SET_AUTO_FEED: Final = "ace_set_auto_feed"
SERVICE_ACE_SET_SLOT: Final = "ace_set_slot"
SERVICE_ACE_DRY_START: Final = "ace_dry_start"
SERVICE_ACE_DRY_STOP: Final = "ace_dry_stop"

ATTR_ORDER_MESSAGE_ID: Final = "order_message_id"
