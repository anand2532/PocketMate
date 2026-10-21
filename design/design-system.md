# PocketMate Design System (MVP, 800×480, 4.3" IPS ≈ 217 ppi)
Source of truth for wireframes: `gen.py` (regenerates svg/, png/, overview.png). Target: Qt/QML.

## Grid & layout
- 8 px base unit; 16 px outer margins; 16 px gutters (tiles: 3 cols × 248 px).
- Fixed zones: **Status bar** 0–40 (time · mic state pill centered · LOCAL/CLOUD · battery) | **Content** 40–424 | **Hint bar** 424–480 (back gesture · volume-key role · Action-key role).
- Back: on-screen ‹ button (56×56, top-left) on every non-root screen + left-edge swipe (start ≤24 px from edge, ≥80 px travel). Dialogs use explicit Cancel buttons.
- Focus ring (2 px accent outline) marks the item that the volume keys select.
- Max 6 primary targets per screen; one primary (accent) action per screen.

## Type (DejaVu Sans / Inter in production), min 15 px
| Token | px | Use |
|---|---|---|
| display | 30 bold | state labels (Listening/Thinking) |
| h1 | 28 bold | screen title |
| h2 | 22–24 bold | card titles, tiles |
| body | 18–20 | content, buttons (20 semibold) |
| caption | 15–16 | meta, sources, hints |

## Color tokens: high-contrast Dark (default) and Light
| Token | Dark | Light | Use |
|---|---|---|---|
| bg | #0F1115 | #FFFFFF | screen |
| surface | #1A1D23 | #F1F3F5 | cards, rows |
| surface2 | #252932 | #E2E6EA | buttons, fields |
| text | #E8EAED | #0B0D10 | primary text (≥15:1) |
| text2 | #A8AEB4 | #3C434B | secondary text (≥7:1, WCAG AAA) |
| accent | #4C8DFF | #0B57D0 | primary action, focus ring, links |
| on-accent | #FFFFFF | #FFFFFF | text on accent/state fills |
| state.listening | #2ECC71 | #0A7A3B | live mic / REC |
| state.processing + cloud | #F5A623 | #9A5B00 | thinking, CLOUD badge, cloud toggles |
| state.error/destructive/muted | #FF5A5F | #C5221F | errors, delete, MIC MUTED, low battery |
| chrome | #000000 | #E2E6EA | status + hint bars |
| line | #3A3F48 | #6B737C | outlines |
Theme: Settings › Theme — Auto (ambient light sensor: Light >~2,000 lux, Dark <~200 lux, 10 s hysteresis), Dark (default), Light. Light is for outdoor/sunlight use. Rendered light variants: 01-home, 04-response, 06-memory-search, 12-privacy (`*-light`), plus 16-settings.
State colors are always paired with a text label (never color-only).

## Touch targets
- Min 48×48 px; standard button height 56 px; list rows 50–64 px; tiles 248×124. ≥8 px between targets.
- Destructive confirm = hold-to-confirm (1.5 s progress bar) — works with gloves and prevents accidental taps.

## States
Mic: READY (grey pill) · ● REC (green, only while capturing) · MUTED (red, from hardware switch). Processing: amber ring + progress + "local model"/"cloud" label. Error: red text + retry. Cloud: OFF by default. While **any** cloud feature is enabled, an amber CLOUD badge stays in the status bar at all times (not only during calls); otherwise it shows LOCAL. Battery: green fill; amber at ≤20%, red at ≤10%, ⚡ when charging.

## Icon list (24 px line, 2 px stroke)
mic, mic-off, waveform, spinner, speaker, camera, scan-text, note, photo, search, source-link, play/pause, task-check, bell/reminder, repeat, calendar, shield/privacy, cloud, cloud-off, lock, export-usb, trash, edit, undo, back-chevron, battery(0–100, charging), wifi, bluetooth, settings, power.

## Scripts
Latin: DejaVu Sans (Inter in production). Devanagari: Noto Sans Devanagari, same sizes (+1 px for matras at ≤16 px). Keyboard: EN QWERTY; Hindi **phonetic transliteration (default)** with a collapsible single-row suggestion bar (4 candidates + ⌄ collapse, 48 px; phonetic only), InScript optional (Settings › Display); language key bottom row. Keyboard keys 56 px.

## Error pattern
Icon ring (red = failure, amber = degraded/recoverable) · title ≤ 30 chars · 1–2 lines cause + consequence · left button = safe fallback, right (accent) = fix. Thermal: sustained target <65 °C · 70 °C 'Device warm' banner · 75 °C throttle (20h) · 85 °C safe shutdown. Storage: 90% amber banner · 97% full (recordings paused, 20e). Banners: 44 px, amber outline, top of content, tappable (20i).

## Cloud timing
Cloud request timeout 4 s. At 1.85 s with no reply, the processing screen shows an amber cue "Slow network · on-device answer in 2 s" (03b); at 4 s, falls back on device and shows 20b.
