# Anycubic Cloud Connect for Home Assistant

Home Assistant custom integration for monitoring and controlling Anycubic 3D printers through Anycubic Cloud.

**Languages:** [English](README.md) | [Deutsch](README.de.md) | [Francais](README.fr.md)

## Features

- UI setup through Home Assistant integrations.
- Cloud polling through `anycubic-cloud-mcp`.
- Printer status, progress, temperatures, time, layers, fan, speed and ACE sensors.
- Online, busy, printing, paused and ACE drying binary sensors.
- Pause, resume, cancel and refresh buttons.
- ACE auto-feed switches and ACE-related services.
- English, German and French documentation. UI translations include English, German, French and Russian.

## Installation with HACS

1. Open HACS in Home Assistant.
2. Open the three-dot menu and choose **Custom repositories**.
3. Add this repository URL:

   ```text
   https://github.com/woddi81-beep/ha-anycubic-cloud-connect
   ```
4. Select category **Integration**.
5. Install **Anycubic Cloud Connect**.
6. Restart Home Assistant.
7. Go to **Settings → Devices & services → Add integration → Anycubic Cloud Connect**.

The repository metadata for documentation, issues and code owner is set in `custom_components/anycubic_cloud_connect/manifest.json`.

## Manual Installation

Copy this directory:

```text
custom_components/anycubic_cloud_connect
```

to your Home Assistant configuration:

```text
/config/custom_components/anycubic_cloud_connect
```

Restart Home Assistant and add the integration from the UI.

## Authentication

The integration accepts these modes:

- `slicer`: recommended; use the Anycubic Slicer Next access token.
- `web`: token from the Anycubic Cloud web UI; REST polling only.
- `android`: mobile API mode; requires `device_id`.

Never commit tokens, diagnostics with secrets, local logs or Home Assistant backups.

## Getting a Slicer Next Token

On Windows, Anycubic Slicer Next commonly stores its configuration here:

```text
%AppData%\AnycubicSlicerNext\AnycubicSlicerNext.conf
```

Use the value of `access_token`.

## Entities

Common entities include:

- `sensor.<printer>_status`
- `sensor.<printer>_print_progress`
- `sensor.<printer>_nozzle_temperature`
- `sensor.<printer>_bed_temperature`
- `sensor.<printer>_remaining_time`
- `sensor.<printer>_current_layer`
- `binary_sensor.<printer>_online`
- `binary_sensor.<printer>_printing`
- `button.<printer>_pause_print`
- `button.<printer>_resume_print`
- `button.<printer>_cancel_print`
- `button.<printer>_refresh`

Exact entity IDs depend on the printer name reported by Anycubic Cloud.

## Services

- `anycubic_cloud_connect.pause_print`
- `anycubic_cloud_connect.resume_print`
- `anycubic_cloud_connect.cancel_print`
- `anycubic_cloud_connect.ace_feed_filament`
- `anycubic_cloud_connect.ace_retract_filament`
- `anycubic_cloud_connect.ace_set_auto_feed`
- `anycubic_cloud_connect.ace_set_slot`
- `anycubic_cloud_connect.ace_dry_start`
- `anycubic_cloud_connect.ace_dry_stop`

Example:

```yaml
service: anycubic_cloud_connect.pause_print
data:
  printer_id: 123456
```

## Limitations

- This is an unofficial cloud integration, not a local LAN integration.
- Anycubic Cloud behavior can change without notice.
- Command support depends on printer model, firmware and cloud permissions.
- Keep the polling interval reasonable to avoid cloud rate limits.

## Development

Run basic checks before publishing:

```bash
python -m compileall custom_components
python -m json.tool hacs.json
python -m json.tool custom_components/anycubic_cloud_connect/manifest.json
```

GitHub Actions for HACS and hassfest validation are included.

## Attribution

This repository package is based on the community integration `IceSlam/ha-anycubic-cloud-connect` and keeps the original GPL-3.0-or-later license.
