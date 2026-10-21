# PocketMate UX — FROZEN for prototype (2026-10-21)
UX is frozen for the prototype build. Changes after this point go through PM change request. Regenerate with `python3 gen.py` (needs cairosvg, Pillow, DejaVu Sans, Noto Sans Devanagari).

## Docs
- `design-system.md`: grid, type, dark/light high-contrast tokens, auto theme, touch targets, states, error/banner pattern, cloud timing, scripts, icons
- `flows.md`: navigation and the mermaid diagram, 19 key flows
- `controls.md`: Action / Power / Vol± / chord / mic-mute switch mapping per screen, force-off (MCU + ship mode), battery thresholds
- `overview.png`: contact sheet; `svg/` + `png/`: 800×480 per screen

## Screens (68)
- 00a-ob-welcome
- 00b-ob-language
- 00c-ob-wifi
- 00d-ob-privacy
- 00e-ob-cloud
- 00f-ob-controls
- 00g-ob-done
- 01-home
- 01-home-light
- 02-ptt-listening
- 03-processing
- 03b-processing-cloud
- 04-response
- 04-response-light
- 05-capture
- 06-memory-search
- 06-memory-search-light
- 07-memory-detail
- 08-ocr-capture
- 09-ocr-result
- 09b-photo-result
- 10-tasks-list
- 11-task-create
- 11b-keyboard
- 11c-keyboard-hindi
- 11d-keyboard-inscript
- 12-privacy
- 12-privacy-light
- 12b-cloud-consent
- 12c-revoke-confirm
- 12d-cloud-log
- 13-data-review
- 13b-export
- 13c-export-lockout
- 13d-export-passphrase
- 14-delete-confirm
- 15-battery
- 15b-low-battery
- 16-settings
- 16-settings-light
- 16b-settings-theme
- 16c-settings-wifi
- 16d-settings-bluetooth
- 16e-settings-display
- 16f-settings-about
- 16g-wifi-password
- 16h-bt-pair-scan
- 16i-bt-pair-confirm
- 16j-bt-paired
- 16k-legal
- 17-power-menu
- 18a-update-available
- 18b-update-progress
- 18c-update-done
- 18d-whats-new
- 19-recovery
- 19b-recovery-reset
- 20a-err-no-network
- 20b-err-cloud-unreachable
- 20c-err-mic
- 20d-err-camera
- 20e-err-storage-full
- 20f-err-ocr-no-text
- 20g-err-update-failed
- 20h-err-thermal
- 20i-warn-banners
- 20j-free-up-space
- 21-diagnostics

## Locked parameters
Battery 20/10/3% · thermal 70/75/85 °C (target <65 °C) · storage 90/97% · cloud timeout 4 s, cue 1.85 s · PIN lockout 5 tries then 30 s→1 m→5 m→15 m→1 h (resets on download/new PIN, no wipe) · provider delete retry 7 days · cloud log ≥30 days · BT earbuds MVP, keyboards v2.

## Pending (not blocking prototype)
1. A/B update slot size (~6 GB each): **pending Software confirmation** (shown on 16f About).
2. Hindi phonetic transliteration engine: choice, footprint, and candidate quality for the suggestion bar.
3. `<provider>` cloud provider name and its deletion-API support.
