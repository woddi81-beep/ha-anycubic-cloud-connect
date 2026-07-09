# Anycubic Cloud Connect fuer Home Assistant

Benutzerdefinierte Home-Assistant-Integration zum Ueberwachen und Steuern von Anycubic-3D-Druckern ueber die Anycubic Cloud.

**Sprachen:** [English](README.md) | [Deutsch](README.de.md) | [Francais](README.fr.md)

## Funktionen

- Einrichtung ueber die Home-Assistant-Oberflaeche.
- Cloud-Abfrage ueber `anycubic-cloud-mcp`.
- Sensoren fuer Status, Fortschritt, Temperaturen, Zeiten, Layer, Luefter, Geschwindigkeit und ACE.
- Binary-Sensoren fuer Online, Beschaeftigt, Druckt, Pausiert und ACE-Trocknung.
- Buttons fuer Pause, Fortsetzen, Abbrechen und Aktualisieren.
- ACE-Auto-Feed-Schalter und ACE-Services.
- Dokumentation auf Englisch, Deutsch und Franzoesisch. UI-Uebersetzungen fuer Englisch, Deutsch, Franzoesisch und Russisch.

## Installation mit HACS

1. HACS in Home Assistant oeffnen.
2. Im Drei-Punkte-Menue **Custom repositories** waehlen.
3. Diese Repository-URL eintragen:

   ```text
   https://github.com/woddi81-beep/ha-anycubic-cloud-connect
   ```
4. Als Kategorie **Integration** waehlen.
5. **Anycubic Cloud Connect** installieren.
6. Home Assistant neu starten.
7. Unter **Einstellungen → Geraete & Dienste → Integration hinzufuegen → Anycubic Cloud Connect** einrichten.

Die Repository-Metadaten fuer Dokumentation, Issues und Code Owner stehen in `custom_components/anycubic_cloud_connect/manifest.json`.

## Manuelle Installation

Diesen Ordner kopieren:

```text
custom_components/anycubic_cloud_connect
```

nach:

```text
/config/custom_components/anycubic_cloud_connect
```

Danach Home Assistant neu starten und die Integration in der Oberflaeche hinzufuegen.

## Authentifizierung

Die Integration unterstuetzt diese Modi:

- `slicer`: empfohlen; nutzt den Access Token aus Anycubic Slicer Next.
- `web`: Token aus der Anycubic-Cloud-Weboberflaeche; nur REST-Abfrage.
- `android`: Mobile-App-API-Modus; benoetigt `device_id`.

Tokens, Diagnosen mit Secrets, lokale Logs und Home-Assistant-Backups gehoeren nie ins Git-Repository.

## Slicer-Next-Token finden

Unter Windows liegt die Konfiguration von Anycubic Slicer Next haeufig hier:

```text
%AppData%\AnycubicSlicerNext\AnycubicSlicerNext.conf
```

Verwendet wird der Wert von `access_token`.

## Entities

Typische Entities:

- `sensor.<drucker>_status`
- `sensor.<drucker>_print_progress`
- `sensor.<drucker>_nozzle_temperature`
- `sensor.<drucker>_bed_temperature`
- `sensor.<drucker>_remaining_time`
- `sensor.<drucker>_current_layer`
- `binary_sensor.<drucker>_online`
- `binary_sensor.<drucker>_printing`
- `button.<drucker>_pause_print`
- `button.<drucker>_resume_print`
- `button.<drucker>_cancel_print`
- `button.<drucker>_refresh`

Die exakten Entity-IDs haengen vom Druckernamen ab, den die Anycubic Cloud liefert.

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

Beispiel:

```yaml
service: anycubic_cloud_connect.pause_print
data:
  printer_id: 123456
```

## Einschraenkungen

- Dies ist eine inoffizielle Cloud-Integration, keine lokale LAN-Integration.
- Anycubic kann das Cloud-Verhalten ohne Vorankuendigung aendern.
- Befehle haengen von Druckermodell, Firmware und Cloud-Rechten ab.
- Das Polling-Intervall sollte nicht zu kurz gewaehlt werden, um Rate Limits zu vermeiden.

## Entwicklung

Vor der Veroeffentlichung einfache Checks ausfuehren:

```bash
python -m compileall custom_components
python -m json.tool hacs.json
python -m json.tool custom_components/anycubic_cloud_connect/manifest.json
```

GitHub Actions fuer HACS- und hassfest-Validierung sind enthalten.

## Attribution

Dieses Repository-Paket basiert auf der Community-Integration `IceSlam/ha-anycubic-cloud-connect` und behaelt die urspruengliche GPL-3.0-or-later-Lizenz bei.
