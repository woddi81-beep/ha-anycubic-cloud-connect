"""Sensor entities for Anycubic Cloud Connect."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorEntityDescription, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfTemperature, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from .coordinator import AnycubicCloudDataUpdateCoordinator
from .entity import AnycubicCloudEntity
from .const import DOMAIN


STATUS_OPTIONS = [
    "available",
    "busy",
    "printing",
    "paused",
    "finished",
    "failed",
    "downloading",
    "checking",
    "preheating",
    "slicing",
    "offline",
    "unknown",
]

_STATUS_ALIASES = {
    "complete": "finished",
    "completed": "finished",
    "cancelled": "failed",
    "canceled": "failed",
    "failure": "failed",
    "error": "failed",
    "idle": "available",
    "ready": "available",
}


@dataclass(frozen=True, kw_only=True)
class AnycubicSensorEntityDescription(SensorEntityDescription):
    """Describes an Anycubic sensor."""

    value_fn: Callable[[Any], StateType]
    attrs_fn: Callable[[Any], dict[str, Any] | None] | None = None


def _normalize_status(value: Any) -> str | None:
    """Normalize Anycubic status values to enum states known by Home Assistant."""
    if value is None:
        return None

    status = str(value).strip().lower().replace(" ", "_").replace("-", "_")
    status = _STATUS_ALIASES.get(status, status)
    return status if status in STATUS_OPTIONS else "unknown"


def _project_status(printer) -> str | None:
    """Return a stable enum status value; frontend translations render it in the selected language."""
    return _normalize_status(printer.latest_project_print_status or printer.current_status)


def _project_status_attrs(printer) -> dict[str, Any]:
    """Return raw status details as attributes for diagnostics and automations."""
    return {
        "raw_print_status": printer.latest_project_raw_print_status,
        "status_message": printer.latest_project_print_status_message,
    }


def _round_or_none(value: Any, ndigits: int = 2) -> StateType:
    if value is None:
        return None
    try:
        return round(float(value), ndigits)
    except (TypeError, ValueError):
        return None


SENSOR_DESCRIPTIONS: tuple[AnycubicSensorEntityDescription, ...] = (
    AnycubicSensorEntityDescription(
        key="status",
        translation_key="status",
        device_class=SensorDeviceClass.ENUM,
        options=STATUS_OPTIONS,
        icon="mdi:printer-3d",
        value_fn=_project_status,
        attrs_fn=_project_status_attrs,
    ),
    AnycubicSensorEntityDescription(
        key="print_progress",
        translation_key="print_progress",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:progress-clock",
        value_fn=lambda p: p.latest_project_progress_percentage,
    ),
    AnycubicSensorEntityDescription(
        key="download_progress",
        translation_key="download_progress",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:download",
        value_fn=lambda p: p.latest_project_download_progress_percentage,
    ),
    AnycubicSensorEntityDescription(
        key="nozzle_temperature",
        translation_key="nozzle_temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda p: p.curr_nozzle_temp,
    ),
    AnycubicSensorEntityDescription(
        key="bed_temperature",
        translation_key="bed_temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda p: p.curr_hotbed_temp,
    ),
    AnycubicSensorEntityDescription(
        key="remaining_time",
        translation_key="remaining_time",
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.MINUTES,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:timer-sand",
        value_fn=lambda p: p.latest_project_print_time_remaining_minutes,
    ),
    AnycubicSensorEntityDescription(
        key="elapsed_time",
        translation_key="elapsed_time",
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.MINUTES,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:timer-outline",
        value_fn=lambda p: p.latest_project_print_time_elapsed_minutes,
    ),
    AnycubicSensorEntityDescription(
        key="current_layer",
        translation_key="current_layer",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:layers-triple-outline",
        value_fn=lambda p: p.latest_project_print_current_layer,
    ),
    AnycubicSensorEntityDescription(
        key="total_layers",
        translation_key="total_layers",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:layers-triple",
        value_fn=lambda p: p.latest_project_print_total_layers,
    ),
    AnycubicSensorEntityDescription(
        key="print_speed",
        translation_key="print_speed",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:speedometer",
        value_fn=lambda p: p.latest_project_print_speed_pct,
    ),
    AnycubicSensorEntityDescription(
        key="fan_speed",
        translation_key="fan_speed",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:fan",
        value_fn=lambda p: p.latest_project_fan_speed_pct,
    ),
    AnycubicSensorEntityDescription(
        key="print_count",
        translation_key="print_count",
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:counter",
        value_fn=lambda p: p.print_count,
    ),
    AnycubicSensorEntityDescription(
        key="total_print_time",
        translation_key="total_print_time",
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.HOURS,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:history",
        value_fn=lambda p: p.total_print_time_hrs,
    ),
    AnycubicSensorEntityDescription(
        key="ace_temperature",
        translation_key="ace_temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermometer",
        value_fn=lambda p: p.primary_multi_color_box_current_temperature,
    ),
    AnycubicSensorEntityDescription(
        key="ace_drying_remaining",
        translation_key="ace_drying_remaining",
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:timer-sand",
        value_fn=lambda p: p.primary_drying_status_remaining_time,
    ),
    AnycubicSensorEntityDescription(
        key="ace_drying_target_temperature",
        translation_key="ace_drying_target_temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermometer-lines",
        value_fn=lambda p: p.primary_drying_status_target_temperature,
    ),
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up Anycubic sensors from a config entry."""
    coordinator: AnycubicCloudDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[AnycubicSensor] = []
    for printer_id in coordinator.data or {}:
        entities.extend(AnycubicSensor(coordinator, printer_id, description) for description in SENSOR_DESCRIPTIONS)
    async_add_entities(entities)


class AnycubicSensor(AnycubicCloudEntity, SensorEntity):
    """Anycubic Cloud sensor."""

    entity_description: AnycubicSensorEntityDescription

    def __init__(
        self,
        coordinator: AnycubicCloudDataUpdateCoordinator,
        printer_id: int,
        description: AnycubicSensorEntityDescription,
    ) -> None:
        super().__init__(coordinator, printer_id, description.key)
        self.entity_description = description

    @property
    def native_value(self) -> StateType:
        """Return sensor value."""
        printer = self.printer
        if printer is None:
            return None
        return self.entity_description.value_fn(printer)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return sensor attributes."""
        printer = self.printer
        attrs = super().extra_state_attributes or {}
        if printer is None:
            return attrs
        if self.entity_description.attrs_fn:
            attrs.update(self.entity_description.attrs_fn(printer) or {})
        return attrs
