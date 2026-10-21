# PocketMate Navigation Flows
Hub-and-spoke: Home is the hub; depth ≤ 3. Action (PTT) works from every screen (context-aware) unless muted or on privacy screens. Back = on-screen ‹ or left-edge swipe, up one level.

```mermaid
flowchart TD
  OB1[00a Welcome] --> OB2[00b Language] --> OB3[00c Wi-Fi] --> OB4[00d Privacy] --> OB5[00e Cloud choices] --> OB6[00f Controls] --> OB7[00g Done] --> H[01 Home]
  H --> SE[16 Settings] --> TH[16b Theme]
  SE -->|About & updates| UA[18a Update] --> UP[18b Installing] --> UD[18c Done]
  ANY2((Power 2 s)) -.-> PM[17 Power menu]
  BOOT((Power+Vol− at boot / 3 failed boots)) -.-> RC[19 Recovery]
  C -->|keyboard lang key| HK[11c Hindi keyboard]
  H -->|Action hold| L[02 Listening]
  L -->|release| P[03 Processing]
  L -->|Cancel| H
  P -->|done| A[04 Response]
  P -->|cloud feature, first use| CC[12b Cloud consent]
  CC -->|Allow / Keep local| P
  A -->|source chip| MD[07 Memory detail]
  A -->|Action follow-up| L
  H --> C[05 Capture]
  C -->|Voice note| L
  C -->|Typed note| KB[11b Keyboard]
  C -->|Scan text| OC[08 Camera]
  C -->|Photo| OC
  OC -->|OCR| OR[09 OCR result]
  OC -->|Photo| PH[09b Photo result]
  PH -->|Ask cloud for more| CC
  OR -->|Remind| TC[11 Task create]
  H --> MS[06 Memory search]
  MS --> MD
  MD -->|Delete…| DC[14 Delete confirm]
  H --> T[10 Tasks] --> TC
  H --> PR[12 Privacy]
  PR -->|enable cloud feature| CC
  PR --> DR[13 My data]
  DR --> EX[13b Export]
  DR -->|Delete…| DC
  H -.status bar battery tap.-> BA[15 Battery]
  ANY((any screen)) -.≤10%.-> LB[15b Low battery]
  PR -->|Revoke| RV[12c Revoke confirm] -->|provider delete request| PR
  PR -->|feature log| CL[12d Cloud log]
  EX -->|5 wrong PINs| LO[13c Lockout]
  EX -->|Choose…| PP[13d Passphrase]
  SE --> WF[16c Wi-Fi]
  SE --> BT[16d Bluetooth]
  SE --> DS[16e Display]
  SE --> AB[16f About]
  RC -->|Factory reset| FR[19b Hold Vol− 3 s]
  P -.no reply 1.85 s.-> PC[03b Cloud slow cue] -.4 s.-> E2[20b fallback]
  WF --> WP[16g Wi-Fi password]
  BT --> BS[16h Pair scan] --> BC[16i Confirm] --> BD[16j Connected]
  E -->|storage| FS[20j Free up space]
  E -->|mic/camera| DG[21 Diagnostics]
  AB --> LG[16k Legal]
  UD --> WN[18d What's new]
  H -.evening / Memory.-> DS2[22 Daily summary] -->|source| MD
  C -->|Translate| TR[09c Camera translate]
  ERR((any failure)) -.-> E[20a–h Error states]
```

## Key flows
1. **Onboarding** (7 steps): welcome → language (EN/हि) → Wi-Fi (skippable) → privacy summary → cloud choices (all off) → controls tutorial (try Action) → done.
2. **Ask**: hold Action → Listening → Processing → Response with source chips + Undo/Edit for actions taken.
3. **Cloud consent**: generic "Send this to <provider> cloud?" dialog on first use per feature; the answer is remembered per feature. Privacy › Cloud permissions lists granted features with date and Revoke (revoking returns to Not allowed; next use asks again). CLOUD badge persists while any grant exists.
4. **Capture**: voice note (Action hold), typed note (11b keyboard, Action-hold dictation), photo (09b on-device description; optional cloud detail via consent), scan (09 OCR → Save/Remind/Discard).
5. **Recall**: Memory → query → "Based on N sources" → detail (play/edit/delete).
6. **Tasks**: list → New/dictate → Save.
7. **Data**: Privacy → My data (counts, cloud log, auto-delete Never [default]/30/90/365 d) → Export: an AES-256 encrypted zip (Markdown+JSON+media). The **zip password is a random 4-word passphrase generated on device and shown once** on the Export screen (user writes it down; never stored or sent). Delivery: USB mass storage, or Wi-Fi HTTPS (self-signed cert, fingerprint shown) — scan QR → accept cert → enter 6-digit PIN; 1 device, 10 min expiry or Delete (hold-to-confirm).
8. **Power**: battery tap → 15; ≤10% → 15b warning; ≤3% → save + safe shutdown; Power long-press → power menu.
9. **Settings**: theme (Auto via ambient light sensor ~2,000/200 lux with 10 s hysteresis, Dark, Light), Wi-Fi, Bluetooth, language, display, about & updates.
10. **Update**: available (signed, verified, needs ≥30% or charger) → install to B slot with progress → reboot → done; automatic rollback on failure.
11. **Recovery**: Power+Vol− at boot or 3 failed boots → rollback / repair storage / encrypted USB export / factory reset (hold-to-confirm), controlled by volume keys.
12. **Revoke**: Privacy › Revoke → 12c confirm → device sends provider deletion request where the API supports it; result shows "Delete request sent" or "Provider doesn't support deletion". Failed deletes retry with backoff for 7 days; deletions, retries and failures are recorded in the Cloud log. Log retention follows auto-delete with a 30-day minimum. Per-feature Cloud log (12d) shows when, what, size, status.
13. **Export passphrase**: generated 4-word passphrase (↻ New regenerates) or Choose… (13d, min 12 chars / 4 words, confirm). Never stored.
14. **PIN lockout**: 5 failures → 30 s, then 1 m, 5 m, 15 m, 1 h (13c); no wipe; lockout ladder resets after a successful download or a new PIN.
15. **Errors** (20a–h): icon + title + plain cause + safe fallback (left) + fix (right). No network, cloud unreachable (4 s timeout, cue at 1.85 s, on-device fallback), mic, camera, storage full (90% warn banner, 97% full → 20j Free up space), OCR no text, update rolled back, thermal (warm 70 °C, throttle 75 °C, shutdown 85 °C, target <65 °C).
16. **Updates**: A/B slots ~8.25 GiB each (4 GB RAM variant), ~5.25 GiB (2 GB variant). Confirmed.
17. **Bluetooth (MVP = earbuds audio only; keyboards v2)**: Settings › Bluetooth › Pair → 16h scan (audio devices only) → 16i confirm code → 16j connected, audio routed; PocketMate mics stay in use.
18. **Free up space** (20j): suggested categories with sizes, Export first, Delete selected (hold-confirm via 14 pattern).
19. **Diagnostics** (21): mic L/R, speaker, camera, touch, battery, storage; local report without personal data.
20. **Daily summary** (22, CR1): evening recap (default 20:00, also from Memory) of notes, tasks, reminders and scans; each item links to its source (07/10/09); Action asks a follow-up; missed reminders flagged red.
21. **Camera translate** (09c, CR1): live overlay Devanagari ↔ English, direction toggle, Freeze (pauses frame) → Save to Memory as scan + translation; LOCAL on-device by default, CLOUD badge only if the translate feature is granted (consent 12b).
