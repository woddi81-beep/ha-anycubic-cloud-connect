# Anycubic Cloud Connect pour Home Assistant

Integration personnalisee Home Assistant pour surveiller et controler des imprimantes 3D Anycubic via Anycubic Cloud.

**Langues :** [English](README.md) | [Deutsch](README.de.md) | [Francais](README.fr.md)

## Fonctionnalites

- Configuration depuis l'interface Home Assistant.
- Interrogation cloud via `anycubic-cloud-mcp`.
- Capteurs pour statut, progression, temperatures, temps, couches, ventilateur, vitesse et ACE.
- Capteurs binaires pour en ligne, occupe, impression, pause et sechage ACE.
- Boutons pause, reprendre, annuler et actualiser.
- Interrupteurs ACE auto-feed et services ACE.
- Documentation en anglais, allemand et francais. Traductions UI en anglais, allemand, francais et russe.

## Installation avec HACS

1. Ouvrir HACS dans Home Assistant.
2. Ouvrir le menu a trois points et choisir **Custom repositories**.
3. Ajouter cette URL de depot :

   ```text
   https://github.com/woddi81-beep/ha-anycubic-cloud-connect
   ```
4. Choisir la categorie **Integration**.
5. Installer **Anycubic Cloud Connect**.
6. Redemarrer Home Assistant.
7. Aller dans **Parametres → Appareils et services → Ajouter une integration → Anycubic Cloud Connect**.

Les metadonnees du depot pour documentation, issues et code owner sont definies dans `custom_components/anycubic_cloud_connect/manifest.json`.

## Installation manuelle

Copier ce dossier :

```text
custom_components/anycubic_cloud_connect
```

vers :

```text
/config/custom_components/anycubic_cloud_connect
```

Redemarrez Home Assistant puis ajoutez l'integration depuis l'interface.

## Authentification

L'integration accepte ces modes :

- `slicer` : recommande ; utilise le jeton d'acces d'Anycubic Slicer Next.
- `web` : jeton de l'interface web Anycubic Cloud ; interrogation REST uniquement.
- `android` : mode API mobile ; necessite `device_id`.

Ne committez jamais de jetons, diagnostics contenant des secrets, journaux locaux ou sauvegardes Home Assistant.

## Recuperer un jeton Slicer Next

Sous Windows, Anycubic Slicer Next stocke souvent sa configuration ici :

```text
%AppData%\AnycubicSlicerNext\AnycubicSlicerNext.conf
```

Utilisez la valeur de `access_token`.

## Entites

Entites courantes :

- `sensor.<imprimante>_status`
- `sensor.<imprimante>_print_progress`
- `sensor.<imprimante>_nozzle_temperature`
- `sensor.<imprimante>_bed_temperature`
- `sensor.<imprimante>_remaining_time`
- `sensor.<imprimante>_current_layer`
- `binary_sensor.<imprimante>_online`
- `binary_sensor.<imprimante>_printing`
- `button.<imprimante>_pause_print`
- `button.<imprimante>_resume_print`
- `button.<imprimante>_cancel_print`
- `button.<imprimante>_refresh`

Les identifiants exacts dependent du nom d'imprimante renvoye par Anycubic Cloud.

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

Exemple :

```yaml
service: anycubic_cloud_connect.pause_print
data:
  printer_id: 123456
```

## Limites

- Il s'agit d'une integration cloud non officielle, pas d'une integration LAN locale.
- Anycubic peut modifier le comportement du cloud sans preavis.
- Les commandes dependent du modele, du firmware et des autorisations cloud.
- Gardez un intervalle d'interrogation raisonnable pour eviter les limites de debit.

## Developpement

Executer ces controles avant publication :

```bash
python -m compileall custom_components
python -m json.tool hacs.json
python -m json.tool custom_components/anycubic_cloud_connect/manifest.json
```

Les GitHub Actions pour HACS et hassfest sont incluses.

## Attribution

Ce paquet de depot est base sur l'integration communautaire `IceSlam/ha-anycubic-cloud-connect` et conserve la licence GPL-3.0-or-later d'origine.
