# Contributing

Thanks for considering a contribution.

## Development workflow

1. Fork the repository.
2. Create a feature branch.
3. Make your changes under `custom_components/anycubic_cloud_connect/`.
4. Run basic checks:

   ```bash
   python -m compileall custom_components/anycubic_cloud_connect
   python -m json.tool hacs.json >/dev/null
   python -m json.tool custom_components/anycubic_cloud_connect/manifest.json >/dev/null
   ```

5. Open a pull request and describe what changed.

## Reporting issues

Please include:

- Home Assistant version.
- Integration version.
- Printer model and firmware.
- Auth mode used: `slicer`, `web`, or `android`.
- Sanitized debug logs.
- Diagnostics downloaded from Home Assistant.

Never post tokens, cookies, or raw diagnostics that contain secrets.
