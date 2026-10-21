# Physical Controls Mapping (PM decision 2026-10-21)
Hardware: **Action** (distinctive tactile; push-to-talk), **Power**, **Volume +**, **Volume −**, **mic-mute slide switch** with **hardware-wired mic LED**. No Back button, no encoder.
Back = on-screen ‹ button (top-left of every non-root screen) or left-edge swipe. Dialogs: Cancel button only (no swipe-dismiss on destructive/consent dialogs).

## Global
| Control | Press | Long-press (≥0.8 s) | Double-press |
|---|---|---|---|
| Action | tap: start listening, tap again to send (toggle) | hold-to-talk: records while held; release = send | quick voice note (saved to Memory, no answer) |
| Power | screen sleep/wake | 2 s: power menu (Shut down / Restart / Airplane mode / Lock) · 10 s: **hardware cut** — the low-power MCU (independent of the CM5) opens the power path and puts the charger into **ship mode** (battery disconnected); wake by USB-C plug-in **or** Power press (confirmed). Works even if Linux is hung; unsaved data may be lost | lock now |
| Vol + / − | speaker volume (default) or screen role per table below | auto-repeat (scroll/step faster) | — |
| Vol + and − together (chord, confirmed; 80 ms window) | activate focused item ("select") | 3 s: toggle mute of speaker | — |
| Power + Vol − at boot | enter Recovery (19) | | |
| Mic-mute switch | hardware cuts mic power: LED red, status pill "MIC MUTED", Action press shows toast "Mic muted — slide switch to enable" | | |

Volume keys stay speaker volume during listening/response audio playback and whenever no list/focus exists; holding Vol for a speaker change on list screens is via the system volume overlay (swipe down from status bar).

## Per screen
| Screen | Action | Vol ± | Back |
|---|---|---|---|
| 00 Onboarding | try a question | speaker | on-screen Back button (no swipe on step 1) |
| 01 Home (root) | hold: talk | move focus over tiles · both: open | — (Power = sleep) |
| 02 Listening | release/tap: send | speaker | Cancel button (discards audio) |
| 03 Processing | press: interrupt, new ask | speaker | Cancel button |
| 04 Response | follow-up | scroll | ‹ / swipe → Home |
| 05 Capture | hold: voice note | move focus | ‹ / swipe |
| 06 Memory search | voice query | select result · both: open | ‹ / swipe |
| 07 Memory detail | ask about this | seek ±5 s | ‹ / swipe |
| 08 OCR / photo capture | shutter | zoom | ‹ / swipe (cancel) |
| 09 OCR result / 09b Photo result | ask about it | scroll | ‹ / swipe (retake) |
| 10 Tasks | add by voice | select · both: toggle done | ‹ / swipe |
| 11 Task create | dictate title | adjust time (15 min steps) | ‹ / swipe (cancel, confirm if edited) |
| 11b Keyboard | hold: dictate into field | move cursor | ‹ / swipe (keeps draft) |
| 12 Privacy, 13 Data, 13b Export | disabled (no recording on privacy screens) | select · both: toggle | ‹ / swipe |
| 12b Cloud consent, 14 Delete confirm | ignored | speaker | Cancel / Keep local only (destructive needs 1.5 s on-screen hold) |
| 15 Battery / 15b Low battery | ask | speaker | ‹ / Dismiss |

## Mic / recording indication
- Mic LED wired in hardware to the mic power/record line: green = recording, red = muted, off = idle. Software cannot light "idle" while recording.
- Screen: status pill always visible; "● REC" green only during capture; full listening ring.
- No recording without a deliberate Action press; no wake word in MVP. Cancelled audio discarded immediately.
- Camera active only with live preview on screen.

## Additional screens
| Screen | Action | Vol ± | Notes |
|---|---|---|---|
| 00a–00g Onboarding | 00f: hold to try | select · chord: Continue | on-screen Back button |
| 11c Hindi keyboard (phonetic, default) / 11d InScript (optional) | hold: dictate Hindi | cursor | language key toggles EN / हि; type "kal" gives कल; InScript enabled in Settings › Display › Keyboard |
| 16 Settings / 16b Theme | ask | select · chord: open | |
| 17 Power menu | — | select · chord: choose | opened by Power 2 s |
| 18b Update progress | locked | locked | Power 10 s still force-offs; A/B rollback |
| 19 Recovery | — | select · chord: run | primary input; touch may be unavailable |
| 19b Factory reset | — | **hold Vol− 3 s** with on-screen countdown; release cancels | no touch needed |

## Battery thresholds (approved)
20% battery saver + amber icon · 10% low-battery warning (15b) + red icon · 3% save & safe shutdown.
| 13c Export lockout | — | — | after 5 wrong PINs: 30 s, 1 m, 5 m, 15 m, 1 h; never wipes |
| 20a–20h Errors | ask (if mic ok) | select · chord: choose | ‹ / swipe = first (safe) button |
| 03b Cloud slow cue | interrupt | speaker | auto-falls back at 4 s |
| 16g Wi-Fi password | — | cursor | |
| 16h–16j BT pairing | — | select · chord: pair; on 16j Vol = earbud volume | |
| 20j Free up space | — | select · chord: toggle | delete uses hold-confirm |
| 21 Diagnostics | press: mic test | select | |
