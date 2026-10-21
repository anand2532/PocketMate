# PocketMate — Software Architecture v0.3.12

Status: final v0.3.12 (baseline) · Owner: software · Source of truth for requirements: `../docs/PRD.md`, plus PM decisions and research (`../research/market.md` §6–7, `../research/bom.md` §7–8)
Tag conventions:
- **[PRD]**: stated in the PRD.
- **[PM 2026-10-21]**: a PM decision or requirement dated 2026-10-21.
- **[Research]**: taken from `../research/*.md`.
- **[A-n]**: an assumption made by this doc. Each one needs confirmation (§16).
- **⚠ FEASIBILITY**: a target that looks hard or infeasible with the chosen models or hardware. Each is collected in §14.1.

### PM decisions incorporated (v0.2 + v0.3) [PM 2026-10-21]
| Topic | Decision | Where |
|---|---|---|
| Display | 4.3" 800×480, landscape | §3, §4 |
| Battery | **~3.6 Ah cell (8.5×51×65.5 mm) in the 125×75×22 mm passive v4_22 body** [PM/Enclosure 2026-10-21]. This supersedes 2.7 Ah / 20 mm. Target: 16 h mixed use + ≥ 24 h standby with the CM5 fully off and the MCU holding. ~9 W system cap for the 1C prototype cell | §10.2–10.5 |
| Low-power MCU | **STM32U031K8** (UFQFPN-32) [Schematic netlist v3]. Prototype uses NUCLEO-U031R8 | §11, §12, B2, B3 |
| Languages | English + Hindi at launch. Hinglish (code-mixed) is a known risk | §6.2, §6.4, §6.5, §6.9 |
| ASR | Default is IndicWhisper or a Hinglish Whisper fine-tune on-device. Sarvam is the opt-in cloud ASR adapter | §6.2, §6.7, §6.10 |
| OCR | Default is PaddleOCR or IndicPhotoOCR, replacing Tesseract | §6.4 |
| Camera translation | Indian-script camera translation is **MVP feature #4** | §6.8, §9.2 |
| Daily summary | Evening recap of notes, tasks and reminders, generated locally | §9.1 |
| Cloud | Off by default. Pluggable provider interface with no vendor lock-in | §6.7 |
| Haptics | **LRA is DNP (footprint only) on the PCB and not part of the MVP UX** (v0.3). The firmware `null` driver hook stays | §11, §12 |
| Retention | Data is kept until the user sets auto-delete. No default expiry | §7, §8 |
| Updates | RAUC bundles published as GitHub Releases assets. Anand holds the signing keys | §2.2 |
| Latency | Feedback < 100 ms; local actions ≤ 750 ms; progress cue before 1.85 s; cloud answers capped at 4 s | §14, B5 |
| Thermal | CM5 sustained < 65 °C. Skin ≤ 43 °C sustained at 35 °C ambient; at 45 °C ambient, ≤ Ta+3 °C sustained and ≤ 48 °C peak. Skin-temperature governor. JEITA charging only within 10–40 °C | §10.4, §12, B5 |
| SKUs | 2 GB runs qwen2.5-0.5B. **Cloud is off by default with per-request consent, and a notice that Hinglish works best with cloud** (v0.3). 4 GB runs the full local stack | §6.11 |
| Search | Every search result opens its source note, audio timestamp, or photo | §7.1, B5 |
| UX | The UI is built against the frozen 68-screen spec (`../design/README.md`). UX pending items 1–3 are closed here | §2.1, §4, §6.7, §6.12 |
| Transliteration | Hindi phonetic typing and cross-script search | §6.12 |
| **v0.3** UX | UX is adding screens **22-daily-summary** and **09c-translate-overlay** and fixing **16f** (slot size from §2.1) | §4, §9.1, §9.2 |
| **v0.3** Battery claim | 16 h accepted for light use, **marketed as "all-day typical use"**, to be validated after benchmarks | §10.3 |
| **v0.3** Operating range | **Rated 0–40 °C; limited use at 45 °C** | §10.4 |
| **v0.3** Hinglish fallback | If no small Hinglish model passes §6.10, the fallback is **cloud with per-request consent** (Sarvam) | §6.2, §6.10 |
| **v0.3** Releases | The existing GitHub repo (`anand2532/PocketMate`, publicly readable: unauthenticated API returned 200 on 2026-10-21) with signed GitHub Releases | §2.2 |
| **v0.3** Keys | Anand is the sole custodian, with an offline backup and a documented recovery procedure | §2.2.1 |
| **v0.3** Providers | Sarvam first. OpenAI and Gemini are optional plug-ins. Retention and deletion terms researched | §6.7.1 |
| **v0.3** Scripts | **Devanagari only for MVP.** Tamil, Bengali and Telugu are planned for v2 | §6.4, §6.8, §9.2 |
| **v0.3.1** Cloud account model | **Bring-your-own API key per user. No PocketMate proxy or account in MVP.** Keys are entered on the device and stored only in the LUKS data partition | §6.7, §6.7.1 |
| **v0.3.1** Consent dialog | Consent dialog 12b must show **each provider's retention and training terms** | §8.3, §6.7.1 |
| **v0.3.1** Sarvam | The adapter defaults to the **training opt-out** wherever the API/account allows it. **Sarvam DPA is a pre-launch action for Anand.** Until then, terms remain unconfirmed | §6.7.1 |
| **v0.3.2** Compute | **v1 = CM5 4 GB only. The 2 GB SKU is deferred and not part of v1.** Measured CM5 idle 2.4–2.65 W exceeds the ~1.6–1.75 W passive budget, so **the CM5 is OFF by default** and sessions are duty-cycled. Aggressive power policy. s2idle test with a decision rule. Rev-2 Radxa CM5 (RK3588S2, RKNN) portability | §10.0, §10.3, §10.3b, §10.6, §10.7, §17 |
| **v0.3.11** [Tech Research 2026-10-21, v0.3.11] | A-78 resolved: prototype = Akyga LP655063 (3000 mAh, 1C, ≤ 65.5 × 51 × 7.0 mm, 10k NTC β unstated); production = custom cell per battery-rfq.md Rev C (≥ 3000/3100 mAh, ≥ 2C, 3C/10 s, ≤ 8.5 × 50.5 × 62 mm, 10k B3435). Pocket/spacer fit, runtime table, NTC windows and M5b divider recompute values | §10.2, B2, B4, §16 |
| **v0.3.10** [Schematic netlist v3.2] [Tech Research 2026-10-21] | Final mic wiring: SW5 → MIC_SW_LIVE → U14 → MIC_FEED → mics + green D6 (green = mics powered, exactly); red D1 from SW5's muted throw; MUTE_STATUS_IO via Q6 inverter, valid only with CM5 power-good; J11 pin 11/15 changes. Charge thresholds + NTC β configurable in MCU config flash; M5b β measurement. Production cell corrected to 3000 mAh (RFQ) | §5, §8, §10.2, §12, B3, B4, B5, §16 |
| **v0.3.9** [Schematic netlist v3.1] | **REC interlock implemented**: `MIC_PWR_EN` = PA11 → U14 TPS22917 → MIC_FEED → SW5 → mics; green REC LED D6 on MIC_FEED. MIC_ENABLE accepted | §8, §11, §12, B2, B3, B5, §16 |
| **v0.3.8** [Schematic netlist v3] [PM 2026-10-21, v0.3.8] | +3V3_PERIPH = buck U12 enabled by CM5_3V3 (A-70 resolved). MCU = **STM32U031K8** (QFN-32, 64 KB/12 KB), prototype NUCLEO-U031R8. Case NTC on PB0 with PA12-switched bias (A-72 resolved); cell NTC → BQ25895 TS, read via TSPCT. Mic interlock rewritten around DPDT SW5 (REC LED + MIC_PWR_EN added in v0.3.9). Cells: prototype Akyga LP655063, production custom 2C ~3.2 Ah (A-67 resolved) | §8, §10.2–10.4, §11, §12, B2, B3, B5, §16 |
| **v0.3.7** [Schematic netlist v3] | Bus map confirmed (v0.3.6 items retagged). STUSB4500 at 0x28 (A-69 address part resolved). Mic-mute status on CM5 GPIO17 + MCU PA10 (high = muted), used in the privacy interlock. Buttons active-low: PWR PA0/WKUP1, ACTION (PTT) PA1/WKUP3, VOL+ PA4, VOL− PA5. Mics/display/camera on +3V3_PERIPH, which is only on with the CM5 up | §3, §5, §8, §11, §12, B3, B5, §16 |
| **v0.3.6** [Schematic netlist v3] | VEML7700, BQ25895, MAX17055 and STUSB4500 on STM32U0 I2C1 (PB6/PB7, always-on 3V3). Link is CM5 UART0 (GPIO14/15) ↔ MCU USART2, with `MCU_IRQ_N` on CM5 GPIO4. DRV2605L (DNP) on CM5 I2C1 (GPIO2/3). A-66 resolved; I2C address map added; protocol opcode collisions fixed (0x27/0x28) | §3, §10.4.3, §11, §12, B3, §16 |
| **v0.3.5** [Enclosure 2026-10-21] | A-64 confirmed for the prototype (thresholds on the compensated hot spot, intentionally double-counting lag; relax after M5b). Prototype cell LP755060 (superseded in v0.3.8 by LP655063; 3.0 Ah nominal, below the 3.6 Ah budget; runtime impact flagged). VEML7700 light sensor: pocket detection + auto-brightness; A-65 resolved, no proximity sensor in v1 | §10.2–10.4, B2, B5, §16 |
| **v0.3.4** Baseline [PM/Enclosure 2026-10-21] | **Passive, fan-free 22 mm aluminium enclosure v4_22** (the micro blower is not baseline; only an unused fan hook remains). **~3.6 Ah cell.** **CM5-off-by-default is the core strategy.** **Radxa rev 2 is unfunded until after M5b.** Frozen governor limits and stages, case NTC on the STM32U0, battery NTC to charger JEITA, case detection heuristic, external Wi-Fi FPC antenna (`dtparam=ant2`) | §3, §10.3–10.4, §11, §17, B4 |
| **v0.3.3** Compute decision [Anand 2026-10-21] | **Stay on Raspberry Pi CM5 (4 GB) for v1.** The body may grow to **22–26 mm** for cooling. **Keep driving idle power down**, because every watt saved keeps the body thinner. Radxa CM5 stays a rev-2 option only (§17) | §10.0, §10.3c, §10.8 |
| **v0.3.1** Keys | No emergency key designee for now | §2.2.1 |
| **v0.3** Audio | Audio is not stored by default, only transcripts. Audio saving is opt-in | §8.1 P6, §7 |

---
## 0. Scope and design principles

- Target: Raspberry Pi CM5 4 GB [PRD]; CM4 is the alternate [PRD] and must keep working with reduced models (§6.6).
- MVP features [PRD]: push-to-talk assistant with listening/processing indicators; voice and typed notes stored locally; searchable memory with source-linked answers; camera OCR; basic image understanding (local or cloud); reminders, daily tasks, action-item extraction; offline notes, docs, and utilities; configurable local/cloud; physical mic mute; data review/export/edit/delete; battery monitoring; reliable sleep/wake; controlled shutdown. Added by PM [PM 2026-10-21]: **camera OCR + translation for Indian scripts (MVP #4)**, **daily summary** (opt-in evening recap), and English + Hindi/Hinglish at launch.
- Principles:
  1. **Local-first.** Every MVP feature has to work offline. Cloud is an optional adapter used one request at a time with consent.
  2. **No covert capture.** The mic and camera only open on an explicit user action, and the indicator is driven from a hardware-backed path.
  3. **Fast feedback over big models.** The first visual or audio response comes within 300 ms of PTT (§14). Small models are the default.
  4. **Crash isolation.** Each heavy engine runs in its own process. The UI never blocks on inference.
  5. **Recoverable.** A/B rootfs, signed updates, a recovery image, and user data on a separate partition.

---

## 1. System overview

```
 ┌──────────────────────────── CM5 (Linux, aarch64) ─────────────────────────────┐
 │  pm-ui (Qt6/QML, C++)  ◄──── D-Bus (session/system) + Unix socket streams ────┐ │
 │        ▲                                                                       │ │
 │        │ events/state                                                          │ │
 │  pm-core (orchestrator, Python) ── intents, dialog, tools, consent gate ──────┤ │
 │     │        │         │          │           │            │                  │ │
 │  pm-audio  pm-asr   pm-llm     pm-ocr      pm-tts      pm-memory  pm-remind    │ │
 │  (capture, (Indic   (llama.cpp (Paddle/    (Piper)     (SQLite    (scheduler)  │ │
 │   PTT,VAD)  whisper) server)    IndicOCR)                FTS5+vec)              │ │
 │                                                                               │ │
 │  pm-power (power state machine) ◄── UART ──► Low-power MCU (STM32U0)          │ │
 │  pm-cloud (optional, consent-gated egress)   pm-update (A/B, RAUC)             │ │
 └──────────────────────────────────────────────────────────────────────────────┘
        MCU: buttons, PTT, mic-mute sense, LED, fuel gauge, charger, RTC, power rail
```

---

## 2. OS image

| Item | Decision |
|---|---|
| Base | Raspberry Pi OS Lite (Bookworm or newer) 64-bit, built reproducibly with **pi-gen** at first. The plan is to move to **Yocto (meta-raspberrypi + meta-rauc)** before the custom PCB [A-1]. Rationale: pi-gen is the fastest path to a prototype, and Yocto gives a minimal, reproducible, signed product image. |
| Kernel | RPi vendor kernel 6.6+ LTS, arm64, 16K pages default on CM5 (validate llama.cpp/sqlite-vec builds) |
| Init | systemd. Every pm-* service is a unit with `Restart=on-failure`, `MemoryMax=`, `CPUWeight=`, plus sandboxing (`ProtectSystem=strict`, `PrivateNetwork=yes` for all engines except pm-cloud/pm-update) |
| Display stack | Qt6 on **EGLFS/KMS** (no X/Wayland compositor) using the vc4-kms-v3d driver. Fallback: `cage` kiosk Wayland if multi-window is ever needed |
| Audio | PipeWire (or plain ALSA for minimal footprint [A-2]), with ALSA plugin for the I2S mic/amp |
| Camera | libcamera + picamera2 (Python) for capture; IMX708 autofocus module [A-3] |
| Networking | NetworkManager (Wi-Fi/BT). nftables default-deny egress except for the `pm-cloud` and `pm-update` UIDs |
| Users | `pm` (UI), one system user per service, no login shell. SSH disabled in production and enabled only in dev builds |
| Logging | journald with volatile+persistent caps (50 MB). User content (transcripts, text) is **never** logged. Log scrubber unit tests enforce this |
| Time | chrony with the MCU RTC as the fallback source at boot (§11) |

### 2.1 Partition layout — eMMC and A/B slot sizes [closes UX pending item 1]

**eMMC: 32 GB on both SKUs** (CM5104032 / CM5102032 [Research]). Usable capacity is ≈ 29.1 GiB. microSD is for dev only (the 2 GB Lite + microSD variant is not planned).

An **"update slot" = boot + rootfs + models** for one slot. All three are A/B, so a model pack and a system update roll back together.

| # | Partition | FS | **cm5-4g (v1)** | **cm5-2g (deferred, not v1)** | Mount / notes |
|---|---|---|---|---|---|
| 1 | boot-A | FAT32 | 256 MiB | 256 MiB | /boot/firmware (kernel, DTB, overlays) |
| 2 | boot-B | FAT32 | 256 MiB | 256 MiB | |
| 3 | rootfs-A | ext4 ro (squashfs+verity in Yocto) | 3.0 GiB | 3.0 GiB | / (OS + Qt + services ≈ 1.6–2.0 GiB, ~40 % headroom) |
| 4 | rootfs-B | same | 3.0 GiB | 3.0 GiB | |
| 5 | models-A | ext4 ro | 5.0 GiB | 2.0 GiB | /opt/pm/models (4g pack ≈ 3.5–4.8 GiB incl. 3B "quality" LLM; 2g pack ≈ 1.2–1.5 GiB) |
| 6 | models-B | same | 5.0 GiB | 2.0 GiB | |
| 7 | recovery | squashfs | 512 MiB | 512 MiB | recovery UI (screens 19/19b) |
| 8 | data | ext4 on LUKS2 | **≈ 11.6 GiB** | **≈ 17.6 GiB** | /var/lib/pm (DB, media, settings, logs) |
| | **A/B update slot** (boot+rootfs+models) | | **≈ 8.25 GiB each** | **≈ 5.25 GiB each** | **value for screen 16f About** (UX said "~6 GB": correct to these figures) |

- GPT with the partition table on eMMC. Partition sizes are fixed at the factory and can't be resized in the field, so headroom has been built in. If the 4G model pack grows past 5 GiB, the fix is a smaller default model, not repartitioning.
- Data sizing check: a 4 GB-SKU user storing 2 photos per day (~1.5 MB after downscale) plus text, for 3 years, needs ≈ 3.5 GiB. That fits. The storage warnings at 90/97 % are locked UX parameters.
- `tryboot` / autoboot.txt handles A/B bootloader slot selection on CM5. The bootloader EEPROM is updated only through signed rpi-eeprom images.
- Data encryption key: LUKS2 keyslot sealed with a device secret through the CM5 OTP / secure-boot chain [A-4]. An optional user PIN adds a second keyslot. The PIN lockout follows the locked UX parameters. In dev builds the key file lives on boot-A, which is acceptable for dev only.

### 2.2 A/B signed updates and recovery

- Tool: **RAUC** (signed bundles with X.509 and CMS, verity format, A/B slot handling, adaptive delta). Alternative considered: SWUpdate. RAUC was picked for its simpler Yocto integration and verity bundles.
- Bundle types: `system` (boot+rootfs), `models`, and `mcu-firmware` (a signed STM32U0 image that pm-power flashes through the MCU's own UART bootloader; see §12).
- **Distribution [PM 2026-10-21]: GitHub Releases** on `anand2532/PocketMate`.
  - Each release carries these assets: `pocketmate-system-<ver>-<sku>.raucb`, `pocketmate-models-<ver>-<sku>.raucb`, `pocketmate-mcu-<ver>.raucb`, and `manifest.json` (version, min-from-version, sha256 per asset, SKU, release notes URL) with `manifest.json.sig`.
  - `pm-update` checks `https://api.github.com/repos/anand2532/PocketMate/releases/latest` when the user taps "Check for updates", or on a weekly schedule if auto-check is enabled in Settings (off until the user opts in, so in Local mode no packets leave the device by default). It downloads the assets over HTTPS and resumes with HTTP Range.
  - **GitHub is a transport only and is not trusted for integrity.** The device trusts only the RAUC CMS signature, verified against the keyring baked into rootfs, plus the manifest signature. A compromised GitHub account can't push a bootable image without the signing key.
  - Unauthenticated API limit: 60 requests/h per IP, which is enough. The repo is publicly readable (checked 2026-10-21) [PM 2026-10-21, v0.3]. If it ever goes private, release assets must move to a public mirror, because devices hold no GitHub token.
  - Anti-rollback: the manifest carries `security_version`. `pm-update` refuses a lower value than the one stored in `/var/lib/pm/update.state` (and in OTP later [A-4]).
- **Signing-key custody [PM 2026-10-21, v0.3]: Anand is the sole custodian, with an offline backup.** The two-level PKI below stays. The recovery procedure is in §2.2.1.
  - Two-level PKI:
    - **Root CA** (offline): generated on an air-gapped machine and stored on two hardware tokens (e.g., YubiKey/Nitrokey PIV/PKCS#11) plus one paper/encrypted-USB backup kept in a separate location. Used only to sign intermediates.
    - **Release signing cert** (intermediate, 1–2 y validity): kept on a hardware token held by Anand. RAUC signs through PKCS#11, so the key never leaves the token.
    - **Dev cert**: a separate CA. Production keyrings don't contain it, so dev builds can't install on production devices.
  - Never put keys in the repo, in GitHub Actions secrets, or on the box. CI builds an *unsigned* bundle. Anand signs it locally (`rauc resign` / `rauc bundle --signing-keyring`), then uploads it to the release.
  - Rotation and revocation: the keyring holds the root. Intermediates are revoked with a CRL shipped in the next update. If the root is lost, devices can only be recovered through USB recovery with physical access. This is documented and accepted.
  - Sole-custodian risk is accepted [PM 2026-10-21]. See R6 in §2.2.1.
- Flow: download → verify the manifest signature and sha256 → `rauc install` (verifies the CMS signature) → write to the inactive slot → mark it "try" → reboot → health check by `pm-health.service` within 120 s (UI up, pm-core responding, DB open, MCU link OK) → `rauc status mark-good`. Otherwise the watchdog or the boot counter (3 tries) falls back to the previous slot.
- Updates never run below 30 % battery unless charging, never during an active recording, and never above skin-governor stage T2 (§10.4).
- Recovery partition entry: hold Volume-Down + Power for 5 s at boot (the MCU detects it and sets the boot-mode flag over UART) [A-6], or after 3 failed boots on both slots. Recovery offers: reinstall from USB-C mass storage or a USB stick, factory reset (cryptographic wipe = destroy LUKS keyslots), and export data to USB (requires PIN).

---

### 2.2.1 Signing-key custody and recovery procedure [PM 2026-10-21, v0.3]

**Assets** (all held by Anand):

| Asset | Where | Protection |
|---|---|---|
| K-root: root CA private key (ed25519 or P-256), 10 y | **Offline backup only**. Encrypted file (age, passphrase ≥ 6 diceware words) on **two** USB drives. Drive A at home, drive B off-site (e.g., a bank locker / trusted family location). Plus a paper copy of the passphrase in a sealed envelope stored with drive B | Never connected to a networked machine. Used only on an offline laptop/live-USB |
| K-rel: release signing key + cert (intermediate), 2 y | Hardware token T1 (YubiKey/Nitrokey PIV, PIN + touch), plus an encrypted backup of the key on the same offline USB drives | PIN retry limit; touch required per signature |
| K-mcu: MCU firmware ed25519 key | same pattern as K-rel (a separate slot on T1 plus offline backup) | |
| Keyring (public root cert, CRL) | in rootfs `/etc/rauc/keyring.pem` and in the repo `software/os/keys/public/` | public |
| Custody record | `software/os/keys/CUSTODY.md` in the repo (fingerprints, serials, validity, locations described generically, last-verified date). **No secrets** | |

**Routine release signing**:
1. CI builds an unsigned bundle and publishes its sha256.
2. Anand verifies the sha256 on his machine.
3. `rauc resign` / `rauc bundle` with PKCS#11 against T1 (PIN + touch).
4. Sign `manifest.json`.
5. Upload to the GitHub Release.
6. Run a smoke install on the prototype.

**Recovery scenarios**:

| Scenario | Procedure | Device impact |
|---|---|---|
| **R1. T1 lost, stolen or broken** (K-rel compromise possible) | (1) Boot the offline laptop and decrypt K-root from drive A (or B). (2) Revoke the old K-rel: add its serial to the CRL, signed by K-root. (3) Generate a new K-rel on a new token T1′, issue its cert with K-root, back it up encrypted to both drives. (4) Ship the next release signed by the new K-rel and containing the new CRL. Devices accept it because they trust K-root and reject the old K-rel from then on. (5) Update CUSTODY.md. | none; next update carries the CRL |
| **R2. T1 PIN forgotten / locked** | as R1, without revocation if there's no compromise. Restore K-rel from the encrypted offline backup onto a new token, or issue a new one | none |
| **R3. One backup drive lost** | Assess it as a possible exposure (still passphrase-protected). Re-encrypt K-root with a **new passphrase** onto two new drives, destroy the old ones. If compromise is suspected → R5 | none |
| **R4. Release key expiry** (planned) | 60 days before expiry: issue a new K-rel with K-root offline. Both certs are valid in parallel for one release cycle | none |
| **R5. K-root compromised or both backups lost** | Cannot be fixed over the air. (1) Generate a new root. (2) If the old root is still under control, ship a final "keyring transition" bundle signed by the old chain that installs the new keyring. (3) If it's lost: devices can only be updated through **USB recovery with physical access** (recovery partition, signed by the factory/dev procedure), or by a factory re-flash. Documented and accepted risk | high |
| **R6. Anand unavailable** (sole-custodian risk) | No one else can sign releases. Accepted per PM. **No emergency designee for now** [PM 2026-10-21, v0.3.1]. Devices keep working without updates. The sealed envelope with drive B carries only Anand's own recovery notes | updates paused |

**Annual drill**: verify both drives decrypt on the offline laptop, verify the T1 PIN, verify fingerprints against CUSTODY.md, re-sign a test bundle with a test key, and record the date.

---

## 3. Device tree / config.txt (prototype on CM5 IO Board)

```ini
# /boot/firmware/config.txt (prototype)
arm_64bit=1
dtoverlay=vc4-kms-v3d
# Display [PM 2026-10-21]: 4.3" 800x480 DSI capacitive panel, landscape (prototype: Waveshare 4.3" DSI; overlay per vendor, e.g. vc4-kms-dsi-waveshare-panel,4_3_inch)
dtoverlay=vc4-kms-dsi-waveshare-panel,4_3_inch,dsi1
# Camera (IMX708 / Camera Module 3, CAM1 port)
camera_auto_detect=0
dtoverlay=imx708,cam1
# I2S audio: mic + amp
dtparam=i2s=on
dtoverlay=googlevoicehat-soundcard          # stand-in for 2x I2S MEMS + MAX98357A; final: custom overlay
# MCU link [Schematic netlist v3]: CM5 UART0 on GPIO14 (TXD) / GPIO15 (RXD) <-> STM32U0 USART2
dtparam=uart0=on                 # UART0 on GPIO14/15 (/dev/ttyAMA0); no Linux console on it
enable_uart=0                    # cmdline.txt must have no console=serial0 / ttyAMA0 entry; serial-getty@ttyAMA0 masked
# CM5 I2C1 on GPIO2/3: DRV2605L haptic driver only (DNP in MVP), 0x5A. Not the battery/sensor bus.
dtparam=i2c_arm=on
dtparam=i2c_arm_baudrate=400000
# MCU_IRQ_N on GPIO4 (active-low, open-drain from the MCU, 10k pull-up to CM5 3V3; pull is in the custom overlay)
#   used as a gpio-keys IRQ/wake source (see pocketmate-carrier overlay below); no gpio-shutdown overlay
# MIC_MUTE on GPIO17 [Schematic netlist v3]: input, high = muted (no pull: driven by the switch circuit). GPIO17 is reserved for this;
#   nothing else may claim it (no gpio-shutdown, no gpio-fan, no LED overlay on 17)
# Wi-Fi/BT: external FPC antenna on the CM5 U.FL connector [PM/Enclosure 2026-10-21]
dtparam=ant2
# Hardware watchdog
dtparam=watchdog=on
# RTC: CM5 has an on-board RTC (needs backup battery on VBAT); MCU RTC is secondary
```

Custom overlay `pocketmate-carrier.dtbo` (for the custom PCB) defines: the I2S codec/mic (`simple-audio-card` with 2× MEMS mic, stereo TDM or L/R), amp enable GPIO, MCU UART (`&uart0`, status okay, GPIO14/15 alt0, no console) and **`MCU_IRQ_N` on GPIO4** [Schematic netlist v3]. This is a `gpio-keys` node (`gpios = <&gpio 4 GPIO_ACTIVE_LOW>`, `linux,code = KEY_WAKEUP`, `wakeup-source`) so it can wake from s2idle (§10.7), read by pm-power through evdev. The fallback is libgpiod edge events on gpiochip line 4, if the evdev path is not used. Optional `&i2c1` child `ti,drv2605l@5a` with `status = "disabled"` (DNP), **mic-mute sense on GPIO17** ([Schematic netlist v3]; `gpio-keys` node, `linux,code = SW_MUTE_DEVICE`, `linux,input-type = EV_SW`, active-high, so the state is available as an evdev switch and readable at boot), indicator LED (owned by the MCU, mirrored), and button GPIOs if not routed through the MCU.

---

## 4. UI — Qt6/QML (4.3" 800×480 landscape) [PM 2026-10-21]

- **Process**: `pm-ui`, a C++ host + QML, EGLFS, runs as the `pm` user. Target 60 fps, rendered on the GPU. Startup budget < 3 s after systemd reaches the target (QML precompiled with qmlcachegen / Qt Quick Compiler).
- **Why a C++ host**: lower memory and faster startup than PySide. Business logic stays out of the UI. The UI is a thin client of pm-core over D-Bus (QtDBus).
- **Spec**: the UI is built against the **frozen 68-screen UX spec in `../design/README.md`**, plus the 2 screens being added in v0.3 (22, 09c) (frozen 2026-10-21; changes go through a PM change request). It uses its design tokens (`design-system.md`), flows (`flows.md`) and control mapping (`controls.md`). Locked UX parameters are used as-is: battery 20/10/3 %, thermal 70/75/85 °C with a < 65 °C target, storage 90/97 %, cloud cue at 1.85 s and timeout at 4 s, the PIN lockout ladder, provider-delete retry for 7 days, and cloud log retained ≥ 30 days. UI code is **not** part of this doc.
- **QML module map (high level)**. The `-light` variants are not separate screens: they come from the `PocketMate.Design` theme (dark/light/auto).

| QML module | Frozen screens | Backed by |
|---|---|---|
| `PocketMate.Design` (tokens, theme, fonts EN+Devanagari) + `PocketMate.Components` (buttons, banners, lists, hold-confirm, source chip) | all; 20i warn banners | — |
| `PocketMate.Onboarding` | 00a–00g | pm-core settings, pm-cloud (00e: all off) |
| `PocketMate.Assistant` | 01 home, 02 PTT listening, 03 processing, 03b processing-cloud, 04 response | pm-audio, pm-asr, pm-core, pm-llm, pm-tts |
| `PocketMate.Capture` | 05 capture | pm-core, pm-memory |
| `PocketMate.Memory` | 06 search, 07 detail (source note / audio timestamp / photo) | pm-memory |
| `PocketMate.Camera` | 08 OCR capture, 09 OCR result, 09b photo result, **09c translate overlay** (v0.3) | pm-ocr, pm-vision, pm-translate |
| `PocketMate.Tasks` | 10 tasks list, 11 task create | pm-remind |
| `PocketMate.Input` (Qt Virtual Keyboard custom layouts + transliteration suggestion bar) | 11b keyboard, 11c Hindi phonetic, 11d InScript | pm-xlit (§6.12) |
| `PocketMate.Privacy` | 12 privacy, 12b cloud consent, 12c revoke confirm, 12d cloud log | pm-core consent gate, pm-cloud, consent_log |
| `PocketMate.Data` | 13 data review, 13b export, 13c lockout, 13d passphrase, 14 delete confirm, 20j free up space | pm-memory |
| `PocketMate.Power` | 15 battery, 15b low battery, 17 power menu | pm-power |
| `PocketMate.Settings` | 16, 16b–16k (theme, Wi-Fi, BT, display, about, Wi-Fi password, BT pair scan/confirm/paired, legal) | NetworkManager, BlueZ, pm-update (16f shows slot size §2.1) |
| `PocketMate.Update` | 18a–18d | pm-update |
| `PocketMate.Feedback` | 20a–20h errors (20h thermal is driven by the skin governor §10.4) | all services |
| `PocketMate.Diagnostics` | 21 | pm-health |
| `PocketMate.Summary` | **22 daily summary** (v0.3) | pm-remind, pm-memory |
| **Recovery UI** (separate minimal Qt app in the recovery partition) | 19, 19b | recovery scripts |

- **v0.3 [PM 2026-10-21]**: UX is adding **22-daily-summary** (module `PocketMate.Summary`, backed by pm-remind/pm-memory, §9.1) and **09c-translate-overlay** (in `PocketMate.Camera`, backed by pm-ocr/pm-translate, §9.2). It is also correcting **16f About** to show the A/B slot sizes from §2.1 (≈ 8.25 GiB on 4 GB, ≈ 5.25 GiB on 2 GB). That brings the spec to 70 screens.
- **2 GB SKU notice** (16f/00e and the first Hinglish use): "Hinglish works best with cloud. Cloud stays off unless you allow each request."
- Accessibility: font scaling, high-contrast theme, TTS readout.

---

## 5. Services and IPC

### 5.1 IPC design
- **Control plane**: **D-Bus system bus** (`org.pocketmate.*`). Typed methods and signals, policy files restrict which UIDs may call what. sd-bus/dbus-next (Python, asyncio) and QtDBus (UI).
- **Data plane (streams)**: Unix domain sockets under `/run/pm/` carrying length-prefixed **msgpack** frames for audio PCM chunks, partial ASR results, and LLM token streams. These avoid D-Bus overhead and the D-Bus message size limit.
- **Large blobs** (images): passed by file path under `/run/pm/blobs/` (tmpfs, mode 0600, per-request ownership). The path is deleted after use.
- Every request carries `request_id` (UUIDv7), `origin` (ui/voice/schedule), and `consent_token` (if cloud).

### 5.2 Service list

| Service | Lang | Responsibilities | Boundary / privileges | Mem budget [A-8] |
|---|---|---|---|---|
| `pm-ui` | C++/QML | Rendering, touch, indicators (mirror), consent dialogs | `pm` user; no network; D-Bus client | 150 MB |
| `pm-core` | Python 3.11 asyncio | Orchestrator: intent routing, dialog state, tool calls (note/search/remind/scan), RAG assembly, action-item extraction, **consent gate**, confirmation of consequential actions | no network; only service allowed to call pm-cloud | 120 MB |
| `pm-audio` | Python + C ext (or C++) | Owns ALSA capture/playback, PTT gating, VAD/endpointing (Silero VAD ONNX or WebRTC VAD), AGC/beamforming lite (2 mics), level meter stream | `audio` group; **only** process that can open capture device (udev ACL); refuses capture if mute switch is on or PTT not held/latched | 60 MB |
| `pm-asr` | Python wrapper over whisper.cpp (C++) | Streaming/segment transcription, language ID | no network, no device access; gets PCM via socket | 250–600 MB |
| `pm-llm` | llama.cpp `llama-server` (C++) + thin Python adapter | Chat/generation, summarization, extraction (JSON-grammar constrained) | no network; models ro | 1.5–2.5 GB |
| `pm-ocr` | Python (PaddleOCR ONNX / IndicPhotoOCR; Tesseract fallback) | Text detection/recognition, script ID, layout blocks | no network | 150–400 MB |
| `pm-translate` | Python + CTranslate2 (IndicTrans2-dist) | Camera/text translation (§6.8, §9.2) | no network; on-demand | 250–400 MB |
| `pm-xlit` | Python + CTranslate2 (IndicXlit) | Roman→Devanagari suggestions, query expansion (§6.12) | no network; resident | 40–60 MB |
| `pm-profile` | Python oneshot | SKU detection, model selection at boot (§6.11) | runs before pm-core | — |
| `pm-vision` | llama.cpp multimodal (mtmd) or ONNX captioner | Basic image understanding (local) | no network; on-demand only | 1–2 GB (exclusive with pm-llm) |
| `pm-tts` | Piper (C++/ONNX) | Speech synthesis, streaming chunks | no network | 80 MB |
| `pm-memory` | Python + SQLite (FTS5, sqlite-vec) | Storage, search, embeddings, retention jobs, export/import | single writer to DB; LUKS data partition | 80 MB |
| `pm-remind` | Python | Reminder/task scheduler, recurrence (RFC 5545 RRULE), hands next wake time to pm-power | | 30 MB |
| `pm-power` | Python | Power state machine, MCU protocol (UART), battery telemetry, **skin-temperature governor + 9 W power cap** (§10.4–10.5), inhibitors, watchdog petting | `dialout`; can call logind | 30 MB |
| `pm-cloud` | Python | Optional cloud adapters (LLM/ASR/vision); TLS 1.3, pinned hosts; **validates consent token** before any egress | only service with general egress (nftables by UID) | 50 MB |
| `pm-update` | RAUC + Python agent | Check/download/install bundles | egress to update host only | 30 MB |
| `pm-health` | Python | Boot health check, service liveness, mark-good | | 20 MB |

**Model residency (4 GB RAM)**: ASR and the LLM do not both stay fully resident on CM4 or in vision mode. pm-core runs a **model scheduler**: the LLM is loaded with mmap (stays in page cache). pm-vision runs exclusively, so the LLM is unloaded first. zram swap is 1 GB (lz4). This is a target to measure, not a guarantee [A-8].

### 5.3 Main voice flow (sequence)
1. MCU detects action-button press → `EVT_BUTTON{PTT,down}` → pm-power → D-Bus signal `PttPressed`.
2. pm-audio checks the mute GPIO (GPIO17, high = muted; if muted it refuses and the UI shows "Mic off (hardware)"). pm-power sends `MIC_ENABLE{on, session_id, max_s}` while ACTION is held (or for a confirmed tap-to-talk session); the MCU drives PA11 high, U14 powers MIC_FEED, and **the green REC LED lights in hardware**. pm-audio waits for `ACK` + `EVT_MIC_RAIL{on}`, shows the on-screen listening overlay (a second indicator), then opens capture.
3. PCM is streamed to pm-asr and partial transcripts are shown live.
4. Button released (hold mode) or VAD end / second press (toggle mode). Capture closes and the LED goes off.
5. pm-core routes the intent. For a question, it runs pm-memory hybrid search → builds a RAG prompt with source ids → pm-llm streams tokens → UI renders them with source chips → optional pm-tts.
6. The transcript, answer, and source links are saved as a `transcript` + `interaction` entry (subject to retention settings).

---

## 6. Modular AI engine interfaces

All engines live in the `pocketmate.engines` package. Backends register through entry points (`pocketmate.engines.asr` etc.) and are selected in `/var/lib/pm/settings.toml`. The core depends only on the Protocols below.

### 6.1 Common types

```python
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import AsyncIterator, Protocol, runtime_checkable, Sequence, Literal
import uuid

class Locality(str, Enum):
    LOCAL = "local"
    CLOUD = "cloud"

@dataclass(frozen=True)
class RequestContext:
    request_id: uuid.UUID
    origin: Literal["voice", "ui", "schedule", "system"]
    locale: str = "en-US"
    deadline_ms: int | None = None
    consent_token: "ConsentToken | None" = None   # required iff backend.locality == CLOUD

@dataclass(frozen=True)
class ConsentToken:
    token_id: uuid.UUID
    scope: Literal["asr", "llm", "ocr", "vision", "tts"]
    request_id: uuid.UUID          # bound to ONE request
    provider: str
    payload_sha256: str            # hash of exactly what the user approved
    expires_at: float              # monotonic deadline, <= 60 s
    signature: bytes               # HMAC by pm-core consent gate key

@dataclass(frozen=True)
class EngineInfo:
    name: str; version: str; locality: Locality
    languages: Sequence[str]; max_input: int | None = None

class EngineError(Exception): ...
class ConsentRequired(EngineError): ...
class Cancelled(EngineError): ...

class Engine(Protocol):
    def info(self) -> EngineInfo: ...
    async def load(self) -> None: ...
    async def unload(self) -> None: ...
    async def health(self) -> bool: ...
```

### 6.2 ASR

```python
@dataclass(frozen=True)
class AudioFormat:
    sample_rate: int = 16_000; channels: int = 1; sample_fmt: Literal["s16le", "f32le"] = "s16le"

@dataclass(frozen=True)
class AudioChunk:
    pcm: bytes; seq: int; t_start_ms: int; is_last: bool = False

@dataclass(frozen=True)
class WordTiming:
    word: str; start_ms: int; end_ms: int; prob: float

@dataclass(frozen=True)
class TranscriptSegment:
    text: str; start_ms: int; end_ms: int
    is_final: bool; confidence: float | None
    language: str | None                     # 'en' | 'hi' | 'hi-en' (code-mixed) | None
    script: Literal["Latn", "Deva", "mixed"] | None = None
    words: Sequence[WordTiming] = ()

@runtime_checkable
class ASREngine(Engine, Protocol):
    def stream(self, ctx: RequestContext, fmt: AudioFormat,
               audio: AsyncIterator[AudioChunk],
               language_hint: Sequence[str] = ("en", "hi")) -> AsyncIterator[TranscriptSegment]:
        """Yields partial (is_final=False) and final segments. Must honour cancellation."""
    async def transcribe(self, ctx: RequestContext, fmt: AudioFormat, pcm: bytes,
                         language_hint: Sequence[str] = ("en", "hi")) -> list[TranscriptSegment]: ...
```

**Launch languages: English + Hindi [PM 2026-10-21]. ASR default: IndicWhisper or a Hinglish Whisper fine-tune, on-device [PM 2026-10-21].**

| Role | Candidate (4 GB SKU) | Notes |
|---|---|---|
| **Final transcript (default)** | Hindi/Hinglish-fine-tuned Whisper converted to ggml for whisper.cpp, Q5_0/Q8_0. Candidates: **AI4Bharat IndicWhisper** [Research: best WER on 39/59 Vistaar benchmarks] and a **Hinglish fine-tune** (e.g., Trelis whisper-hinglish-preview [Research: CoSHE WER 13.67 vs Whisper-large-v3 29.74, vendor-run]) | ⚠ FEASIBILITY: IndicWhisper checkpoints are, to my knowledge, *medium*-size (~769 M params). On CM5 that's likely RTF > 1, too slow for interactive use [A-9]. The usable path is a **small (244 M) or base (74 M) sized** Hindi/Hinglish fine-tune, or distilling one. Base size of the Trelis model to be verified. Pick by the §6.10 benchmark |
| English fallback | whisper.cpp `base.en`/`small.en` Q5_1 | used when the user locks the language to English |
| Live partials | **Vosk** `small-en-in` + `small-hi` (~50 MB each) | true streaming. Gives the on-screen live text while the final model runs |
| Fallback if no small model passes §6.10 [PM 2026-10-21, v0.3] | Sarvam cloud ASR **with per-request consent** | local Vosk/whisper is still used for the offline result. Cloud is offered, never automatic |
| 2 GB SKU | Vosk small-hi/en-in + whisper `base`/`tiny` multilingual | Hinglish quality is weak. Cloud is off by default, with the "Hinglish works best with cloud" notice. Sarvam is offered with per-request consent (§6.11) |
| Cloud (opt-in) | **Sarvam** speech-to-text adapter [PM 2026-10-21] (Saaras family [Research: CoSHE 11.47]) | only through pm-cloud with a consent token (§6.7) |

- Pseudo-streaming for Whisper: VAD-segmented chunks are decoded *during* speech (5–8 s windows), so at end of speech only the last chunk remains. This is required for the ≤ 750 ms local-action target (§14).
- **Hinglish / code-mix risk [PM 2026-10-21]**:
  - Stock Whisper roughly doubles WER on Hinglish [Research].
  - Output script is inconsistent: Hindi may come out in Devanagari or romanized, and English words may come out in Devanagari.
  - Language ID on short utterances is unreliable.
  - Mitigations:
    - The user sets a primary language (English / Hindi / Hinglish) in onboarding, which skips LID.
    - Script normalization: store the raw output plus a **romanized shadow** (`indic-transliteration`/ITRANS) and a **Devanagari shadow** for search (§7).
    - Intent grammar and reminder parsing accept both scripts.
    - Test sets include Hinglish (§6.10).

### 6.3 LLM

```python
@dataclass(frozen=True)
class ChatMessage:
    role: Literal["system", "user", "assistant", "tool"]; content: str
    source_ids: Sequence[str] = ()          # memory items cited/injected

@dataclass(frozen=True)
class GenParams:
    max_tokens: int = 256; temperature: float = 0.3; top_p: float = 0.9
    stop: Sequence[str] = (); json_schema: dict | None = None   # → GBNF grammar locally
    seed: int | None = None

@dataclass(frozen=True)
class TokenDelta:
    text: str; finish_reason: Literal["stop", "length", "cancel", None] = None
    usage: dict | None = None               # prompt/completion tokens, t/s

@runtime_checkable
class LLMEngine(Engine, Protocol):
    def generate(self, ctx: RequestContext, messages: Sequence[ChatMessage],
                 params: GenParams) -> AsyncIterator[TokenDelta]: ...
    async def count_tokens(self, text: str) -> int: ...
    @property
    def context_window(self) -> int: ...

@runtime_checkable
class EmbeddingEngine(Engine, Protocol):
    dim: int
    async def embed(self, ctx: RequestContext, texts: Sequence[str]) -> list[list[float]]: ...
```

Local backends: **llama.cpp `llama-server`** (OpenAI-compatible HTTP over a Unix socket, streaming SSE), GGUF Q4_K_M:
- 4 GB SKU candidates [A-11, benchmark in M3]: **Llama-3.2-1B/3B-Instruct** (Hindi is an officially supported language), **Qwen2.5-1.5B-Instruct**, Gemma-3-1B. Expected decode ~8–15 tok/s for 1–1.5B Q4 on CM5 and ~3–6 tok/s for 3B [measure].
- 2 GB SKU: **qwen2.5-0.5B-Instruct** Q4 (~400 MB, ~34 tok/s on Pi 5 2 GB [Research bom.md §8]) [PM 2026-10-21].
- ⚠ FEASIBILITY (prompt processing): on CM5, prefill for a 1–1.5B Q4 model is roughly 50–100 tok/s [A-9, measure]. An 800-token RAG prompt would take 8–16 s before the first token, which breaks every latency target. Mitigations:
  - RAG context capped at about 250 tokens (top-3 snippets, trimmed).
  - System prompt KV cached at boot (`--cache-reuse`, slot save/restore).
  - **Search hits with source links are shown first, at under 300 ms**. The generated answer streams in afterwards.
  - Template-free short prompts for extraction.
- Structured extraction (action items, reminder parsing, daily summary) uses a JSON schema → GBNF grammar, so the output is always parseable.
- Embeddings: **multilingual-e5-small** (384-d, covers Hindi and English) via llama.cpp `--embedding` or ONNX Runtime. Runs in background batches while charging or idle. Disabled on the 2 GB SKU by default.

### 6.4 OCR

```python
@dataclass(frozen=True)
class ImageRef:
    path: str; width: int; height: int; mime: str = "image/jpeg"; sha256: str = ""

@dataclass(frozen=True)
class OCRBlock:
    text: str; bbox: tuple[int, int, int, int]; confidence: float
    kind: Literal["line", "paragraph", "table_cell", "word"] = "line"
    script: str | None = None               # ISO 15924: 'Latn', 'Deva', 'Beng', ...
    language: str | None = None

@dataclass(frozen=True)
class OCRResult:
    blocks: Sequence[OCRBlock]; full_text: str; language: str | None; duration_ms: int

@runtime_checkable
class OCREngine(Engine, Protocol):
    async def recognize(self, ctx: RequestContext, image: ImageRef,
                        langs: Sequence[str] = ("en", "hi"),
                        mode: Literal["document", "scene"] = "document") -> OCRResult: ...
```
- Preprocessing (OpenCV): autofocus capture → document detection/deskew (document mode) → downscale to ~2–3 MP.
- **Scripts [v0.3]: Latin + Devanagari in MVP. Tamil/Bengali/Telugu in v2.** **Default [PM 2026-10-21]: PaddleOCR (PP-OCRv4/v5 mobile, ONNX Runtime) with Latin and Devanagari recognition models** for documents. **IndicPhotoOCR** (Bhashini/IITJ, 11 Indian languages + English [Research]) for scene text such as signs and menus, and for non-Devanagari scripts. A script-ID step routes each detected line to the matching recognizer.
- Tesseract (`eng`+`hin`) is **demoted to a fallback/debug backend** [Research: Tesseract 18.2 % CER vs PaddleOCR 4.5 % on printed Gujarati].
- ⚠ FEASIBILITY: IndicPhotoOCR is a PyTorch research toolkit. CPU latency on CM5 and an ONNX/int8 export path are unverified. If it doesn't run in < 4 s per image, scene mode falls back to PaddleOCR with a consent-gated cloud offer. Target: < 3 s per document page and < 4 s per scene photo [A-12].

### 6.5 TTS and Vision

```python
@dataclass(frozen=True)
class Voice:
    id: str; language: str; sample_rate: int

@runtime_checkable
class TTSEngine(Engine, Protocol):
    def voices(self) -> Sequence[Voice]: ...
    def synthesize(self, ctx: RequestContext, text: str, voice: Voice,
                   rate: float = 1.0) -> AsyncIterator[AudioChunk]: ...  # sentence-chunked

@dataclass(frozen=True)
class VisionAnswer:
    text: str; regions: Sequence[tuple[int, int, int, int]] = ()

@runtime_checkable
class VisionEngine(Engine, Protocol):
    async def describe(self, ctx: RequestContext, image: ImageRef,
                       prompt: str | None = None) -> VisionAnswer: ...
```
- **TTS default: Piper**, with `en_US`/`en_GB` voices and **Hindi `hi_IN` voices** (e.g., `hi_IN-pratham-medium`, `hi_IN-priyamvada-medium`; availability and quality to verify [A-35]). Sentence-streamed, so the first audio arrives < 500 ms after the first sentence. For code-mixed text, a per-sentence script detector picks the voice. English words inside Hindi sentences are read by the Hindi voice, and quality there is a known risk. Fallback: AI4Bharat Indic-TTS (FastPitch/VITS) if the Piper `hi` voices are weak [A-35].
- **Vision local**: llama.cpp multimodal with a small VLM (e.g., SmolVLM-256M/500M, Moondream2, or Qwen2-VL-2B Q4) [A-13], 4 GB SKU only. Expect 5–30 s per image on CM5, so it's labeled "basic" per the PRD. Cloud vision is the higher-quality option, with consent.

### 6.6 Backend registry and profiles

```toml
# /var/lib/pm/settings.toml  (defaults are written from the SKU profile at first boot, §6.11)
[profile]
sku = "auto"            # auto-detected: "cm5-4g" | "cm5-2g" | "cm4"
mode = "local"          # "local" (default) | "ask_each_time"
primary_language = "hinglish"   # "en" | "hi" | "hinglish"; set in onboarding
[asr]       backend = "whispercpp"; model = "hinglish-small-q5_0.bin"; partials = "vosk"; partial_models = ["en-in-small","hi-small"]
[llm]       backend = "llamacpp";   model = "llama-3.2-1b-instruct-q4_k_m.gguf"; ctx = 4096
[ocr]       backend = "paddleocr";  doc_langs = ["en","hi"]; scene_backend = "indicphotoocr"
[translate] backend = "indictrans2-dist-ct2"; pairs = ["hi-en","en-hi","indic-en"]
[tts]       backend = "piper";      voices = { en = "en_US-lessac-medium", hi = "hi_IN-pratham-medium" }
[vision]    backend = "llamacpp-mtmd"; model = "smolvlm-500m"
[embed]     backend = "llamacpp";   model = "multilingual-e5-small-q8_0.gguf"; enabled = true
[summary]   enabled = false; time = "20:30"      # §9.1, opt-in
[cloud]     enabled = false          # §6.7, providers configured individually
```

### 6.7 Cloud adapters (optional, pluggable, no vendor lock-in) [PM 2026-10-21]

- **Off by default.** `cloud.enabled = false` is the factory state on every SKU [PM 2026-10-21, v0.3]. On the 2 GB SKU, the device *offers* cloud more often, but each use still needs per-request consent.
- **Provider plug-in interface.** The core code never imports a vendor SDK. Adapters are entry-point plug-ins (`pocketmate.cloud.providers`) that implement the same engine Protocols (§6.1–6.5) plus:

```python
@dataclass(frozen=True)
class ProviderManifest:
    id: str                       # 'sarvam', 'openai-compatible', 'self-hosted', ...
    display_name: str
    capabilities: frozenset[Literal["asr", "llm", "ocr", "vision", "tts", "translate"]]
    endpoints: Sequence[str]      # hostnames allowed in nftables/TLS pinning for this provider
    data_policy_url: str          # shown in consent dialog
    region: str | None            # e.g. 'IN'
    auth: Literal["api_key", "oauth", "none"]

class CloudProvider(Protocol):
    manifest: ProviderManifest
    def engine(self, capability: str) -> Engine: ...           # returns ASR/LLM/... engine, locality=CLOUD
    async def validate_credentials(self) -> bool: ...
    async def estimate(self, capability: str, payload_bytes: int) -> dict: ...  # cost/latency hint for dialog
```
- Adapters [PM 2026-10-21, v0.3]:
  - **`sarvam` (first, built-in)**: ASR (Saaras/Saarika), with OCR/translate later.
  - **`openai` (optional plug-in)**, which also covers generic OpenAI-compatible and self-hosted endpoints.
  - **`gemini` (optional plug-in)**.
- Others can be added as plug-ins. A per-capability router lets the user choose a provider for each capability.
- No vendor-specific types cross the plug-in boundary. Everything is converted to the PocketMate dataclasses. Provider settings export and import as part of the backup, minus the secrets.
- **Deletion API (required for every provider plug-in) [PM 2026-10-21, closes UX pending item 3]**:

```python
@dataclass(frozen=True)
class RemoteRef:
    provider: str; request_id: uuid.UUID          # our id
    remote_ids: Sequence[str]                      # provider job/file/response ids returned at send time
    kind: Literal["request_log", "uploaded_file", "transcript", "conversation", "other"]

@dataclass(frozen=True)
class DeletionReceipt:
    ref: RemoteRef
    status: Literal["deleted", "pending", "unsupported", "failed"]
    provider_receipt: str | None                   # provider's confirmation id / HTTP status
    verified: bool                                  # verify_deleted() confirmed absence (e.g. GET → 404)
    checked_at: float

class CloudProvider(Protocol):                     # (continued)
    supports_deletion: bool                         # manifest-level claim, shown in consent dialog 12b
    declared_retention_days: int | None             # provider's stated server-side retention if no deletion API
    async def delete(self, refs: Sequence[RemoteRef]) -> list[DeletionReceipt]: ...
    async def verify_deleted(self, ref: RemoteRef) -> DeletionReceipt: ...
```
  - pm-cloud records every send in `cloud_requests` (§7) together with the provider's remote ids.
  - **Delete paths**:
    - the user deletes a local item that was produced with cloud help (cascade);
    - the user revokes a provider (screen 12c: delete all remote data for that provider);
    - the user deletes from the cloud log (12d).
  - **Flow**:
    1. `delete()`, then `verify_deleted()`.
    2. On failure or pending, retry with backoff **for 7 days** (locked UX parameter). The retry runs only while online, under the same egress rules.
    3. The final state is shown in 12d.
  - Every step is logged in `consent_log` (`cloud_delete_requested`, `cloud_delete_confirmed`, `cloud_delete_failed`, `cloud_delete_unsupported`).
  - If a provider has **no deletion API**, the consent dialog 12b says so before sending ("<provider> keeps data for N days and can't delete on request").
  - **Sarvam: no per-request deletion API was found in the docs (2026-10-21)**, so it's treated as `unsupported`. Retention is controlled by the user's workspace setting (zero retention available for Model APIs). See §6.7.1.
  - The provider shown in the UX (`<provider>`) is **Sarvam for ASR** [PM 2026-10-21]. Other capabilities have no default provider yet.
- **Hard gate**: pm-cloud rejects any call without a valid `ConsentToken` whose `request_id` matches, `payload_sha256` matches the exact bytes being sent, scope matches, and that hasn't expired. A token is single-use and is stored in the consent log.
- Cloud is never a silent fallback. When a local engine fails, or the device is hot (§10.4), the UI offers "Try with cloud?" and the consent dialog opens.
- **Cloud latency cap [PM 2026-10-21]: 4 s.** pm-core cancels a cloud request that hasn't produced a first result in 4 s, shows "Cloud too slow, using on-device", and falls back to the local result (§14).
- API keys are stored on the LUKS data partition (or in the kernel keyring), entered by the user, and never logged.

### 6.7.1 Provider data-retention and deletion terms (researched 2026-10-21, primary sources) [PM 2026-10-21, v0.3]

Provider order [PM 2026-10-21]: **Sarvam first** (ASR, built-in). **OpenAI and Gemini are optional plug-ins.** All three use the user's own API key/account. **BYO key per user, no PocketMate proxy in MVP** [PM 2026-10-21, v0.3.1]. The user's account settings therefore decide retention, and the device can't change them through the API.

| Provider | Default retention | Retention controls | Per-request deletion API | Training use | Sources |
|---|---|---|---|---|---|
| **Sarvam** (Model APIs, e.g., speech-to-text) | **Indefinite until a workspace Owner sets a retention period.** The privacy policy separately states "Your Content: user-configurable (default: 30 days after last access)". The two sources disagree, so we assume indefinite | Workspace default + Model API override: 0 days (**zero retention supported for Model APIs**), 1, 15, 30, 45, 60, 90, 180, 365, 730 days. Not retroactive. Owner-only | **None found** in the docs. Deletion is by retention setting, or by a request to the Grievance Officer (privacy policy: requests handled per applicable law) | **Privacy policy: content is used for training unless you opt out** (account settings toggle, Owner-only) | https://docs.sarvam.ai/api/platform/data-retention.md · https://docs.sarvam.ai/api/platform/faq.md · https://docs.sarvam.ai/changelog/2026/9/15.md · https://www.sarvam.ai/privacy-policy · https://www.sarvam.ai/trust-center |
| **OpenAI API** (optional plug-in) | Abuse-monitoring logs (may contain prompts/responses) kept **up to 30 days**. `/v1/chat/completions`: no application state by default. `/v1/responses`: stored unless `store=false`. `/v1/files`: kept **until deleted** | Zero Data Retention / Modified Abuse Monitoring: **approval-only**, not self-serve | Yes, for application state: `DELETE /v1/files/{id}`, and deletion of stored responses (`DELETE /v1/responses/{id}`) [A-51: verify the endpoint in the current API reference]. **No API to delete abuse-monitoring logs** | API data is not used for training by default (endpoint table: "Data used for training: No") | https://developers.openai.com/api/docs/guides/your-data · https://trust.openai.com/ · https://openai.com/business-data/ |
| **Google Gemini API** (optional plug-in) | **Paid tier**: prompts/responses logged **55 days** for abuse monitoring. Files API: until deleted or expired. Interactions API stores state unless `store=false`. Live API session resumption keeps state up to 24 h. Grounding with Search/Maps keeps 30 days and can't be disabled | No self-serve ZDR on the Gemini Developer API (Google points to Vertex AI for guaranteed ZDR). Developer logs: 7/14/28/55 days | Files API delete. **No API for abuse-monitoring logs** | Paid: not used to improve products. **Unpaid/free tier: governed by the unpaid-services terms (may be used to improve products, with human review). The adapter must refuse non-billing projects** [A-52: confirm the unpaid wording on the terms page] | https://ai.google.dev/gemini-api/terms · https://ai.google.dev/gemini-api/docs/usage-policies · https://ai.google.dev/gemini-api/docs/zdr · https://ai.google.dev/gemini-api/docs/logs-policy |

**Consent dialog terms display (12b) [PM 2026-10-21, v0.3.1]**:
- Every request shows the provider's terms from its `ProviderManifest`, extended with:

```python
@dataclass(frozen=True)
class ProviderTerms:
    retention_summary: str              # e.g. "Abuse logs up to 30 days; no deletion"
    retention_days: int | None          # None = indefinite/unknown
    user_configured_retention_days: int | None   # BYO account setting the user confirmed (e.g. Sarvam 0 days)
    training_use: Literal["no", "opt_out_confirmed", "opt_out_unconfirmed", "yes"]
    deletion: Literal["api", "retention_only", "none"]
    source_urls: Sequence[str]          # primary sources (§6.7.1 table)
    reviewed_on: str                    # '2026-10-21'
    contract_status: Literal["dpa_signed", "public_terms_only", "unconfirmed"]
```
- The dialog layout shows two lines plus a "Details" expander with the URLs:
  - "Kept: <retention_summary>"
  - "Used for training: <training_use>"
- A missing or unknown field is shown as **"Unknown"** in amber. It's never hidden.
- The terms version shown is stored in `consent_log.detail` (`terms_reviewed_on`, `contract_status`), so the audit log records what the user saw.

**Adapter consequences (implemented in pm-cloud)**:
- **Sarvam**:
  - **Training opt-out by default [v0.3.1]**:
    - If the API exposes a per-request or account flag (none found in the docs, 2026-10-21 [A-53]), the adapter always sends or sets the opt-out.
    - Otherwise provider setup is **blocked on a checklist step**: the user confirms that Settings → Organisation → General → *Model training* is **off** (Owner-only toggle per the Sarvam FAQ). The setup screen links there and offers a pre-filled opt-out email to the address in the privacy policy.
    - The adapter records `training_optout = confirmed | unconfirmed`. While unconfirmed, consent dialog 12b shows the training warning in red on every request.
  - **DPA status**: no Sarvam DPA yet. A Sarvam DPA is a **pre-launch action for Anand** [PM 2026-10-21, v0.3.1]. Until it's signed, all Sarvam terms in this doc are marked **unconfirmed**, and the dialog says "Terms not yet confirmed by contract".
  - `supports_deletion = False`.
  - `declared_retention_days` is read from user input during provider setup. Screen 00e/12 asks the user to confirm they've set Model API retention to **0 days** and turned **training off**, with links to the Sarvam settings. Otherwise, consent dialog 12b warns: "Sarvam may keep this audio indefinitely and may use it for training".
  - The device can't verify these settings through the API [A-53].
- **OpenAI**:
  - Always send `store=false`. Never use the Files/Assistants APIs (inline audio/image only).
  - `supports_deletion = True` for anything with an id: the adapter records response/file ids in `cloud_requests` and deletes them immediately after use.
  - The consent dialog states "copies may stay in OpenAI abuse-monitoring logs for up to 30 days".
- **Gemini**:
  - Paid (billing-enabled) projects only. The adapter checks at setup and refuses otherwise [A-52].
  - No Files API, no Grounding, Interactions `store=false`, no Live session resumption, no explicit caching.
  - The consent dialog states "kept up to 55 days for abuse monitoring".
- **Unverified items**:
  - Sarvam per-request delete API: none found, so we assume none.
  - The Sarvam docs-vs-policy default retention discrepancy.
  - The exact OpenAI responses-delete endpoint semantics.
  - The Gemini unpaid-tier wording.
  - All terms can change, so pm-cloud shows a "terms last reviewed: 2026-10-21" date and the review is repeated before each release.

### 6.8 Translation (camera translation, MVP feature #4) [PM 2026-10-21]

```python
@dataclass(frozen=True)
class TranslationSegment:
    src_text: str; tgt_text: str; src_lang: str; tgt_lang: str
    bbox: tuple[int, int, int, int] | None = None     # for camera overlay
    confidence: float | None = None

@runtime_checkable
class TranslationEngine(Engine, Protocol):
    def pairs(self) -> Sequence[tuple[str, str]]: ...
    async def translate(self, ctx: RequestContext, texts: Sequence[str],
                        src_lang: str | None, tgt_lang: str) -> list[TranslationSegment]: ...
    def translate_stream(self, ctx: RequestContext, texts: Sequence[str],
                         src_lang: str | None, tgt_lang: str) -> AsyncIterator[TranslationSegment]: ...
```
- **Local default: IndicTrans2 distilled** (~200 M params, indic↔en and indic↔indic). Converted to **CTranslate2 int8**, running on CPU in a `pm-translate` process.
- ⚠ FEASIBILITY:
  - RAM: ~250–400 MB for each direction model (en→indic and indic→en are separate checkpoints).
  - Speed: estimated 0.5–2 s for a short sign or menu (≤ 30 words), and several seconds for a dense page [A-36, unmeasured].
  - Tokenization dependency: IndicTrans2 needs IndicProcessor preprocessing plus SentencePiece. Those must be ported or packaged for aarch64.
  - Fits the 4 GB SKU only if the LLM is unloaded or mmap-evicted while translating.
  - On the 2 GB SKU, local translation is limited to indic→en and offered with cloud assistance (consent).
  - Fallback options: smaller distilled or quantized models, or the OPUS-MT `hi-en` Marian models (~75 M params) for Hindi only.
- Pipeline and UI: §9.2.

### 6.9 Language and script handling
- Text is stored NFC-normalized. The FTS index also stores a romanized shadow and a Devanagari shadow (§7), so "kal meeting" finds "कल meeting" and vice versa.
- UI fonts: Noto Sans + Noto Sans Devanagari (+ other Indic Noto fonts for translation display). HarfBuzz shaping through Qt is required, and Devanagari rendering is tested at 800×480.
- On-screen keyboard: Qt Virtual Keyboard with English and Hindi (Devanagari) layouts, plus transliteration input [A-37].

### 6.10 CM5 benchmark plan: ASR, OCR, translation, LLM (milestone M2/M3/M4 gate) [PM 2026-10-21]

**Rig**:
- Hardware: CM5 4 GB and CM5 2 GB on the IO Board, with the official cooler *and* a passive mock-enclosure configuration.
- Each run is logged at 25 °C and at 35 °C ambient.
- Settings: fixed governor, `taskset` 4 threads.
- Telemetry: `vcgencmd measure_temp/clock`, `/proc/<pid>/status` VmHWM.
- Power: INA226 on the 5 V input.

**Test sets** (each ~30–60 min, with licensing checked):
- EN: FLEURS en-IN or Svarah (Indian-accented English) plus an in-house set of 100 PocketMate-style commands and notes.
- HI: FLEURS hi plus Vistaar subsets (e.g., Kathbath).
- HINGLISH: CoSHE / cs-FLEURS subsets plus an in-house set of 200 code-mixed utterances (reminders, notes, questions) recorded on the prototype mics. Recordings include quiet, café (~65 dBA) and street noise.

**Candidates**:
- ASR:
  - whisper.cpp `base`/`small` multilingual (stock).
  - A Hindi/Hinglish fine-tune at small/base size.
  - IndicWhisper (medium, as the reference).
  - Vosk small-hi/en-in.
  - faster-whisper int8 for comparison.
  - Sarvam cloud as the reference upper bound, used with test data only.
- OCR: PaddleOCR mobile (Latin + Devanagari), IndicPhotoOCR, Tesseract (baseline).
- Translation: IndicTrans2-dist (CT2 int8), OPUS-MT hi-en.
- LLM: Llama-3.2-1B/3B, Qwen2.5-0.5B/1.5B, Gemma-3-1B. Measure prefill and decode separately.

**Metrics**

| Metric | Definition | Pass bar (4 GB) |
|---|---|---|
| WER / CER | jiwer, after script normalization (both scripts romanized before scoring Hinglish, plus native-script CER for HI) | EN ≤ 12 %, HI ≤ 20 %, Hinglish ≤ 25 % [A-33] |
| RTF | decode time / audio duration, 4 threads | ≤ 0.5 (final), partial lag ≤ 500 ms |
| End-of-speech → final | for 3 s / 10 s / 30 s utterances, streaming chunking on | ≤ 600 ms tail for 3 s commands (feeds the ≤ 750 ms local-action budget) |
| Peak RAM (VmHWM) | per engine | ASR ≤ 600 MB, translate ≤ 400 MB, LLM ≤ 1.6 GB |
| Energy | J per utterance (INA226) | report |
| Thermal | SoC °C after 10 min at 1 utterance / 15 s | ≤ 65 °C SoC (§10.4) |
| OCR | CER/word accuracy on 100 printed docs + 100 scene photos (EN/HI) | doc CER ≤ 5 %, scene word acc ≥ 80 % |
| Translation | chrF++ / BLEU on FLORES-200 devtest hi↔en, plus a 100-photo sign/menu set; latency for ≤ 30 words | chrF++ ≥ 50 hi→en; ≤ 2 s |
| LLM | prefill tok/s, decode tok/s, TTFT at a 250-token prompt, JSON-extraction accuracy on 100 Hinglish reminder phrases | TTFT ≤ 1.5 s; extraction ≥ 90 % |

**Output**: `software/bench/REPORT.md` plus CSVs, and the decision recorded in this doc. Scripts live in `software/tools/bench/` (Python, reproducible, model hashes pinned).

### 6.11 SKU profiles and model selection at boot [PM 2026-10-21]

| Profile | Module | ASR (final / partial) | LLM | OCR | Translation | Vision | Embeddings | Cloud |
|---|---|---|---|---|---|---|---|---|
| **cm5-4g** (₹29,999 SKU [Research]) | CM5104032 | Hinglish/Indic fine-tune small/base / Vosk | Llama-3.2-1B (3B "quality" mode) | PaddleOCR + IndicPhotoOCR | IndicTrans2-dist both directions | SmolVLM local | e5-small on | off. Per-request offers on failure or heat |
| ~~**cm5-2g**~~ **DEFERRED, not v1 (v0.3.2)** (₹17,999–24,999 SKU [Research]; cloud off by default, Hinglish notice [PM v0.3]) | CM5102032 | whisper `base` multilingual (or tiny) / Vosk | **qwen2.5-0.5B** | PaddleOCR (doc) | indic→en only, or cloud-assisted | cloud-assisted only | off (FTS only) | off by default. **"Cloud-assisted mode"**: proactively offers Sarvam ASR / cloud LLM / vision per request, each with consent |
| **cm4** (alternate) | CM4 4 GB | Vosk + whisper tiny | qwen2.5-0.5B | PaddleOCR doc | OPUS-MT hi-en | none | off | as 2 GB |

**v1 ships only `cm5-4g`** [v0.3.2]. On any other module, pm-profile boots into a "platform not supported in this build" diagnostics mode (dev builds may override). The `cm5-2g`/`cm4` rows are kept for later SKUs, and `radxa-cm5-4g` is added in rev 2 (§17).

**Model selection at boot**:
1. `pm-profile.service` (oneshot, before pm-core) reads `/proc/device-tree/model` and `/proc/meminfo` MemTotal, plus `/proc/device-tree/serial-number` for the record. It maps these to a profile: MemTotal < 2.5 GB → `cm5-2g`.
2. It reads the installed `models` bundle manifest (`/opt/pm/models/manifest.json`, listing per-model RAM, SKU tags and sha256). It verifies that the required models are present and their hashes match. Missing models are disabled and the UI shows a "Model pack missing" notice.
3. It writes `/run/pm/profile.toml`. User settings may downgrade a choice (e.g., smaller ASR) but not upgrade beyond the RAM budget.
4. The pm-core model scheduler enforces exclusivity: on 2 GB, at most one heavy engine at a time. zram is 1 GB on 4 GB devices and 768 MB on 2 GB devices.
5. Models bundles are built per SKU (`pocketmate-models-<ver>-cm5-2g.raucb`), so 2 GB devices don't carry 4 GB models.

⚠ FEASIBILITY (2 GB): Qt UI (~150 MB) + services (~400 MB) + qwen2.5-0.5B (~400 MB) + whisper base (~200 MB) + OS ≈ 1.4 GB. That fits, with only small headroom. Hindi/Hinglish ASR quality on whisper base/tiny will likely miss the §6.10 WER bars. The 2 GB SKU should be positioned as cloud-assisted for Hinglish [Research bom.md §8].

### 6.12 Hindi phonetic transliteration (typing + search) [closes UX pending item 2]

**Recommendation: AI4Bharat IndicXlit (Roman→Devanagari, neural) for the keyboard suggestion bar, plus `indic-transliteration` (sanscript, rule-based) for deterministic normalization and indexing.**

| | IndicXlit (en→hi) | indic-transliteration (sanscript) |
|---|---|---|
| Role | top-k candidates for loose, phonetic Roman input ("kal milte hai" → कल मिलते है), and query expansion | lossless scheme conversion (Devanagari ↔ ITRANS/IAST/HK) used to build the romanized index shadow |
| Model | transformer, ~11 M params, beam search [A-38: size/latency to verify] | pure Python tables, no model |
| On-device runtime | export the fairseq checkpoint to **CTranslate2 int8** (or ONNX), ~15–30 MB on disk, ~40–60 MB RAM. Word-level beam 4 → 4 candidates. Est. 5–20 ms/word on one A76 core [A-38] | < 1 ms/word |
| Process | `pm-xlit` (small, resident; no network) on D-Bus `org.pocketmate.Xlit.Suggest(word, k)`; UI debounces 50 ms | library inside pm-memory |
| Fallback | if latency > 50 ms: a rule-based scheme + a frequency dictionary (top-50k Hindi words with romanized variants) | — |

- **Keyboard (screens 11c/11b)**: the phonetic layout is the default (design-system.md). Each keystroke updates the current Roman word, pm-xlit returns 4 candidates, and the suggestion bar shows them (with ⌄ to collapse). Space commits the first candidate. The user dictionary learns accepted picks (stored locally in the data partition, deletable). InScript (11d) is direct Devanagari input with no engine.
- **FTS integration: Roman queries match Devanagari text, and the reverse.**
  1. Every chunk is indexed in three FTS columns: `text` (original), `text_rom` (Devanagari spans → ITRANS via sanscript → a **phonetic key**), and `text_deva` (Latin-script Hindi words in Hinglish text → top-1 IndicXlit, only for tokens not in an English lexicon).
  2. **Phonetic key** normalization, applied to both index and query. The goal is that "milte"/"milate"/"मिलते" collide:
     - lowercase;
     - aa→a, ee/ii→i, oo/uu→u;
     - drop the schwa at word end;
     - w→v, z→j, sh/ṣ→s, ph→f;
     - collapse doubled letters;
     - remove nasal marks (ṃ/ṁ/n before consonant).
  3. Query rewrite in pm-memory: the user's query `q` becomes the FTS expression `({text}: q) OR ({text_rom}: phonkey(q)) OR ({text_deva}: xlit_topk(q, 3))`. Results are ranked with `bm25` weighting `text` 1.0, `text_deva` 0.8, `text_rom` 0.6.
  4. The unicode61 tokenizer splits on some Devanagari combining marks in edge cases [A-39], so a **trigram** index on `text` is kept as a fallback for Devanagari substring search.
- Quality evaluation: top-1 and top-4 accuracy on a 1,000-word Hinglish typing set (Aksharantar test plus in-house), and search recall@10 on 100 cross-script queries (target ≥ 90 %).

---

## 7. Memory — SQLite FTS5 schema

DB: `/var/lib/pm/memory.db`, WAL mode, `PRAGMA foreign_keys=ON`, `secure_delete=ON` (so deleted data is overwritten), single writer (pm-memory). Media files live under `/var/lib/pm/media/<yyyy>/<mm>/<uuid>.<ext>`.

```sql
PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;
PRAGMA secure_delete = ON;

-- Common item table: every memorable thing has a row here (source-link target).
CREATE TABLE items (
  id            TEXT PRIMARY KEY,            -- UUIDv7
  kind          TEXT NOT NULL CHECK (kind IN ('note','transcript','ocr_doc','image','interaction','task','summary')),
  title         TEXT,
  created_at    INTEGER NOT NULL,            -- unix ms UTC
  updated_at    INTEGER NOT NULL,
  source        TEXT NOT NULL CHECK (source IN ('voice','typed','camera','import','assistant')),
  locality      TEXT NOT NULL DEFAULT 'local' CHECK (locality IN ('local','cloud')), -- was cloud used to produce it
  retention     TEXT NOT NULL DEFAULT 'keep',    -- [PM 2026-10-21] keep until user sets auto-delete; else ISO duration e.g. 'P30D'
  expires_at    INTEGER,                     -- NULL = keep (default); set only when user configures auto-delete
  language      TEXT,                        -- 'en' | 'hi' | 'hi-en'
  pinned        INTEGER NOT NULL DEFAULT 0,
  deleted_at    INTEGER                      -- soft delete (trash, 7 days) before purge
);
CREATE INDEX items_kind_created ON items(kind, created_at DESC);
CREATE INDEX items_expires ON items(expires_at) WHERE expires_at IS NOT NULL;

CREATE TABLE tags (item_id TEXT REFERENCES items(id) ON DELETE CASCADE, tag TEXT NOT NULL,
                   PRIMARY KEY (item_id, tag));

CREATE TABLE notes (
  item_id   TEXT PRIMARY KEY REFERENCES items(id) ON DELETE CASCADE,
  body      TEXT NOT NULL,                   -- markdown
  origin_transcript_id TEXT REFERENCES items(id) ON DELETE SET NULL
);

CREATE TABLE transcripts (
  item_id     TEXT PRIMARY KEY REFERENCES items(id) ON DELETE CASCADE,
  text        TEXT NOT NULL,
  language    TEXT,
  duration_ms INTEGER,
  audio_path  TEXT,                          -- NULL unless user chose "keep audio" (default: discard audio)
  engine      TEXT NOT NULL                  -- e.g. 'whispercpp:base-q5_1'
);
CREATE TABLE transcript_segments (
  item_id  TEXT REFERENCES items(id) ON DELETE CASCADE,
  seq      INTEGER, start_ms INTEGER, end_ms INTEGER, text TEXT,
  PRIMARY KEY (item_id, seq)
);

CREATE TABLE ocr_docs (
  item_id     TEXT PRIMARY KEY REFERENCES items(id) ON DELETE CASCADE,
  image_path  TEXT NOT NULL,
  full_text   TEXT NOT NULL,
  language    TEXT,
  blocks_json TEXT,                          -- [{text,bbox,conf}]
  engine      TEXT NOT NULL,
  mean_conf   REAL,
  translation_json TEXT,                     -- [{src,tgt,src_lang,tgt_lang,bbox}] (§9.2)
  target_lang TEXT
);

CREATE TABLE interactions (                  -- Q&A history with citations
  item_id   TEXT PRIMARY KEY REFERENCES items(id) ON DELETE CASCADE,
  question  TEXT NOT NULL, answer TEXT NOT NULL, engine TEXT NOT NULL
);
CREATE TABLE citations (
  interaction_id TEXT REFERENCES items(id) ON DELETE CASCADE,
  cited_item_id  TEXT REFERENCES items(id) ON DELETE CASCADE,
  span_start INTEGER, span_end INTEGER,      -- char offsets in cited text (or ms for transcript)
  PRIMARY KEY (interaction_id, cited_item_id, span_start)
);

CREATE TABLE reminders (
  id           TEXT PRIMARY KEY,
  item_id      TEXT REFERENCES items(id) ON DELETE SET NULL,   -- originating note/transcript
  title        TEXT NOT NULL,
  due_at       INTEGER,                      -- unix ms UTC; NULL = undated task
  tz           TEXT NOT NULL DEFAULT 'Asia/Kolkata',  -- [A-15] device tz from settings
  rrule        TEXT,                         -- RFC 5545, e.g. 'FREQ=DAILY;BYHOUR=9'
  status       TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('suggested','pending','done','dismissed','snoozed')),
  snooze_until INTEGER,
  is_task      INTEGER NOT NULL DEFAULT 0,   -- daily task vs timed reminder
  created_at   INTEGER NOT NULL, completed_at INTEGER
);
CREATE INDEX reminders_due ON reminders(status, due_at);

CREATE TABLE consent_log (                   -- append-only audit log
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  ts           INTEGER NOT NULL,
  event        TEXT NOT NULL CHECK (event IN ('cloud_granted','cloud_denied','cloud_sent','cloud_error',
                                              'mic_open','mic_close','camera_capture','export','delete',
                                              'retention_change','setting_change','factory_reset',
                                              'cloud_delete_requested','cloud_delete_confirmed',
                                              'cloud_delete_failed','cloud_delete_unsupported','charge_inhibit','thermal_stage')),
  scope        TEXT,                         -- asr/llm/ocr/vision
  provider     TEXT,
  request_id   TEXT,
  payload_sha256 TEXT,
  bytes_sent   INTEGER,
  detail       TEXT,                         -- JSON, no user content
  prev_hash    TEXT NOT NULL,                -- hash chain for tamper evidence
  row_hash     TEXT NOT NULL
);
CREATE TRIGGER consent_log_no_update BEFORE UPDATE ON consent_log
BEGIN SELECT RAISE(ABORT, 'consent_log is append-only'); END;
CREATE TRIGGER consent_log_no_delete BEFORE DELETE ON consent_log
WHEN (SELECT value FROM meta WHERE key='factory_reset_in_progress') IS NOT '1'
BEGIN SELECT RAISE(ABORT, 'consent_log is append-only'); END;

CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT);  -- schema_version, etc.

-- Auto-delete rules (user-set; none by default) [PM 2026-10-21]
CREATE TABLE retention_rules (
  kind TEXT PRIMARY KEY, duration TEXT NOT NULL,   -- e.g. 'transcript' -> 'P90D'
  created_at INTEGER NOT NULL
);

-- Cloud requests and remote ids for the deletion API (§6.7)
CREATE TABLE cloud_requests (
  request_id   TEXT PRIMARY KEY,
  provider     TEXT NOT NULL, capability TEXT NOT NULL,
  item_id      TEXT REFERENCES items(id) ON DELETE SET NULL,
  remote_ids   TEXT NOT NULL DEFAULT '[]',         -- JSON array
  sent_at      INTEGER NOT NULL,
  delete_state TEXT NOT NULL DEFAULT 'none' CHECK (delete_state IN ('none','requested','pending','deleted','failed','unsupported')),
  delete_attempts INTEGER NOT NULL DEFAULT 0, delete_deadline INTEGER, verified_at INTEGER
);

-- Daily summary (§9.1)
CREATE TABLE daily_summaries (
  item_id     TEXT PRIMARY KEY REFERENCES items(id) ON DELETE CASCADE,
  day         TEXT NOT NULL UNIQUE,               -- local date 'YYYY-MM-DD'
  body_json   TEXT NOT NULL,                      -- {highlights[{text,source_ids}], done[], open[], tomorrow[]}
  mode        TEXT NOT NULL CHECK (mode IN ('llm','extractive')),
  stale       INTEGER NOT NULL DEFAULT 0,         -- set when a cited item is deleted/edited
  generated_at INTEGER NOT NULL, notified_at INTEGER
);
-- Highlights reuse `citations` (interaction_id = summary item_id).
CREATE TRIGGER summary_stale_on_delete AFTER UPDATE OF deleted_at ON items
WHEN NEW.deleted_at IS NOT NULL
BEGIN
  UPDATE daily_summaries SET stale = 1
  WHERE item_id IN (SELECT interaction_id FROM citations WHERE cited_item_id = NEW.id);
END;

-- Full-text index over all searchable text (external-content style, one row per chunk).
CREATE TABLE chunks (
  id       INTEGER PRIMARY KEY,
  item_id  TEXT NOT NULL REFERENCES items(id) ON DELETE CASCADE,
  seq      INTEGER NOT NULL,
  text     TEXT NOT NULL,                    -- ~300-500 tokens, overlap 50
  span_start INTEGER, span_end INTEGER,      -- offsets back into source text (source links)
  t_start_ms INTEGER, t_end_ms INTEGER,      -- transcript chunks: audio timestamps (source link)
  bbox_json  TEXT,                           -- OCR chunks: region(s) in the photo (source link)
  UNIQUE(item_id, seq)
);
CREATE VIRTUAL TABLE chunks_fts USING fts5(
  text,                                      -- original (any script)
  text_rom,                                  -- phonetic key of romanized text (§6.12)
  text_deva,                                 -- Devanagari shadow of Latin-script Hindi tokens
  title UNINDEXED, kind UNINDEXED,
  content='', contentless_delete=1,          -- SQLite >= 3.43
  tokenize = 'unicode61 remove_diacritics 2'
);
-- pm-memory writes chunks_fts(rowid=chunks.id, ...) in the same transaction as chunks.
-- Optional: second index with tokenize='trigram' for substring/OCR-noise tolerant search.

-- Optional semantic retrieval (sqlite-vec extension)
-- .load vec0
CREATE VIRTUAL TABLE chunk_vec USING vec0(
  chunk_id INTEGER PRIMARY KEY,
  embedding float[384]                       -- multilingual-e5-small (EN+HI)
);
CREATE TABLE embedding_meta (chunk_id INTEGER PRIMARY KEY REFERENCES chunks(id) ON DELETE CASCADE,
                             model TEXT NOT NULL, created_at INTEGER NOT NULL);
```

> Note: chunk/FTS/vec rows are deleted by pm-memory in the same transaction as the item (vec0 and contentless FTS don't honor FK cascades). A test asserts zero orphans after delete.

### 7.1 Example queries

```sql
-- 1. Keyword search with ranking + snippet, newest-weighted, excluding trash
SELECT i.id, i.kind, i.title, i.created_at,
       snippet(chunks_fts, 0, '[', ']', '…', 12) AS snip,
       c.span_start, c.span_end,
       bm25(chunks_fts) AS score
FROM chunks_fts
JOIN chunks c ON c.id = chunks_fts.rowid
JOIN items  i ON i.id = c.item_id
WHERE chunks_fts MATCH :q            -- e.g. 'wifi NEAR(password, 5)' or 'invoice*'
  AND i.deleted_at IS NULL
ORDER BY score + (strftime('%s','now')*1000 - i.created_at) / 8.64e10 * 0.05
LIMIT 20;

-- 2. Semantic top-k (sqlite-vec) then hybrid merge (Reciprocal Rank Fusion) in Python
SELECT chunk_id, distance FROM chunk_vec
WHERE embedding MATCH :qvec AND k = 20 ORDER BY distance;

-- 3. Source link: open the exact cited span
SELECT i.kind, c.text, c.span_start, c.span_end FROM citations ct
JOIN chunks c ON c.item_id = ct.cited_item_id
JOIN items i ON i.id = ct.cited_item_id
WHERE ct.interaction_id = :iid;

-- 4. Today's agenda
SELECT id, title, due_at, is_task FROM reminders
WHERE status IN ('pending','snoozed')
  AND (due_at < :end_of_day_ms OR (is_task = 1 AND due_at IS NULL))
ORDER BY due_at NULLS LAST;

-- 5. Next wake time to hand to MCU
SELECT MIN(COALESCE(snooze_until, due_at)) FROM reminders
WHERE status IN ('pending','snoozed') AND COALESCE(snooze_until, due_at) > :now_ms;

-- 6. Retention sweep (daily + on boot). No-op unless user created retention_rules (default keep)
UPDATE items SET deleted_at = :now WHERE expires_at < :now AND pinned = 0 AND deleted_at IS NULL;
-- purge after 7-day trash: DELETE items + chunks + chunks_fts + chunk_vec + media files

-- 8. Daily summary input for local day [:day_start_ms, :day_end_ms)
SELECT i.id, i.kind, i.title, substr(coalesce(n.body, t.text, o.full_text), 1, 160) AS first_line
FROM items i
LEFT JOIN notes n ON n.item_id = i.id
LEFT JOIN transcripts t ON t.item_id = i.id
LEFT JOIN ocr_docs o ON o.item_id = i.id
WHERE i.created_at >= :day_start_ms AND i.created_at < :day_end_ms
  AND i.deleted_at IS NULL AND i.kind IN ('note','transcript','ocr_doc','image')
ORDER BY i.pinned DESC, i.created_at LIMIT 40;
SELECT id, title, status, due_at FROM reminders
WHERE (completed_at BETWEEN :day_start_ms AND :day_end_ms)
   OR (status IN ('pending','snoozed','suggested') AND (due_at IS NULL OR due_at < :tomorrow_end_ms));

-- 9. Cross-script search (query 'kal meeting' expanded by pm-memory, §6.12)
SELECT c.item_id, bm25(chunks_fts, 1.0, 0.6, 0.8) AS score
FROM chunks_fts JOIN chunks c ON c.id = chunks_fts.rowid
WHERE chunks_fts MATCH '{text}: (kal meeting) OR {text_rom}: (kal meting) OR {text_deva}: (कल)'
ORDER BY score LIMIT 20;

-- 10. Open-source target for a search hit (note span / audio timestamp / photo bbox) [PM 2026-10-21]
SELECT i.kind, c.span_start, c.span_end, c.t_start_ms, c.t_end_ms, c.bbox_json,
       t.audio_path, o.image_path
FROM chunks c JOIN items i ON i.id = c.item_id
LEFT JOIN transcripts t ON t.item_id = i.id
LEFT JOIN ocr_docs o ON o.item_id = i.id
WHERE c.id = :chunk_id;
-- UI: note → scroll+highlight span; transcript → play audio from t_start_ms (or highlight segment if no audio);
--     ocr_doc/image → open photo with bbox highlight (screen 07 / 09).

-- 7. Consent audit for UI
SELECT ts, event, scope, provider, bytes_sent FROM consent_log ORDER BY id DESC LIMIT 100;
```

**Export**: a ZIP containing `items.jsonl`, markdown notes, media, and `consent_log.csv`, optionally encrypted with an age passphrase. **Import** restores from the same format. That gives the documented backup/recovery the PRD requires.

---

## 8. Consent and privacy model

### 8.1 Rules (enforced, tested)
| # | Rule | Enforcement |
|---|---|---|
| P1 | **Push-to-talk only.** No wake word, no continuous or background recording in MVP | pm-audio opens capture only during a PTT session. There's no API for unattended capture. Code review gate + test that capture fails without a PTT event |
| P2 | **Visible recording indicator** whenever the mic is live [Schematic netlist v3.2] | **Green REC LED D6 on MIC_FEED**: lit exactly when the mics are powered (§8.2), plus the on-screen listening overlay. Neither can be dismissed |
| P3 | **Physical mic mute** [Schematic netlist v3.2] | **DPDT slide SW5**, upstream of the mic load switch. Muted: MIC_SW_LIVE is off (the mics can't be powered whatever PA11 does), and the **red LED D1 is lit** (CM5 up). Software reads only **`MUTE_STATUS_IO`** (Q6 inverter; CM5 GPIO17 / MCU PA10, high = muted, valid only while the CM5 is up).<br>• **pm-audio refuses to open capture while muted**; a mute mid-session closes capture within 20 ms and discards the partial buffer.<br>• **The MCU reports mute changes** (`EVT_MIC_MUTE{muted, valid}`), refuses `MIC_ENABLE` while muted or while status is invalid, and never infers unmuted with the CM5 off.<br>• **The UI shows a persistent "Mic off (hardware)" icon** and, on PTT, "Mic is muted, slide the switch to talk" |
| P4 | **No covert camera** | Camera opens only from the Scan screen with a visible preview. The shutter is a user action. The LED blinks on capture |
| P5 | **Max session length** | PTT session auto-stops at 120 s (configurable up to 10 min for dictation) with a visible countdown |
| P6 | **Audio not stored by default; transcripts only** [PM 2026-10-21, v0.3] | PCM lives in RAM and is dropped after transcription. **Opt-in audio saving**: a global setting (off) and a per-note "Keep audio" toggle. Saved audio goes to the LUKS data partition (Opus 16 kbps) and follows retention rules. Search-to-audio-timestamp (PM-S1) works only for saved audio; otherwise the transcript segment is highlighted |
| P7 | **Cloud off by default.** Per-request explicit consent [PM 2026-10-21] | §8.3. Modes: *Local only* (default) / *Ask each time*. There's no "always cloud". Remote deletion via the provider deletion API (§6.7) |
| P8 | **Confirm consequential actions** | Deleting, bulk export, factory reset, sending anything off-device, and creating reminders from AI extraction (shown as `suggested` until confirmed) |
| P9 | **Retention control** [PM 2026-10-21] | **No default expiry: data is kept until the user sets auto-delete** (per kind in `retention_rules`, or per item). Trash for 7 days, `secure_delete`. The cloud log is kept ≥ 30 days (locked UX) |
| P10 | **Secure storage and comms** | LUKS2 data partition, TLS 1.3 + cert pinning for cloud/update, nftables egress by UID |
| P11 | **Audit log** | `consent_log`, hash-chained and append-only. Viewable in Settings and included in export |
| P13 | **Daily summary is local-only** | §9.1: never uses cloud, only uses explicit captures, opt-in |
| P12 | **Source links** | Every assistant answer that uses memory stores citations. If nothing was retrieved, the UI labels the answer "No sources: general knowledge" |

### 8.2 Recording indicator integrity
- **Peripheral rail** [Schematic netlist v3]: the mics, display and camera run from **+3V3_PERIPH** (buck U12, EN from CM5_3V3), which is only up while the CM5 is up. **When the CM5 is off (S4/ship), the mics are physically unpowered**, so covert recording is impossible in standby, independent of any firmware.
  - Rail sequencing: see §11 "Power control".
- **Final mic wiring** [Schematic netlist v3.2]:
  ```
  +3V3_PERIPH ─► SW5 (DPDT mute slide, flex) ─┬─ unmuted throw ─► MIC_SW_LIVE ─► U14 TPS22917 (EN = PA11) ─► MIC_FEED ─┬─► mics
                                              │                     │                                                  └─► green REC LED D6
                                              │                     └─► Q6 inverter ─► MUTE_STATUS_IO (CM5 GPIO17, MCU PA10)
                                              └─ muted throw ─► red mute LED D1
  ```
  - **SW5** is upstream of everything. When unmuted it energises **`MIC_SW_LIVE`**; when muted it feeds the **red mute LED D1** from +3V3_PERIPH.
  - **U14 TPS22917DBVR** (SOT-23-6, LCSC C2681320): IN = MIC_SW_LIVE, **EN = `MIC_PWR_EN` = MCU PA11 (pin 21)**, active high. A 100 kΩ external pull-down plus U14's internal EN pull-down make it **off by default**. Quick output discharge: turn-on ≈ 100 µs, fast off.
  - **`MIC_FEED`** (U14 output) powers the mics **and** the **green REC LED D6** (Kingbright APTD1608LZGCK, 0603, 1.3 kΩ, ≈ 1 mA).
  - **`MUTE_STATUS_IO`** = **Q6 inverter on MIC_SW_LIVE**: high when muted (MIC_SW_LIVE absent) **and the CM5 is up** (Q6 is pulled up from the CM5-side rail). It's **independent of PA11**.
  - **Flex J11**: **pin 11 = MIC_SW_LIVE**, **pin 15 = +3V3_PERIPH** (pins 9/10 remain the VEML7700 I2C).
  - SW5 pole 2: the data-line grounding from netlist v3 is not restated in v3.2 [A-77: confirm whether pole 2 still grounds the mic data line or is now unused].
- **Guarantees (hardware)**:
  - **Green shows exactly when the mics are powered.** D6 and the mics share MIC_FEED, downstream of SW5 and U14, so it no longer over-indicates when muted.
  - The mics can only be powered if SW5 is unmuted **and** PA11 is high **and** the CM5 is up.
  - **Red is lit whenever muted and the CM5 is up**, independent of PA11.
  - With the CM5 off, +3V3_PERIPH is down: no mic power, no LEDs, and MUTE_STATUS_IO is invalid.
- **Firmware gating (MCU `privacy` module, §12)**:
  - **Mute-status validity**: with the CM5 off, PA10 reads low/invalid (the rail is down). The MCU **treats mute status as invalid unless CM5 power-good is set** (CM5_3V3 sensed / `power_fsm` S0–S2 after `HELLO`). It **never infers "unmuted" from PA10 in that case**. `EVT_MIC_MUTE` carries `valid`; the CM5 uses GPIO17 only while it's running, which is when the status is valid by construction.
  - The MCU accepts **`MIC_ENABLE`** and drives PA11 high **only** if all of these hold:
    1. it's a CM5 request,
    2. ACTION (PA1) is currently held, **or** there's a confirmed tap-to-talk session (`session_id`, started by an ACTION press the MCU itself saw within the last 1 s),
    3. CM5 power-good is set **and** PA10 is valid and low (unmuted).
  - **Max-session timeout**: `max_s`, capped by the MCU at 120 s (600 s for dictation, P5), forces PA11 low.
  - PA11 is also driven low on ACTION release (hold mode), `MIC_ENABLE{off}`, mute, IWDG reset, **UART link loss** (> 2 s), the CM5 heartbeat timeout, **CM5 power-down/`SHUTDOWN_READY`/`RUN` reset**, loss of power-good, and any MCU reset or brown-out (pull-downs).
- Prototype (IO board + I2S mic breakouts): the same chain is built from breakouts (B3). IO-board 3V3 stands in for +3V3_PERIPH.

### 8.3 Cloud consent flow
1. pm-core decides the cloud would help (or the user picks "Use cloud").
2. The consent dialog shows the provider, the data category, an **exact preview** (text, or a thumbnail for an image), size, and the retention policy of the provider (as configured). Buttons: *Send once* / *Cancel*. The default focus is Cancel. **It also shows the provider's retention and training terms, deletion support and contract status** (`ProviderTerms`, §6.7.1) [PM 2026-10-21, v0.3.1].
3. On *Send once*, pm-core mints a single-use `ConsentToken` bound to the request and the payload hash. The log records `cloud_granted`.
4. pm-cloud verifies the token, sends, and logs `cloud_sent` with bytes. The resulting item has `locality='cloud'`, and the UI shows a cloud badge.
5. No implicit retries to other providers. Cancel logs `cloud_denied` and falls back to the local engine.

---

## 9. Reminders, tasks, action items

- **Creation**: voice or typed natural language (EN/HI/Hinglish) → **fast path first**: a rule/grammar parser (`dateparser` with `hi` locale + a Hinglish phrase grammar such as "kal subah 9 baje", "har Monday") gives ≤ 50 ms for the common patterns. **LLM path** only if the fast path fails (JSON-schema grammar). Both produce `{title, due_at_local, rrule?, is_task}`, which is shown as a **suggested** card that the user confirms. Card display ≤ 750 ms after end of speech on the fast path (§14).
- **Action-item extraction**: after a voice note or transcript is saved, pm-core runs extraction in the background and lists candidates as `suggested`. Nothing is auto-scheduled.
- **Scheduling**: pm-remind keeps a heap of upcoming occurrences, recomputed on change. RRULE via `dateutil.rrule`.
- **Delivery**:
  - In S0/S1: a UI banner plus a chime.
  - In S2/S4: pm-remind gives pm-power the next due time, pm-power programs the MCU RTC alarm (`SET_WAKE`), and the MCU wakes the CM5 and flashes the LED (plus haptic if fitted, §12).
- Missed reminders (device was off) are shown as "missed" on the next boot.
- Time is stored as UTC + tz.

### 9.1 Daily summary (evening recap) [PM 2026-10-21]

- **What**: a short recap of *today's* explicit captures: notes, voice notes, OCR docs, tasks completed/open/suggested, reminders that fired or were missed, and tomorrow's reminders. Each line carries a **source link** to the item it came from. Market research shows a fixed nightly ritual drives daily use [Research §6.1].
- **Opt-in** (`summary.enabled = false` until the user turns it on in onboarding or Settings, per the research recommendation). The default time is 20:30 local, user-set [A-41].
- **Trigger (pm-remind)**: a system recurring job `RRULE:FREQ=DAILY` at `summary.time − 10 min`.
  - If the CM5 is in S4, pm-remind has already scheduled an MCU RTC wake (`SET_WAKE` takes the min of the next reminder and the summary pre-generation time).
  - pm-core generates the summary, stores it, then either notifies at `summary.time` (LED/chime; banner on 01-home) or, if the device was woken only for this, returns to S4 after storing it. The user sees it on the next wake.
- **Generation**:
  - **Local only, always.** Cloud is never used for the summary, even in "ask each time" mode.
  - Input: the SQL in §7.1 (Q8) gives ≤ 40 items, which are truncated to ~600 tokens of titles and first lines.
  - Model: the local LLM with a JSON schema `{highlights[≤5]{text, source_ids[]}, open_tasks[], tomorrow[]}`. Task and reminder lists are filled **deterministically from SQL**, not by the LLM. The LLM only writes the "highlights" text, and every highlight must cite one or more source ids (the grammar enforces it).
  - On the 2 GB SKU, or at thermal stage ≥ T2: an **extractive-only** summary (titles + counts, no LLM).
  - Generation runs as a background job with a thermal-burst budget (§10.4). It's skipped below 10 % battery (the extractive one is still produced).
- **UI**: screen **`22-daily-summary`**, being added by UX [PM 2026-10-21, v0.3]. Sections: Highlights (with source chips), Done today, Still open (tick off), Tomorrow, and buttons: "Read aloud" (TTS), "Dismiss", "Settings".
- **Schema**: `daily_summaries` table plus item kind `summary` (§7). Retention follows the user's setting like other items.
- **Privacy note**:
  - Only uses data the user explicitly captured. No audio is retained or re-processed.
  - Never leaves the device.
  - The summary is itself a deletable item. Deleting a source item marks the summaries citing it `stale`, and the cited text is removed from them on next open (`citations` FK).
  - It doesn't show on the always-on / locked state beyond "Your daily summary is ready".

### 9.2 Camera translation for Indian scripts (MVP feature #4) [PM 2026-10-21]

Pipeline:

```
 08 OCR capture (preview, "Translate" toggle, target lang EN/HI) → result shown on 09c-translate-overlay
   └─► capture (AF lock, 12 MP) ─► preprocess (scene/doc auto-detect, downscale ~2 MP)
        └─► pm-ocr.recognize(mode=scene|document)  — PaddleOCR / IndicPhotoOCR, script-ID per line
             └─► line grouping into sentences, drop conf < 0.5
                  └─► pm-translate.translate_stream(lines, src=auto(script), tgt=EN|HI)   — IndicTrans2-dist CT2 int8
                       └─► overlay renderer (QML): translated text boxes over original bboxes, tap = show source
                            ├─► optional pm-tts (Piper en / hi) "Read translation"
                            └─► save → ocr_doc item + translation stored (searchable both languages)
```

- **Languages [PM 2026-10-21, v0.3]**: **Devanagari only for MVP** (Hindi↔English; Marathi/Nepali Devanagari text is OCR'd but not a tested translation pair). **Tamil, Bengali and Telugu are planned for v2.** IndicPhotoOCR and IndicTrans2 already cover them, so v2 means a model pack update plus test sets, not an architecture change.
- **Latency budget** (4 GB SKU, short sign or menu ≤ 30 words):
  - capture → OCR ≤ 1.5 s;
  - translation ≤ 1.5 s, streamed line by line;
  - the first translated line appears ≤ 2.5 s after the shutter.
  - A progress cue shows at once and stays within the 1.85 s rule. Dense pages are progressive.
- **Offline**: works fully offline. A cloud translate/OCR offer appears on low confidence or at thermal stage ≥ T3, with per-request consent.
- ⚠ FEASIBILITY: CM5 latency for IndicTrans2-dist and IndicPhotoOCR is unmeasured (§6.10 gate). The 2 GB SKU can't hold OCR + translation + UI together with the LLM, so the LLM is unloaded during a translation session.
- **Memory**: the translated text is stored in `ocr_docs.translation_json` and indexed in FTS, so searching for "pharmacy" finds a photo of "दवाखाना" and opens the photo with the bbox highlighted.

---

## 10. Power states, battery, thermal

### 10.0 Compute decision and measured idle power (v0.3.2)

**Decision (v0.3.3, Anand 2026-10-21): stay on Pi CM5; the body may grow to 22–26 mm; idle-power reduction continues (§10.8, §10.3c).** **v1 compute = Raspberry Pi CM5 4 GB (CM5104032) only.** The 2 GB SKU (CM5102032) is **deferred and not part of v1**. Every `cm5-2g` reference in this doc is kept for later and is not a v1 deliverable (§6.11). Rev-2 candidate: Radxa CM5 (RK3588S2), §17. Source: `../research/compute-options.md` recommendation table.

**Measured idle (sourced, not our own measurement yet)**:

| Item | Measured | Conditions | Source |
|---|---|---|---|
| Pi CM5 4 GB idle | **2.4 W** at the wall (2.3 W Lite) | Pi OS Bookworm, kernel 6.6.51, on the IO board; display not stated | Geerling sbc-reviews #58, via research/compute-options.md |
| Pi CM5 idle | **2.65 W** | passive cooler, stock 2.4 GHz | shumeipai review, via research/compute-options.md |
| Pi CM5 load | 8.5 W stress-ng / 9.4 W HPL | same as the 2.4 W row | Geerling #58 |
| 4.3" DSI LCD | ≤ 0.4 W (120 mA at 3.3 V max) | module only | Lida datasheet, via research |
| Pi 5 default idle clock | 1500 MHz, Wi-Fi/BT on | default settings | LinuxLinks, via research |
| Radxa CM5 (RK3588S2) idle | **1.2 W** | Debian 11, kernel 5.10, Radxa IO board | Geerling #40 |
| RK3588 SoM suspend | 0.59 W | Forlinx | via research |

**Passive thermal budget** (`../mechanical/thermal_v3.md`, Al unibody, EST). The whole device sustained:
- **≈ 1.6–1.75 W held at 35 °C** (≈ 1.0 W lying flat).
- **≈ 0.6 W held at 45 °C** (≈ 0.35 W flat).
- Thermal mass ≈ **140 J/K**, τ ≈ 10 min. This **supersedes A-46 (225 J/K)**.

**Consequence**: the CM5 4 GB idle floor of **2.4–2.65 W is already above the 1.6–1.75 W sustained budget**. thermal_v3 shows skin at 45.7–46.7 °C held at 35 °C ambient, and 55–56 °C at 45 °C, from idle alone.

**The CM5 therefore can't be left on as a resting state.** The design rule from v0.3.2 is:

> **The CM5 is OFF (S4, MCU-held) by default. It powers up only for a user session or a scheduled job. Sessions are duty-cycled against a thermal energy budget, and the CM5 powers back off within 30 s of the session ending.** The MCU owns every wake source.

This replaces the earlier S2 "warm window" of 3 min as the default.

### 10.1 States

| State | CM5 | Display | MCU (STM32U0) | Entry | Exit / wake |
|---|---|---|---|---|---|
| **S0 Active** | running, `schedutil`, freq cap from the governor (§10.4) | on | Run/LP-run | any input | idle timer |
| **S1 Idle** | running, governor `powersave` | dimmed 30 % | Stop2 between events | 30 s no input [A-20] | touch/button |
| **S2 Display-off (post-session hold, ≤ 30 s default, v0.3.2)** | running at tuned idle (~1.9–2.2 W EST, 2.4–2.65 W untuned measured), engines loaded | off (DPMS) | Stop2 | 60 s idle or short Power press | Power/Action button, reminder → resume < 300 ms |
| **S3 Suspend (s2idle)** | **Not used until the §10.7 test passes its decision rule** (v0.3.2). CM5 suspend is unproven [Research §6.4] | — | — | — | — |
| **S4 MCU-held off (standby)** | **CM5 fully unpowered**: the MCU opens the 5 V boost / load switch. PMIC off | off | **Stop2 + RTC + EXTI wake (USART2 RX pin)**, ~µA | post-session hold expired (**30 s** default, v0.3.2), Power 2 s → Shut down, critical battery, thermal T4 | Power/Action button, RTC alarm (reminder / daily summary), USB-C attach (configurable) |
| **S5 Controlled shutdown** (transient) | sync, WAL checkpoint, unmount, `poweroff`, `SHUTDOWN_READY` | "Shutting down" | waits for CM5 3V3 to drop (≤ 10 s), then cuts power | user, battery 3 %, thermal T4, update | → S4 |
| **Ship mode** | off | off | charger BATFET off. MCU is unpowered except through the charger wake | Power 10 s hardware cut (`controls.md`) or factory | USB-C plug-in, or Power press (charger QON) |

- **Sleep = S2 for short gaps, S4 for everything else.** This is the only way to meet the battery target (§10.3).
- The cost is a cold boot from S4: target **< 10 s to the 02-listening screen**, with < 15 s as a hard limit. See ⚠ in §14.1.
- Speeding up the cold path:
  - Yocto minimal image, kernel without initramfs, and services started in parallel.
  - The UI is shown before the models load.
  - ASR partials (Vosk) load first, < 1 s.
  - **PTT pressed while the CM5 is off**: the MCU lights the "starting" LED pattern within 100 ms. (LRA is DNP in MVP [v0.3], so there's no haptic.) The PTT press is latched, so the CM5 opens the listening screen directly after boot.
- **Inhibitors** (block S2→S4): active PTT, OCR/LLM/translation job, update install, export, daily-summary generation.
- **Battery thresholds** (locked UX parameters): 20 % battery saver (amber, which forces governor ≥ T1 and a 1 min warm window), 10 % low-battery warning (15b), 3 % save + controlled shutdown. The MCU hard-cuts at cell UVLO (3.0 V) if the CM5 doesn't respond within 30 s.

Transitions:
```
 S0 ─10s─► S1 (backlight dim/off) ─► S2 ─hold 30 s─► S5 ─► S4 (CM5 off, MCU Stop2)
  ▲ input   ▲ input   │ Power/Action/reminder  │ Power / Action(PTT latched) / RTC alarm / USB-C
  └─────────┴─────────┘◄─────── cold boot < 10–15 s ───┘
 any ─(Power 2s→Shut down | batt 3% | thermal T4 | update)─► S5 ─► S4
 any ─(Power 10 s, MCU, even if Linux hung)─► Ship mode
```

### 10.2 Battery facts (v0.3.8) [PM 2026-10-21, v0.3.8]
**Cells** [Tech Research 2026-10-21, v0.3.11]:
- **Prototype: Akyga LP655063** (off-the-shelf): **3000 mAh, 1C (3 A max)**, assembled pack **≤ 65.5 × 51 × 7.0 mm** (bare cell 63 × 50 × 6.5 mm, all "max", no tolerances), **10 kΩ NTC on the yellow wire, β unstated**. Leads are 40 mm AWG24 on a JST ZHR-3 (re-terminate for J7). Datasheet facts: `../research/components.md` (~L424–442).
- **Production: custom cell per `../research/battery-rfq.md` Rev C**: **≥ 3000 mAh rated, 3100 mAh target**, **≥ 2C continuous (≥ 6 A), 3C (≥ 9 A) for 10 s peak**, pack **≤ 8.5 × 50.5 × 62.0 mm**, NTC **10 kΩ ±1 %, B25/85 = 3435 K ±1 %** (103AT-equivalent), 5-pos Molex Pico-Lock J7.
- There's no conflict between the two (A-78 resolved): the 1C / 65.5 × 51 × 7 mm figures are the prototype's.

**Pocket fit** (pocket 51.5 × 67 × 9.0 mm per the RFQ):

| | Prototype LP655063 | Production (RFQ Rev C) |
|---|---|---|
| Thickness | 7.0 mm max → 2.0 mm free → **1.5 mm foam spacer** (compresses to ~1.0 mm), leaving ≥ 0.5 mm for swelling. Replaces the 2.0 mm spacer from v0.3.8, which assumed a 6.5 mm pack | 8.5 mm max → 0.5 mm swelling allowance (≤ 9.0 mm absolute per RFQ). **No spacer** |
| Width | 51 in 51.5 → fits, 0.25 mm per side | 50.5 in 51.5 → fits |
| Length | 65.5 in 67 → fits: the 1.5 mm is only the pocket wall; below Z 11.5 the floor opens to the inner wall, giving ~3.5 mm of real end space. Leads exit at Y 32.0, U-turn (R 2.15, 0.55 mm to the wall) and run back over the cell face under Kapton into J7; re-terminated with staggered lengths 24.7/27.0/29.4/31.8/34.2 mm; no notch needed (Enclosure v4_22b, keepouts_v4_22b.md) [A-79 resolved] | 62.0 in 67 → ≥ 5 mm reserved for the lead bend ✅ |

- **Usable energy** (×0.83: 0.97 DoD × 0.90 converters × 0.95 ageing) [A-42]: prototype 3000 mAh ≈ **9.2 Wh**; production 3100 mAh target ≈ **9.5 Wh** (≥ 9.2 Wh at the 3000 mAh minimum).

**9 W cap vs. 1C** [A-67 resolved]:
- 9 W at the cell is 2.43 A at 3.7 V and **2.65 A at 3.4 V** (near cutoff), both below 1C = 3.0 A.
- At 3.2 V it's 2.81 A, still below 3.0 A. At 3.0 V, 9 W = 3.0 A, exactly 1C, so **pm-power scales the cap to `min(9 W, 0.95 × 3.0 A × V_cell)`** below 3.3 V. In practice the battery UVLO/critical thresholds (3 %, ≈ 3.4 V under load) shut down before that.
- Production cell: ≥ 2C (≥ 6 A) gives large current headroom (9 W ≈ 2.65 A at 3.4 V is < 0.9C). **The 9 W cap stays for thermal reasons** (§10.3b), not cell limits. The < 3.3 V scaling is a prototype-only necessity, kept harmlessly on production.

**NTC vs. BQ25895 TS/JEITA** [Tech Research 2026-10-21]:
- The prototype **Akyga LP655063 NTC is 10 kΩ on the yellow wire, β not stated**. The production NTC is B3435.
- TI's BQ25895 TS divider for a 103AT (B3435) NTC, 0–45 °C design point: **RT1 = 5.21 kΩ (REGN→TS), RT2 = 29.87 kΩ (TS→GND)** (RTH_COLD 27.28 kΩ, RTH_HOT 4.91 kΩ; datasheet Rev C §8.2.7.5.1, Eq. 2), per `../research/components.md` (~L424–442). Beta-model window with this divider: **B3435 ≈ 1.1–44.6 °C**; **B3950 ≈ 4.0–41.9 °C** (estimates).
- Both windows contain the firmware's 10–40 °C limits, so they're safe. With B3950 the hardware stops charging early in hot weather (41.9 °C). If B3950 is measured, recompute RT1/RT2 with Eq. 2 using **RTH(0 °C) ≈ 33.6 kΩ** and **RTH(45 °C) ≈ 4.35 kΩ** (beta-model EST), or with the actual R-T table.
- **Firmware thresholds are configurable until measured** (§12 `charge_ctrl`). A `charge_cfg` record in MCU config flash (CRC-protected, written by `SET_CHARGE_CFG` 0x2C from pm-power, or a factory tool) holds:
  - `ntc_r25`, **`ntc_beta`**, `rt1`, `rt2`;
  - the firmware thresholds: cold-off 10 °C / cold-on 12 °C / hot-on 38 °C / hot-off 40 °C / derate 35 °C;
  - a `beta_measured` flag.
- Defaults:
  - **Production: β 3435.**
  - **Prototype (β unknown)**: the MCU converts `TSPCT` with **both β 3435 and β 3950** and uses the **worse** reading per limit (hotter for the hot limits, colder for the cold ones) until `beta_measured` = 1.
  - Bounds-checked: thresholds must stay inside 0–45 °C, otherwise the defaults are kept.
- **M5b**: measure the β (§B4). The UI's hardware-window messaging uses the configured β.
- **At 45 °C ambient, expect no charging.** The UI shows "Too hot to charge".

**Runtime estimates** (per-profile energy from §10.3):

| Profile | Energy/day | **Prototype Akyga LP655063** (3000 mAh, 1C; ≈ 9.2 Wh usable) | **Production, RFQ Rev C** (3100 mAh target, ≥ 2C; ≈ 9.5 Wh usable) |
|---|---|---|---|
| **A light / "all-day typical use"** | 5.4–5.9 Wh | 59–64 % → ✅ **16 h met**, ≈ 25–27 h at that usage | 57–62 % → ✅ **16 h met**, ≈ 26–28 h |
| **B heavy** | ≈ 11.1 Wh | ≈ 120 % → ⚠ **≈ 13 h** | ≈ 117 % → ⚠ **≈ 13.7 h** (≈ 13 h at the 3000 mAh minimum) |
| **Standby (S4)** | ≈ 0.1 Wh/day | ✅ ≥ 24 h easily (≈ 90 days theoretical) | ✅ ≥ 24 h (≈ 95 days theoretical) |

The 2C rating doesn't change runtime; it only adds current headroom. The 9 W cap stays.

⚠ **Thermal limit**: at ≥ 35 °C ambient, Profile B is limited by the enclosure duty cycle (§10.3b: held 3 W ≈ 61 %, table 35 %, pocket 20 %) before the battery runs out. Heavy users get throttled sessions, not a dead battery. At 45 °C, all profiles are thermally limited (duty ≤ 21 % held).

### 10.3 Power budget vs. "16 h mixed use + ≥ 24 h standby" (v0.3.4, ~3.6 Ah cell) [PM/Enclosure 2026-10-21]

**Battery**: the v4_22 body was sized for a **~3.6 Ah / ~13.3 Wh** cell (EST); **v0.3.11: prototype LP655063 3000 mAh / production ≥ 3000 mAh (3100 mAh target), see §10.2 for runtime**. The table below keeps the 3.6 Ah basis for reference (8.5 × 51 × 65.5 mm, EST 0.47 Wh/cc, from `../mechanical/thermal_v3_ribs.md` §v4). That replaces 2.7 Ah. Usable at the 5 V rail ≈ 13.3 × 0.97 × 0.90 × 0.95 ≈ **11.0 Wh** [A-42]. At 1C (3.6 A), the cell could support ~12 W. The system cap stays at **9 W** (§10.5) as a thermal and margin choice.

Per-state power (5 V rail, CM5 4 GB; measured idle from §10.0, EST deltas, §10.8 targets):

| State | Untuned (measured / EST) | Tuned target (§10.8) |
|---|---|---|
| S0 interactive, 40 % backlight | 2.8–3.05 W | **≤ 2.0 W** (budget uses 2.6 W until measured) |
| S0 local AI burst | 8.0–9.0 W (≤ 9 W cap) | same |
| S2 display-off hold | 2.4–2.65 W | ≤ 1.6 W (budget uses 2.2 W) |
| Cold boot | 40–60 J | ≤ 50 J |
| S4 (CM5 off, MCU Stop2) | ≤ 4 mW | ≤ 4 mW |

| Profile (16 h waking day) | Energy | % of 11.0 Wh | Verdict |
|---|---|---|---|
| **A light / "all-day typical use"**: 25 sessions, 60 min screen-on, 12 min local AI, 30 s hold, 25 cold boots, daily summary | **≈ 5.4 Wh** (policy) / 5.9 Wh (untuned) | **49–54 %** | ✅ 16 h with ~45 % margin. At this usage the cell lasts ≈ **30 h** |
| **B heavy**: 2 h screen-on, 30 min AI, 40 sessions | ≈ 11.1 Wh | ≈ 101 % | ⚠ ≈ **16 h, borderline** (was ≈ 12 h on 2.7 Ah). Thermal duty limits (§10.3b) bite before energy does at ≥ 35 °C |
| **C always-on** (S2 all day, untuned 2.4 W) | ≈ 38 Wh | ≈ 350 % | ❌ ≈ 4.6 h, and thermally impossible |
| **Standby** (S4) | ≈ 0.1 Wh/day | ≈ 1 %/day | ✅ ≥ 24 h easily. Theoretical ~100 days; in practice cell self-discharge and protection-IC drain dominate [EST] |

**Verdict (v0.3.4)**:
- 16 h "all-day typical use" holds with a wide margin, and heavy use now roughly reaches 16 h on energy.
- **CM5-off-by-default remains the core strategy**, because the **thermal** budget (not energy) is what blocks keeping the CM5 on.

### 10.3b Thermal duty-cycle budget: enclosure v4_22, passive, fan-free (v0.3.4) [PM/Enclosure 2026-10-21]

**Baseline enclosure: v4_22 passive aluminium unibody, 22 mm, no fan** (`../mechanical/thermal_v5_22.md` §"v4_22 passive duty-cycle"; thermal_v3_ribs.md §v4). The micro-blower variant v5_22 is **not baseline**. Software keeps only an unused "fan" hook: the `Platform` HAL has a no-op `fan_set(pct)`, and there's no fan driver in v1.

**Frozen sustained device power** (all heat: CM5 + backlight + power stage):

| Case | 35 °C ambient (skin ≤ 43 °C) | 45 °C ambient (skin ≤ 48 °C) |
|---|---|---|
| **Held** | **1.85 W** | **0.66 W** |
| **Flat (table, on its back)** | **1.08 W** | **0.39 W** |
| Pocket (enclosure model) | 0.64 W | 0.23–0.24 W |

**Time-to-throttle and duty** (enclosure model, starting from cold; C ≈ 205 J/K; off power 0.05 W). This **replaces** the v0.3.2/v0.3.3 time-to-throttle and duty table. Soft = governor's first throttle step; Limit = skin limit reached; Duty = allowed long-run average on-fraction:

| Case | τ | 35 °C budget | 3 W: soft / limit | 3 W duty | 5 W: soft / limit | 5 W duty | 45 °C budget | 3 W: soft / limit | 3 W duty | 5 W: soft / limit | 5 W duty |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Held | 830 s | 1.85 W | 564 / 744 s | 61 % | 260 / 331 s | 36 % | 0.66 W | 70 / 164 s | 21 % | 19 / 70 s | 12 % |
| Table | 1464 s | 1.08 W | 480 / 599 s | 35 % | 242 / 302 s | 21 % | 0.39 W | 69 / 157 s | 11 % | 19 / 69 s | 7 % |
| Pocket | 2500 s | 0.64 W | 447 / 547 s | 20 % | 234 / 289 s | 12 % | 0.23 W | 69 / 154 s | 6 % | 19 / 69 s | 4 % |

⚠ **The 45 °C values are optimistic**:
- The single-node model underestimates the fast SoC-to-pad transient, so trip times under ~30 s are indicative only (thermal_v5_22).
- At 45 °C, treat any local AI burst as likely to reach Warn/Soft within tens of seconds.

**Implications for software**:
- At 35 °C held, a 3 W session reaches Soft after ≈ 9.4 min and the limit after ≈ 12.4 min.
- A 5 W AI-heavy session reaches Soft after ≈ 4.3 min.
- On a table or in a pocket the budget is roughly halved or quartered.
- No case sustains the 2.4–2.65 W CM5-on idle (thermal_v3_ribs: "no variant sustains idle in any case"). Hence CM5-off-by-default and §10.8.

**Governor session accounting** (pm-power, extending §10.4):
1. `E_used` is the heat above budget, decaying with the case's τ (830 / 1464 / 2500 s for held / table / pocket), using the budget for the **detected case** (§10.4.3). The MCU keeps integrating while the CM5 is off and reports it at `HELLO_ACK`.
2. **Admission**: a local AI job runs at full speed only if the predicted case NTC at job end stays below **Warn**. Otherwise it's slowed, queued, or offered to the cloud (per-request consent).
3. **Session end**: backlight off at 10 s, CM5 off at 30 s.
4. **Cooldown gate**: no non-user wake while the NTC ≥ Warn − 1.5 K.

### 10.3c Body thickness (v0.3.4: decided, 22 mm)

The enclosure sweep (thermal_v3_ribs.md §v4) supersedes the v0.3.3 area-scaling estimate.

| Body | Held 35 °C | Table 35 °C | Pocket 35 °C | Held 45 °C | Cell (EST) | Mass (EST) |
|---|---|---|---|---|---|---|
| v3 20 mm | 1.75 W | 1.02 W | 0.62 W | 0.62 W | ~3.0 Ah | ~212 g |
| **v4_22 (baseline)** | **1.85 W** | **1.08 W** | **0.64 W** | **0.66 W** | **~3.6 Ah** | **~233 g** |
| v4_24 | 1.93 W | 1.14 W | 0.66 W | 0.69 W | ~4.5 Ah | ~258 g |
| v4_26 | 2.02 W | 1.20 W | 0.68 W | 0.72 W | ~5.3 Ah | ~283 g |

- Thickness buys only +6 % (22 mm) to +15 % (26 mm) of thermal budget. Each extra 2 mm mainly buys battery.
- Ribs add +2 % (recessed) or +5 % (proud), and the proud ribs are rejected.
- Idle power reduction (§10.8) remains the main lever. The enclosure study's targets are idle **≤ 1.7 W held / ≤ 1.0 W table / ≤ 0.6 W pocket** at 35 °C, adopted as §10.8 stretch goals.

### 10.4 Skin-temperature power governor (in pm-power), frozen limits (v0.3.4) [PM/Enclosure 2026-10-21]

**Rated operating range: 0–40 °C; limited use at 45 °C** [PM 2026-10-21]. Above 40 °C the UI shows "limited use when hot".

#### 10.4.1 Frozen limits
```
T_lim(Ta) = 43 °C                     if Ta ≤ 40 °C
          = min(Ta + 3 °C, 48 °C)     if Ta > 40 °C
```
- Sustained device power budgets are frozen at §10.3b: **held 1.85 W @35 °C / 0.66 W @45 °C**, and **flat 1.08 W / 0.39 W**. Pocket uses the enclosure model values (0.64 / 0.23 W).
- CM5 SoC: target < 65 °C sustained. SoC ≥ 80 °C triggers the Protect stage. This supersedes the earlier 70/75/85 SoC stage triggers; the Raspberry Pi firmware's 80/85 °C throttle stays as a backstop.

#### 10.4.2 Sensors
- **Case NTC (skin)**: 10 kΩ NTC bonded to the **inside of the aluminium back plate at (−55.3, −10) mm** (enclosure coordinates, next to the left grip). It's wired by a **2-pin JST SH (1.0 mm) connector on the carrier**.
  - **Read by the STM32U0 ADC** (preferred: it works with the CM5 off and is independent of Linux).
  - **Netlist v3** [Schematic netlist v3]: NTC on **ADC PB0 (ADC1_IN17)**, biased from **PA12 through 10 kΩ 1 %**. **PA12 is driven high only while sampling** (set high, wait ≥ 100 µs for settling, convert, set low), so the divider draws nothing between samples. Sampled at 1 Hz in S0–S2 and every 60 s in S4. Ratiometric: VDDA = bias source, so the 1 % resistor and the NTC β dominate error; the M5b two-point calibration trims the offset. ADC 12-bit, 16× oversampled, with a β/Steinhart–Hart table in MCU flash.
  - Reported in `EVT_THERMAL` (§11).
  - [A-63 resolved: PB0 ADC.]
- **Load-dependent hot-spot compensation**: the NTC reads **~0.3 K/W below the hot spot** (enclosure estimate; ~75 mm from the SoC zone). The governor uses
  `T_skin,hot = T_NTC + k_hs · P_avg(τ_hs)`, with `k_hs = 0.30 K/W` initial and `P_avg` a first-order filtered device power (τ_hs ≈ 60 s initial).
  `k_hs` and `τ_hs` are calibrated per enclosure revision in M5b (§B4) against thermocouples at the SoC zone and grip, and stored in MCU flash and `/var/lib/pm/thermal_cal.toml`.
  **Stage thresholds below compare `T_skin,hot`** [A-64 **confirmed** by Enclosure 2026-10-21 for the prototype]. The NTC lag is double-counted on purpose, which is conservative. Relax this after M5b calibration: thresholds then move to the raw NTC plus a fitted offset, or the margins are reduced.
- **Battery (cell) NTC** [Schematic netlist v3]: wired **only to the BQ25895 TS input** (not to an MCU ADC). The MCU reads cell temperature as **`TSPCT`** (BQ25895 REG10, TS voltage as % of REGN; ADC conversion via `CONV_START`/`CONV_RATE`), converted to °C with the same NTC table and divider (RT1/RT2). Backup: **MAX17055 `Temp` register** (internal die/thermistor-input temperature; it's a fallback for plausibility only, since it doesn't sense the cell directly unless the gauge's TH pin is wired) [A-75]. JEITA is enforced in the charger hardware (§12).
  - **At 45 °C ambient, expect no charging.**
  - UI messaging on screen 15 and the battery icon: "Too hot to charge, charging resumes below 38 °C". When the CM5 is off, the LED shows an amber double-blink.
  - The system stays powered from USB-C.
- **SoC temperature**: `/sys/class/thermal/thermal_zone0` (cross-check with `vcgencmd measure_temp`).
- **Ambient estimate**: the case NTC after ≥ 30 min in S4 (equilibrium), tracked by an RC model. Needed for T_lim when Ta > 40 °C.
- **System power**: fuel gauge (1 Hz), plus INA226 on the prototype.

#### 10.4.3 Case (held / table / pocket) detection and auto-brightness: VEML7700 [Enclosure 2026-10-21]

**Hardware**:
- **VEML7700** ambient light sensor on the side-key flex, behind a **2.5 mm window in the front bezel at (−58, 20)**.
- On **I2C1 via flex J11 pins 9/10** (SCL/SDA), 7-bit address 0x10.
- **No interrupt line**, so it's polled. There's no proximity sensor or IMU in v1.
- **Resolved A-66** [Schematic netlist v3]: it's on the **STM32U0 I2C1 (PB6 SCL / PB7 SDA)**, on the always-on 3V3 rail, shared with the BQ25895, MAX17055 and STUSB4500. The MCU senses light with the CM5 off.

**DT/I2C note**:
- On the MCU bus, there's no CM5 device-tree node. pm-power gets lux from the MCU in `EVT_THERMAL` (new field `lux` u16, saturating) and `EVT_LIGHT` (0x2A, on case change only).
- The bezel window attenuates light, so lux needs a window gain factor calibrated in M5b (`lux_gain` in `SET_THERMAL_CAL`).

**Low-power polling**:
- The sensor is put into shutdown (`ALS_SD=1`, ~0.5 µA) between single readings at gain ×2, IT 100 ms (~45 µA for ~110 ms).
- **S0**: 1 Hz for auto-brightness (power-save mode PSM 2).
- **S1/S2 (display off)**: every 5 s.
- **S4 (CM5 off)**: every 30 s, only while the case NTC is above Warn − 3 K or when the cooldown gate is evaluating a wake. Otherwise not at all.
- Average sensor current is < 1 µA in S4 and ~5 µA in S0, negligible against the budget [EST].

**Pocket heuristic** (pm-power, mirrored in the MCU):
- **Dark** = lux < 3 lx (enter) / > 10 lx (exit): **hysteresis**, 5 s debounce.
- **Pocket** = dark **and** (display off **or** no touch/key input for ≥ 30 s).
- **Dark-room guard**: a dark reading during active use is not pocket. While the display is on and input happened in the last 30 s, it's held (or table), even at night. The guard combines:
  1. **Display state and input**: active interaction overrides darkness.
  2. **Time of day (local RTC)**: between 21:00 and 07:00, dark plus display off is classed as **table** (likely a nightstand), *unless* check 3 trips.
  3. **Heat-rise check**: if the NTC rise rate for the measured P exceeds the table model by > 30 %, step down to **pocket** regardless.
- **Held vs table** with the display on: input in the last 30 s → held, otherwise table. Light doesn't help here.
- **Display off without a valid lux reading** (sensor fault or NACK): fall back to **pocket** (the v0.3.4 conservative default).
- Lux is used only on the device as a case signal. It is never stored except as the case label in the thermal-stage log.

**Auto-brightness**:
- Backlight % = clamp(a·log10(lux_corr) + b, 10 %, user max), smoothed (τ 2 s up / 5 s down).
- A user override offsets the curve.
- Governor stage caps (Soft −30 %, Hard floor 10 %) always win.
- The default is on, with a toggle in Settings → Display.

#### 10.4.4 Throttle stages (frozen) and actions

The NTC values below are case-NTC thresholds for **Ta ≤ 40 °C / Ta = 45 °C** (T_lim 43 / 48). For Ta between 40 and 45 °C, each threshold = T_lim(Ta) − offset. **Hysteresis is 1.5 K per stage** (release when T ≤ threshold − 1.5 K), with a 30 s minimum dwell.

| Stage | Threshold (Ta ≤ 40 / 45 °C) | Offset from T_lim | Actions |
|---|---|---|---|
| **Normal** | below Warn | — | full speed within the 9 W cap and session admission (§10.3b) |
| **Warn** | **41.0 / 46.0 °C** | −2.0 K | **No new local AI bursts** (running jobs finish). Offer cloud for the next heavy request (per-request consent). Background jobs deferred. Banner 20i |
| **Soft** | **41.8 / 46.8 °C** | −1.2 K | **CPU frequency down** (−300 MHz per 0.5 K above Soft, floor 1.0 GHz) and **backlight down** (−30 %). LLM threads ≤ 2 |
| **Hard** | **42.5 / 47.5 °C** | −0.5 K | **CPU/GPU at minimum** (`scaling_max_freq` = min OPP, `gpu_freq` min), **backlight at the floor** (10 %). Local AI refused. Screen 20h-err-thermal |
| **Protect** | **43.0 / 48.0 °C, or SoC ≥ 80 °C** | 0 K | **Suspend compute: display off, then controlled power-off to S4** (or S3 if §10.7 adopts it). The MCU blocks power-on until the NTC < Warn − 1.5 K (LED "hot" pattern). A user PTT press during the block gives only the LED/visual "too hot" feedback |

- Cloud offload is never automatic: heat only changes what's **offered**, through consent dialog 12b.
- Battery-saver mode (20 %) also forces at least Warn-level behaviour (no background AI).

### 10.5 System power cap (~9 W) [PM 2026-10-21]
- Why: the prototype cell is rated 1C (2.7 A × ~3.3–3.7 V ≈ 9–10 W). Sustained discharge above that ages the cell and trips the protection.
- **Software layer (pm-power)**: the PI loop from §10.4 runs with `P_budget ≤ 9 W` measured at the cell (fuel-gauge current × voltage, 1 Hz, plus a 10 Hz fast window when the MCU flags it). Actuators, in order:
  1. Mutual exclusion of heavy loads: camera capture + LLM never run together, and the amp is limited during an LLM burst.
  2. LLM/ASR thread count.
  3. CPU frequency cap.
  4. Backlight.
- **MCU fast path**: if the cell current is > 2.7 A for > 2 s, the MCU sends `EVT_OVERCURRENT` and asserts `MCU_IRQ`. pm-power steps down one stage immediately. If it's > 3.2 A for > 5 s, the MCU requests S5.
- **Hardware backstop**: the charger/BATFET and the pack protection overcurrent limit.
- On USB-C power, the cap applies to cell discharge only. The power path supplies the rest, and the thermal limits still apply.

### 10.6 Aggressive power policy (v0.3.2)

These are enforced by `pm-power` plus static config. Each lever's saving is EST until M5b measures it (PM-P1).

| Area | Policy | Mechanism |
|---|---|---|
| **CM5 residency** | Off by default (S4). On only for a session or a scheduled job. Off 30 s after the session ends. No "warm window" by default (user option: 30 s / 1 min / 3 min, with a battery and heat warning) | MCU `CM5_PWR_EN`; `SHUTDOWN_READY`; EEPROM `POWER_OFF_ON_HALT=1`, `WAKE_ON_GPIO=1` |
| **Backlight** | Default 40 %. **Dim to 10 % after 5 s without touch, off after 10 s** within a session (the listening/processing overlays keep it on). Panel rail off (not just PWM 0) in S2. Never above the governor stage cap | PWM + panel enable GPIO; DPMS |
| **Wi-Fi / BT** | **rfkill-blocked by default.** Unblocked only for: a consented cloud request; a user-initiated or opted-in update check; the Wi-Fi/BT settings screens; optional NTP at boot (if the user allows "sync time online"); BT earbuds while paired and audio is playing. Re-blocked 30 s after last use. `iw dev wlan0 set power_save on` whenever up | `rfkill block wifi bluetooth`; NetworkManager connection on demand; a pm-cloud/pm-update "radio lease" API with a timeout |
| **CPU caps** | UI/idle: `scaling_max_freq` 1.5 GHz, `arm_freq_min` 500 MHz [A-54: verify the CM5 minimum OPP], **cores 2–3 offline** when no engine is busy. Burst: all 4 cores up to 2.4 GHz within the 9 W cap and governor stage | `/sys/devices/system/cpu/cpuN/online`, cpufreq sysfs, `config.txt` `arm_freq_min` |
| **GPU** | Qt renders only on change (no continuous animation in idle screens). `v3d` idle clock default | QML `Animation` audit, `QSG_RENDER_LOOP=basic` [A-55] |
| **Unused peripherals off** | HDMI disabled; PCIe off (`dtparam=pciex1=off`); Ethernet PHY absent/disabled on the custom carrier; USB host ports off except during debug; activity/power LEDs off; camera sensor powered down when not on screen 08/09c; amp `SD` low unless audio is playing; mics powered only during PTT (MCU); `fan` none | DT overlays/dtparams, regulator GPIOs, `uhubctl`/DT on the prototype |
| **Background work** | Embeddings, model warm-up and summary LLM run only while **charging** or within an existing session's thermal budget. No periodic CM5 wake for housekeeping | pm-core job scheduler checks power source and `E_used` |
| **MCU owns wake** | All wake sources go through the STM32U0: buttons, PTT (latched), RTC alarm (reminder / summary), USB-C attach (configurable: charge LED only, CM5 stays off), and the thermal cooldown gate. The CM5 never polls or keeps timers for wake | §11, §12 |
| **Boot energy** | Minimise E_boot: Yocto image, no initramfs, parallel units, UI before models, Vosk partials first. Target ≤ 12 s, ≤ 50 J per boot | §10.1 |

### 10.7 CM5 suspend / s2idle test plan and decision rule (v0.3.2)

**Question**: does any Linux sleep state on the CM5 4 GB beat "MCU cuts power + cold boot" for short gaps (seconds to minutes between sessions), on energy and/or latency, without breaking peripherals?

**Setup**:
- Hardware: CM5 4 GB on the IO Board, our 4.3" DSI panel, I2S mics/amp, Camera Module 3, NUCLEO-U031R8 driving `GPIO_WAKE` and `RUN`.
- Measurement: INA226 at 5 V input sampled at ≥ 1 kHz (or a Joulescope/PPK2-class meter).
- Images: Pi OS Bookworm, current kernel, and the latest rpi-6.x kernel. Firmware EEPROM at the latest stable.

**Test matrix**:

| # | State | How | Measure |
|---|---|---|---|
| S-1 | Supported states | `cat /sys/power/state /sys/power/mem_sleep`, kernel config (`CONFIG_SUSPEND`, `PM_SLEEP`) | which of `freeze` (s2idle) / `mem` (deep) exist |
| S-2 | Tuned idle baseline | §10.6 policy applied, display off | P_idle (10 min mean) |
| S-3 | **s2idle** | `echo freeze > /sys/power/state` (or `systemctl suspend` with `mem_sleep=s2idle`) | P_s2idle (10 min mean); wake via GPIO (MCU) and the RTC; resume latency (wake edge → first UI frame, high-speed camera); time to working ASR |
| S-4 | deep (`mem`) | only if S-1 lists `deep` | as S-3 |
| S-5 | Halt, PMIC off | `poweroff` with `POWER_OFF_ON_HALT=1` | P_halt (5 V still applied); wake via GPIO; boot time |
| S-6 | MCU rail cut (S4) | MCU opens the load switch | P_S4 at the cell; E_boot (J) and t_boot to listening |
| S-7 | Peripheral resume health | 100 cycles each for S-3/S-4: DSI panel + touch, I2S capture/playback, camera open, Wi-Fi reassociate (when unblocked), UART link to the MCU, USB, RTC time, watchdog | pass/fail per cycle, dmesg errors |
| S-8 | Thermal | skin/NTC over 30 min in the best sleep state at 35 °C | ΔT vs ambient |

**Decision rule** (record the result in §10.1 and the milestone report):
1. Compute the break-even gap `t* = E_boot / (P_sleep − P_S4)`. Example: E_boot = 50 J and P_sleep = 0.5 W gives t* ≈ 100 s.
2. **Adopt s2idle (or deep) as S3** only if **all** of these hold:
   - (a) P_sleep ≤ 0.6 W, so it fits the 45 °C sustained budget and doesn't heat the device;
   - (b) resume to the listening screen ≤ 1.0 s;
   - (c) 100/100 cycles pass S-7 with no peripheral loss;
   - (d) no watchdog/MCU-link failures.
3. If adopted: use S3 for the post-session hold and for gaps ≤ min(t*, 2 min). After that, go to S4. The latency win becomes the reason to keep it.
4. If 0.6 W < P_sleep ≤ 1.2 W and (b)–(d) pass: use S3 **only** as a ≤ 30 s post-session hold, replacing the 2.2 W S2 hold. Otherwise use S4.
5. If P_sleep > 1.2 W, or any of (b)–(d) fails: **reject**. S3 stays unused, and v1 ships S2 (≤ 30 s) plus S4. Optimise cold boot instead (target ≤ 10 s).
6. The same test runs again on Radxa CM5 in rev 2 (RK3588 SoM suspend is reported at 0.59 W).

### 10.8 Idle-power reduction workplan, CM5 4 GB (v0.3.3)

**Why**: every watt of idle saved is thermal budget the body doesn't have to supply. Thickness buys only about +0.05–0.16 W of sustained budget (§10.3c), while a single lever below can save 0.1–0.7 W. **Goal**: on our prototype, measured at the 5 V input, after all levers:
- tuned S2 (CPU idle, display off) **≤ 1.6 W** (stretch 1.4 W);
- S0 interactive at 40 % backlight **≤ 2.0 W** (stretch 1.8 W).
Start point: measured 2.4–2.65 W (§10.0).

**Method for every lever**:
- Prototype on the IO Board, at 25 °C, 5 V input measured with INA226 or a USB power meter at ≥ 10 Hz, as a 5-minute mean after 2 minutes of settling.
- `vcgencmd pmic_read_adc` for per-rail deltas. It omits the 5 V rail, so it isn't a substitute for input power [forum].
- One lever at a time, in the order below, **cumulative**, then each lever removed individually for attribution.
- Results go in `software/bench/idle_power.csv` and update §10.3.

Ranked by expected saving (largest first):

| Rank | Lever | Config / mechanism | Expected saving | Source / basis | Measurement step | Target / pass |
|---|---|---|---|---|---|---|
| 1 | **CM5 off between sessions** (S4) + `POWER_OFF_ON_HALT=1` | EEPROM `POWER_OFF_ON_HALT=1` (default `1` on CM5 per docs), `WAKE_ON_GPIO` is not relevant on CM5 (the power button/`GLOBAL_EN` wakes). The MCU also cuts the 5 V rail | Off-state **~1–1.4 W → ~0.01 W** at halt. ~0 W with the MCU rail cut | RPi docs `power-supplies.adoc` ("around 1 W to 1.4 W … drop … to around 0.01 W") and `eeprom-bootloader.adoc`; Geerling "Reducing Raspberry Pi 5's power consumption by 140x" | P(halt) with and without the setting; P(S4) at the cell | halt ≤ 0.02 W; S4 ≤ 4 mW at the cell |
| 2 | **Idle clock floor** | `config.txt`: `arm_freq_min=500`, `gpu_freq_min=500`. Governor `schedutil`/`powersave` in idle | **~0.4–0.7 W** (a single user report on Pi 5 Lite: 2.7 → 2.0 W) | RPi forum t=384340 (Pi 5 default idle clock is 1500 MHz); LinuxLinks note via research | idle P at the 1500 vs 500 MHz floor; check `time_in_state` | ≥ 0.4 W saved; no UI jank (frame time p95 ≤ 20 ms) |
| 3 | **Wi-Fi/BT off** | Runtime `rfkill block` (default). Build variant: `dtoverlay=disable-wifi,disable-bt` if a product variant needs no radio. `iw … power_save on` when up | **~0.18 W** (3V7_WL_SW rail ~183 mW → 0 with the overlays). rfkill may leave part of this on [EST] | RPi forum t=363330 | P with radio up/idle, rfkill-blocked, overlay-disabled | rfkill ≥ 0.12 W saved; if < 0.1 W, power-gate the module by DT/regulator |
| 4 | **Backlight / panel** | Default 40 %; dim at 5 s, off at 10 s; panel rail off in S2 (§10.6) | up to **0.4 W** at full brightness; ~0.15–0.25 W at 40 % [EST] | Lida 4.3" LCD ≤ 120 mA @ 3.3 V (via research/compute-options.md) | P vs PWM 0/20/40/70/100 %; panel rail off | 40 % ≤ 0.2 W; rail-off = 0 |
| 5 | **CPU frequency cap during UI** | `scaling_max_freq` 1.5 GHz for UI; 2.4 GHz only for admitted bursts | **~0.2 W** on VDD_CORE when active (722 mW at 1.5 GHz vs 930 mW at 2.4 GHz). Little at true idle | RPi forum t=363330 | P during scripted UI interaction at 1.5 vs 2.4 GHz | ≥ 0.15 W saved in S0 |
| 6 | **Ethernet PHY off** (the CM5 has an on-module GbE PHY) | DT: disable `genet`/PHY (`ethernet` node `status="disabled"`), or `ip link set eth0 down`, plus PHY power-down via MDIO | **~0.05–0.3 W** [EST, unsourced] | Research: the Pi 5 paper reports 11.2 % idle reduction for "disabling … WiFi and Ethernet" (DOI 10.1109/compsystech65493.2025.11136932) | P with link down vs node disabled | ≥ 0.05 W; keep if any saving is measurable |
| 7 | **HDMI off** | No HDMI on the custom carrier. On the prototype: no HDMI cable at boot, and disable HDMI in DT (`hdmi` nodes disabled / `vc4-kms-v3d,nohdmi` [A-60]) | **~0.1 W** (≈ 96 mW by booting without a display; only ~10 mW from blanking alone) | RPi forum t=363330 | P with HDMI cable present at boot vs absent vs DT-disabled | ≥ 0.08 W |
| 8 | **Camera fully off when unused** | Close libcamera; sensor regulator/enable GPIO off; CSI lanes idle | **Avoids +1.7 W** seen with a camera active (HQ cam report). Idle saving is small if already closed | RPi forum t=384340 | P with the camera pipeline open, closed, and powered off | closed + powered off = baseline ± 0.02 W |
| 9 | **PCIe / USB off** | `dtparam=pciex1=off` (the external x1 port only; RP1's internal link must stay). USB: no host ports on the carrier; `usbcore.autosuspend=1`; on the prototype `uhubctl` port power off | **~0.05–0.15 W** [EST] | — (to measure) | P with each disabled | ≥ 0.03 W each, otherwise drop |
| 10 | **Unused cores** | Runtime hotplug (`cpuN/online=0`) for cores 2–3 in idle (preferred). Static `maxcpus=2` (kernel cmdline) is **only** an experiment: it blocks 4-core bursts | **~0.02–0.15 W** [EST]. Idle A76 cores already sit in WFI, so the gain may be small | — (to measure) | P with 4/2/1 cores online at idle; burst latency impact | keep only if ≥ 0.05 W and no L2/L5 regression |
| 11 | **Minimal systemd / wakeups** | Yocto minimal image; no avahi/cups/bluetoothd (unless leased)/ModemManager/triggerhappy; timers coalesced; `powertop` wakeups/s budget | **~0.02–0.1 W** [EST] | — | wakeups/s (`powertop --csv`) and P before/after | ≤ 50 wakeups/s at idle; ≥ 0.02 W |
| 12 | **Audio path idle** | ALSA device closed when silent (no PipeWire keep-alive; `suspend-timeout-seconds=1`); I2S clocks stopped; amp `SD` low; mics unpowered by the MCU outside PTT | **~0.01–0.05 W** [EST] (class-D amp quiescent is a few mA at 5 V [A-61]) | amp datasheet to cite | P with the stream open-silent vs closed vs amp SD low | ≥ 0.01 W; no pop on resume |
| 13 | **LEDs off, misc DT** | `dtparam=act_led_trigger=none`, power LED off; disable unused I2C/SPI/UART instances | **< 0.01–0.02 W** [EST] | — | P delta | any |
| 14 | **Negative `over_voltage_delta`** (undervolt) | `over_voltage_delta=-10000…-25000` µV with `arm_freq` unchanged | **~0 W at idle** (DVFS already lowers idle voltage; Geerling measured identical idle across deltas). Some saving under load, with an **instability risk** | Geerling "Overclocking and Underclocking the Raspberry Pi 5" | P idle/burst at 0/−10/−25 mV; 24 h stress + `vcgencmd get_throttled` | **last resort**. Adopt only if ≥ 0.2 W saved in burst with zero errors over 24 h × 3 units; never in v1 by default |
| — | Lower `arm_freq` ceiling (e.g., 2.0 GHz) | `arm_freq=2000` | lower burst power, no idle change; longer tasks (energy per task may not improve) | Geerling (idle identical) | J per ASR/LLM task at 2.0 vs 2.4 GHz | adopt only if J/task falls |

**Expected cumulative result** [EST]:
- 2.4–2.65 W, minus ranks 2–3 and 6–13 (≈ 0.6–1.2 W), gives ≈ **1.4–1.9 W** tuned S2 idle.
- Backlight at 40 % adds ~0.2 W, so S0 ≈ **1.6–2.1 W**.
- This is the M5b deliverable (PM-P1). §10.3 uses 2.2 W (S2) / 2.6 W (S0) until the measurements replace them.

**Order of work** (M5b, ~1.5 wk):
1. Day 1–2: rig and baseline.
2. Day 3–4: ranks 1–5.
3. Day 5–6: ranks 6–13.
4. Day 7: rank 14 experiment (optional).
5. Day 8: write up, update §10.3/§10.3b/§10.3c, hand to mechanical for the final thickness decision.

---

## 11. CM5 ↔ MCU protocol

**Physical** [Schematic netlist v3]:
- **UART**: 115200 8N1, **CM5 UART0 (GPIO14 TXD / GPIO15 RXD, `/dev/ttyAMA0`) ↔ STM32U0 USART2**. There's no console on this UART.
  - Wake from Stop2: the design doesn't rely on the USART2 peripheral's own wake support [A-68: check the STM32U031K8 RM for USART2 Stop-mode wake capability]. The **USART2_RX pin is also configured as an EXTI falling-edge wake line** before entering Stop2.
  - The CM5 sends a `0x00` preamble byte and waits **2 ms** before each frame. The MCU re-enables USART2 on wake, discards the preamble, and holds the clocks on until 50 ms of link silence.
  - If USART2 turns out to support Stop2 wake natively, the EXTI path is kept anyway as a belt-and-braces measure.
- **`MCU_IRQ_N`**: MCU open-drain output, active low, to **CM5 GPIO4**, with a 10 k pull-up to CM5 3V3. The MCU asserts it for pending events (low until the CM5 reads `EVT_*`, then released), and as a wake for s2idle.
  - In S4 the CM5 is unpowered, so the MCU **must keep the pin Hi-Z** (no back-powering the CM5 IO). The same applies to USART2_TX: the MCU puts it in analog/Hi-Z while `CM5_PWR_EN` is low.
- **Power control**: the MCU controls the CM5 5 V load switch / boost enable and the `RUN` line.
- **+3V3_PERIPH** [Schematic netlist v3] (mics, display, camera): **its own buck U12 (TLV62585 from VSYS)**. **EN is driven by CM5_3V3 through a 10 k/100 k divider**, so the rail **tracks CM5 power in hardware; no GPIO (CM5 or MCU) controls it** [A-70 resolved].
  - **Power-on**: MCU closes the CM5 5 V switch → CM5 PMIC brings up CM5_3V3 → U12 EN crosses its threshold (CM5_3V3 × 100/110 ≈ 3.0 V; check against the TLV62585 EN V_IH at layout) → +3V3_PERIPH soft-starts (~1 ms) → the kernel probes the display, camera and I2S mics.
  - **Power-off**: CM5 halts → MCU opens the 5 V switch (or the PMIC drops) → CM5_3V3 falls → U12 EN low → +3V3_PERIPH off. It falls *with* the CM5 rails, never after.
  - **Consequences**:
    - Mics, display and camera are physically unpowered in S4/ship.
    - pm-power can't power-cycle the display/camera separately; use panel sleep, camera stop and `MIC` mute instead.
    - **No back-powering**: MCU pins into the peripheral domain (`MUTE_STATUS_IO` PA10 input; `MIC_PWR_EN` PA11 output, which is held low when CM5_3V3 is absent) are inputs, or driven low when CM5_3V3 is absent.
  - If a CM5_3V3 brown-out glitch toggles EN, the divider's slow edge is acceptable. Check for EN chatter on the scope (test SCH-T4).
**I2C address map** [Schematic netlist v3]:

| Bus | Device | 7-bit address | Notes |
|---|---|---|---|
| MCU I2C1 | VEML7700 (ALS) | **0x10** | fixed address |
| MCU I2C1 | STUSB4500 (USB PD sink) | **0x28** | default (ADDR0/1 strap = 0); straps allow 0x28–0x2B |
| MCU I2C1 | MAX17055 (fuel gauge) | **0x36** | fixed; its model/NV registers also respond at **0x0B** (SBS address), so keep 0x0B free |
| MCU I2C1 | BQ25895 (charger) | **0x6A** | fixed |
| CM5 I2C1 | DRV2605L (haptics, DNP) | 0x5A | fixed; separate bus |

- **No conflicts** on MCU I2C1: 0x0B/0x10/0x28/0x36/0x6A are all distinct.
- Keep 0x0B reserved. Don't put an EEPROM in 0x50–0x57 without rechecking.
- The STUSB4500 address strap must be confirmed in the final netlist.
- The CM5's own on-module devices sit on internal buses, not on GPIO2/3, so there's no clash there [A-69: confirm against the CM5 datasheet; on the prototype IO board, also check the IO board's own devices on GPIO2/3 / i2c-1 with `i2cdetect -y 1`].

**Framing** (COBS-encoded, `0x00` delimiter):
```
| ver(1) | type(1) | seq(1) | len(1) | payload(len ≤ 64) | crc16-CCITT(2) |
```
Every command gets `ACK{seq,status}` within 50 ms. Otherwise the sender retries ×3, and after that the link is marked down.

| Type | Dir | Name | Payload |
|---|---|---|---|
| 0x01 | CM5→MCU | `HELLO` | proto_ver, cm5_fw_ver |
| 0x02 | MCU→CM5 | `HELLO_ACK` | mcu_fw_ver, boot_reason (button/rtc/usb/wdt/brownout), flags |
| 0x10 | CM5→MCU | `SET_STATE` | target state (S0..S5) |
| 0x11 | CM5→MCU | `HEARTBEAT` | uptime_s, cm5_state |
| 0x12 | CM5→MCU | `SET_WAKE` | epoch_s (UTC) of next RTC alarm; 0 = clear |
| 0x13 | CM5→MCU | `SET_TIME` / `GET_TIME` | epoch_s |
| 0x14 | CM5→MCU | `MIC_ENABLE` | `on` u8, `session_id` u16, `mode` u8 (hold / tap), `max_s` u16 [Schematic netlist v3.1]. **Accepted**: the MCU sets PA11 (`MIC_PWR_EN`) only under the §8.2 conditions, replies `ACK` or `NAK{muted, no_ptt, timeout, cm5_down}`, and reports rail changes with `EVT_MIC_RAIL` (0x2B: `on`, `reason`: request / release / timeout / mute / link_loss / wdt / power_down) |
| 0x15 | CM5→MCU | `LED` | pattern id (charging, notify, rec, error), brightness |
| 0x16 | CM5→MCU | `HAPTIC` | pattern id (no-op: LRA is DNP in MVP [PM v0.3]; reserved for later) |
| 0x17 | CM5→MCU | `SHUTDOWN_READY` | — (MCU starts power-cut timer after CM5 halts) |
| 0x18 | CM5→MCU | `BOOT_MODE` | normal / recovery (for next boot) |
| 0x19 | CM5→MCU | `WDT_CFG` | timeout_s (default 30) |
| 0x1A | CM5→MCU | `FW_UPDATE_BEGIN/CHUNK/END` | signed image chunks |
| 0x20 | MCU→CM5 | `EVT_BUTTON` | `id` u8 (0 POWER (PA0), 1 ACTION (PA1; **= PTT**), 2 VOL+ (PA4), 3 VOL− (PA5)), `action` u8 (down/up/short/long/double/repeat), `t_ms` u32 (MCU tick), `woke` u8 (1 if this press caused the CM5 power-on; the MCU latches the ACTION press so PTT survives the cold boot) [Schematic netlist v3] |
| 0x21 | MCU→CM5 | `EVT_BATTERY` | soc_%, mV, mA (signed), cell temp_dC, charging state; 1 Hz in S0 (power cap), else every 30 s or on change > 1 % |
| 0x22 | MCU→CM5 | `EVT_POWER_SRC` | usb_attached, charger status/fault |
| 0x23 | MCU→CM5 | `EVT_MIC_MUTE` | `muted` u8 (PA10 level, 1 = muted), `valid` u8 (CM5 power-good; [Schematic netlist v3.2]), `t_ms`. Sent on every debounced edge and in `HELLO_ACK` at boot [Schematic netlist v3] |
| 0x24 | MCU→CM5 | `EVT_RTC_ALARM` | epoch_s |
| 0x25 | MCU→CM5 | `EVT_SHUTDOWN_REQ` | reason (long-press, critical battery, thermal) and deadline_s |
| 0x26 | MCU→CM5 | `EVT_THERMAL` | v0.3.4 payload: `case_ntc_dC` (i16, raw case NTC at back plate (−55.3,−10), STM32U0 ADC), `cell_dC` (i16), `ambient_dC_est` (i16), `stage` (u8: 0 Normal / 1 Warn / 2 Soft / 3 Hard / 4 Protect, MCU's own view), `adc_fault` (u8 bit flags: open/short). 1 Hz in S0–S2. Hot-spot compensation (§10.4.2) is applied by pm-power and mirrored in the MCU with the calibrated `k_hs` |
| 0x29 | CM5→MCU | `SET_THERMAL_CAL` | `k_hs_mK_per_W` (u16), `tau_hs_s` (u16), `ntc_offset_dC` (i8), `lux_gain_q8` (u16, v0.3.5 window gain), `p_avg_mW` (u16, sent at 1 Hz so the MCU can enforce Protect independently). Stored in MCU flash, acknowledged with `ACK` |
| 0x2C | CM5→MCU | `SET_CHARGE_CFG` | [Tech Research 2026-10-21] `ntc_r25_ohm` u32, `ntc_beta` u16, `rt1_ohm`/`rt2_ohm` u32, thresholds (i16 dC ×5), `beta_measured` u8. Bounds-checked, written to config flash, `ACK`/`NAK{range}` |
| 0x2A | MCU→CM5 | `EVT_LIGHT` | v0.3.5 (opcode moved from 0x28 in v0.3.6 to fix a collision): `case` (u8: 0 held / 1 table / 2 pocket), `lux` (u16, saturating), `valid` (u8). Sent on a case change, plus a 1 Hz `lux` field appended to `EVT_THERMAL` |
| 0x27 | MCU→CM5 | `EVT_CHARGE_INHIBIT` | reason (cell < 10 °C / > 40 °C / charger fault), cell_dC |
| 0x28 | MCU→CM5 | `EVT_OVERCURRENT` | cell_mA, duration_ms (§10.5) |
| 0x1B | CM5→MCU | `HAPTIC_CFG` | driver present?, effect library id. Ignored, since there's no haptic driver in MVP (LRA DNP) |
| 0x1C | CM5→MCU | `SET_POWER_CAP` | cap_mW (default 9000), fast-window enable |
| 0x2F | MCU→CM5 | `EVT_FAULT` | code |

**Wake sources** (S3/S4 → on) [Schematic netlist v3]: POWER button (PA0/WKUP1), ACTION button (PA1/WKUP3, starts a PTT session), and *not* VOL± (their EXTI lines are masked in S4), RTC alarm (reminder), USB-C attach (configurable: boot to "charging" screen or stay off and show the charge LED), critical events.

**Watchdog**: two layers. (1) The BCM2712 hardware watchdog is fed by systemd (`RuntimeWatchdogSec=15`). (2) The MCU watchdog expects a `HEARTBEAT` every 5 s in S0–S2. If it misses for 30 s, the MCU toggles `RUN` to reset the CM5 (logged as `boot_reason=wdt`). After 3 WDT resets in 10 min, it requests `BOOT_MODE=recovery`. The MCU itself runs its own hardware WDT.

**RTC**: CM5 has an on-board RTC (needs VBAT backup cell or supercap). The MCU keeps time with the STM32U0 RTC on a 32.768 kHz LSE crystal [PM 2026-10-21] so RTC alarms work while CM5 rails are fully off. The CM5 syncs MCU time after NTP and pulls MCU time at boot before chrony sync.

---

## 12. Low-power MCU firmware outline: STM32U0 [PM 2026-10-21]

- **Target MCU: STM32U031K8U6** (UFQFPN-32 5×5 mm, Cortex-M0+ up to 56 MHz, **64 KB flash, 12 KB SRAM**) [Schematic netlist v3]. This is not the U083. **Prototype: NUCLEO-U031R8** (STM32U031R8T6, LQFP-64, same die and memory; ST board MB1932, user manual UM3256). Sources: ST product page https://www.st.com/en/microcontrollers-microprocessors/stm32u031k8.html, datasheet https://www.st.com/resource/en/datasheet/stm32u031k8.pdf, board https://www.st.com/en/evaluation-tools/nucleo-u031r8.html.
- **Part check (U031K8)**:
  - **Memory**: 64 KB flash / 12 KB SRAM confirmed.
  - **Peripherals**: 1× 12-bit ADC (HW oversampling to 16-bit), RTC (LSE), 2× LPTIM, IWDG, **3× I2C (I2C1 has an independent clock and wakes from Stop on address match)**, **4× USART + 2× LPUART**, Stop0/1/2, Standby, Shutdown.
  - **USART2 is present** (PA2 TX / PA3 RX, AF). The datasheet USART table marks USART1/USART2 as having the independent clock domain for Stop-mode wake. ST's generic text says USART/LPUART wake from "Stop mode", but I couldn't confirm from the text whether that includes **Stop2** for USART2 (LPUARTs are the documented Stop2-capable ports). The EXTI-on-RX design (§11) is kept [A-68]. Note: **LPUART1 is also on PA2/PA3** (alternate AF), so the same pins could fall back to LPUART1 with no board change.
  - **Pins on QFN-32**: PA0, PA1, PA2, PA3, PA4, PA5, PA10, PA12, PB0, PB6, PB7 are **all present** (STM32duino U031K(4-6-8)U pin map; datasheet pinout to be re-read at layout). PB0 = ADC1_IN17 ✓, PB6/PB7 = I2C1 SCL/SDA ✓.
  - **Nothing missing.** But the package has only ~25 I/O, so the pin budget is tight (below).
  - **WKUP**: PA0 = WKUP1 and PA1 = WKUP3 per netlist v3. Not independently re-confirmed: the ST datasheet PDF couldn't be fetched from the box. WKUP pins matter only for Standby/Shutdown; Stop2 wake uses EXTI on any pin [A-71: **resolved per netlist**, datasheet re-check at layout review].
- **Pin budget (QFN-32)**:
  - Used: PA0/1/4/5 buttons; PA2/3 USART2; PA10 mute; PA12 NTC bias; PB0 NTC ADC; PB6/7 I2C1; PA13/14 SWD; PC14/15 LSE.
  - **PA11 (pin 21) = `MIC_PWR_EN`** [Schematic netlist v3.1]. Still to assign from the remaining ~PA6–PA9, PA15, PB1, PB3–PB5: `MCU_IRQ_N`, `CM5_PWR_EN`, `RUN`, BQ25895 INT, MAX17055 ALRT, STUSB4500 ALERT (optional) and the status LED (1–2). That's 7–8 of ~9, with ≤ 1 spare [A-73].
- **Memory budget (64 KB / 12 KB)**:
  - Flash: bootloader 8 KB + **slot A 26 KB + slot B 26 KB** + config/calibration 2 KB (1 page) + log 2 KB = 64 KB. The application must fit **≤ 26 KB**, so use LL drivers (not HAL), no printf, and COBS/CRC in < 1 KB [EST, to be measured at M5].
  - If it doesn't fit: drop the B slot and recover through the ROM bootloader (USART, BOOT0 test pad) [A-74].
  - SRAM: stack 2 KB, UART RX/TX rings 1.5 KB, event log ring 2 KB, driver state + FSMs ~2 KB, ADC/thermal model 0.5 KB, link frame buffers 1 KB, so ≈ 9 KB with ~3 KB headroom.
  - `FW_UPDATE_*` streams 256 B chunks to flash (no full-image RAM buffer).
- **Toolchain**:
  - STM32CubeU0 HAL/LL with a thin `hal_*` layer of our own, so logic is host-testable.
  - Bare-metal event loop. Zephyr is optional later.
  - CMake + arm-none-eabi-gcc. Unity/CMock for host unit tests.
- **Peripheral use**:

| Function | STM32U0 peripheral | Low-power notes |
|---|---|---|
| CM5 link | **USART2** (115200) [Schematic netlist v3] | RX pin doubles as an EXTI wake line from Stop2 [A-68]; DMA RX into a ring buffer; TX Hi-Z while the CM5 is unpowered. `MCU_IRQ_N` is open-drain to CM5 GPIO4 |
| Buttons [Schematic netlist v3]: **PWR PA0 (WKUP1), ACTION/PTT PA1 (WKUP3), VOL+ PA4, VOL− PA5**, all **active low** (internal pull-ups, or external if fitted); mic-mute **PA10 (high = muted)**; USB-C attach | GPIO + **EXTI** falling edge (mute: both edges) | **Stop2 wake**: PA0 and PA1 EXTI always armed (the WKUP1/3 function is also enabled, so the same pins work should Standby ever be used). **VOL± EXTI is armed only while the CM5 is up** (S0–S2) and masked in S4, so pocket presses don't wake. PA10 EXTI is always armed, to keep the mute state and `MIC_PWR_EN` gating current. Debounce with **LPTIM1** (5 ms), no busy-waiting. Long/double-press timing on LPTIM |
| Long-press timing (2 s menu, 10 s hard cut), chord window 80 ms | **LPTIM1/LPTIM2** | runs in Stop2 on LSE |
| Time / alarms | **RTC** (LSE 32.768 kHz) + Alarm A (wake CM5) + Alarm B (periodic battery/thermal sample) + backup registers (boot reason, boot mode) | **The STM32U0 RTC replaces the external RTC option** [A-24 resolved] |
| Fuel gauge, charger, PD sink, ALS | **I2C1 PB6/PB7**: MAX17055 0x36, BQ25895 0x6A, STUSB4500 0x28, VEML7700 0x10 [Schematic netlist v3] | gauge ALRT and BQ25895 INT on EXTI; STUSB4500 ALERT on EXTI if routed; VEML7700 polled |
| Case NTC [Schematic netlist v3] | **ADC1_IN17 on PB0**; bias from **PA12** via 10 kΩ 1 %, high only while sampling | 1 Hz in S0–S2, every 60 s in S4. Cell temp via BQ25895 `TSPCT` over I2C (MAX17055 `Temp` as backup); no ambient NTC fitted |
| Mute sense; mic power [Schematic netlist v3.1] | **PA10** `MUTE_STATUS_IO` input, EXTI both edges. **PA11 (pin 21) `MIC_PWR_EN`** push-pull output → U14 TPS22917 EN (100 k external + internal pull-down) | PA11 is configured low before anything else at boot; reset state = analog/Hi-Z, held off by the pull-downs |
| Status LED patterns | **TIM** PWM (Run) / LPTIM PWM (Stop) | |
| Haptics (optional hook) | **CM5** I2C1 (GPIO2/3) → DRV2605L (DNP) [Schematic netlist v3]; the MCU has no haptics path in v1 **or** TIM PWM to a motor driver | **LRA is DNP on the PCB and not in the MVP UX [PM 2026-10-21, v0.3].** `haptics_drv_t` interface with a `null` driver by default. Haptics are TBD (LRA under evaluation) [PM 2026-10-21] |
| Watchdog | **IWDG** (LSI), refreshed in the main loop, keeps running in Stop2 | |
| Firmware storage | 64 KB flash: bootloader 8 KB + slot A/B 2 × 26 KB + config/cal 2 KB + log 2 KB [Schematic netlist v3] | A/B is optional if the app outgrows 26 KB [A-74] |

- **Low-power modes**:
  - **Run / LP-run** only while handling events.
  - Otherwise **Stop2**: SRAM retained, RTC/LPTIM/EXTI wake (including the USART2 RX pin EXTI). This applies in every state, including S0, between events.
  - Standby/Shutdown modes are not used, because they lose SRAM and the UART/EXTI wake path.
  - Stop2 entry happens when the event queue is empty and no UART frame is in progress.
- **Modules**:
  - `link`: COBS/CRC framing, seq/ack, retry, dispatch (§11).
  - `buttons`: debounce, short/long/very-long, chord (Vol+ and Vol− together within 80 ms), boot combos (recovery), **PTT latch while the CM5 is off**.
  - `power_fsm`: S0–S5 and ship mode (§10.1); CM5 5 V/`RUN` control; power-cut timer after `SHUTDOWN_READY`; **Power 10 s = hardware cut + charger ship mode**, independent of the CM5 (controls.md).
  - `battery`: gauge/charger drivers; thresholds 20/10/3 %; UVLO cut; reports `EVT_BATTERY`; feeds the **power cap fast path** (§10.5).
  - `charge_ctrl` (**JEITA, charging only within 10–40 °C**) [PM 2026-10-21]:
    - **Hardware layer**: cell NTC on the charger TS pin. The charger's JEITA profile is configured (BQ25895-class: TS divider) as an independent backstop at no charge below 0 °C or above 45 °C, with reduced current/voltage in the outer bands.
    - **Firmware layer (stricter, the product spec)**: the MCU reads cell temperature as **BQ25895 `TSPCT`** over I2C every 10 s while USB-C is attached (one-shot ADC conversion). It cross-checks against MAX17055 `Temp`; a disagreement > 10 K is treated as a sensor fault → charge disabled.
      - **Thresholds come from the `charge_cfg` record in config flash** [Tech Research 2026-10-21] (NTC R25, **β**, RT1/RT2, cold-off/on, hot-on/off, derate; CRC + bounds 0–45 °C; defaults below). Until `beta_measured`, the prototype evaluates both β 3435 and 3950 and takes the worse reading.
      - **Disable charging** (charger `CHG_CONFIG=0` over I2C) if the cell is **< 10 °C or > 40 °C** (defaults).
      - Re-enable at **≥ 12 °C and ≤ 38 °C** (2 K hysteresis).
      - Charge current is derated to 0.5C above 35 °C [A-47].
      - The power path keeps powering the system while charging is inhibited.
      - Sends `EVT_CHARGE_INHIBIT`. The UI shows "Too hot/cold to charge" on screen 15, and the LED pattern shows it when the CM5 is off.
    - **Fail-safe**: NTC open/short (TSPCT at a rail, or the BQ25895 `NTC_FAULT` bits set) → charging disabled. If the MCU stops responding, the charger watchdog (I2C watchdog timer) reverts the charger to its default *safe* limits, and the hardware JEITA layer still applies.
  - `thermal`: samples the skin, cell and ambient NTCs. Sends `EVT_THERMAL`. Blocks CM5 power-on while skin ≥ 43 °C after a T4 shutdown. Can hard-cut if skin > 55 °C and the CM5 doesn't respond [A-48].
  - `rtc_alarm`: time, the next wake (min of reminder and daily-summary pre-generation), drift trimming after NTP sync.
  - `privacy` [Schematic netlist v3.1]: owns PA10 (mute; **valid only with CM5 power-good, never read as "unmuted" otherwise** [Schematic netlist v3.2]) and PA11 (`MIC_PWR_EN`). Accepts `MIC_ENABLE` only for a CM5 request while ACTION is held, or for a confirmed tap-to-talk session, and only when unmuted. Enforces the max-session timeout (LPTIM, ≤ 120 s / 600 s dictation). Forces PA11 low on release/off/mute/timeout/link loss (> 2 s)/heartbeat loss/CM5 power-down or `RUN` reset. Emits `EVT_MIC_RAIL` and `EVT_MIC_MUTE`. This module is tiny and reviewed separately.
  - `wdt_supervisor`: CM5 heartbeat; reset on a miss of more than 30 s; recovery after 3 resets.
  - `bootloader`: verifies an ed25519 signature on the slot image, A/B with rollback. Updated through `FW_UPDATE_*` from pm-power. The ROM system bootloader (BOOT0 + USART) is the last-resort recovery path through a test pad.
  - `log`: an event ring buffer in SRAM plus backup registers for the boot reason.
- **Current targets**: S4 MCU average ≤ 5 µA (Stop2 + RTC + LPTIM ≈ 1–2 µA typical [A-44], plus periodic ADC). The whole S4 system is ≤ 1 mA at the cell (§10.3). The Nucleo board's ST-LINK and LEDs must be cut off (IDD jumper measurement) for meaningful numbers.
- **Safety invariants** (host unit tests plus HIL):
  - PA11 is never high without an accepted `MIC_ENABLE` session, or after its timeout, a link loss, or CM5 power-down; it's low after any reset (the green LED / mic-power coupling is guaranteed by wiring);
  - no charging outside 10–40 °C;
  - power is never cut while the CM5 runs, unless Power 10 s / UVLO / skin > 55 °C;
  - critical battery always leads to S5 → S4;
  - a watchdog reset never loses the RTC.

---

## 13. Logging, telemetry, and diagnostics
- journald with no user content. A structured `pm.log` JSON with event codes.
- No remote telemetry in MVP. A "Diagnostics bundle" export (logs, versions, MCU log, no user content) is user-initiated.
- Crash dumps: `systemd-coredump` limited to engine binaries, stored on the data partition, deleted after 7 days.

## 14. Performance targets [PM 2026-10-21; earlier values were A-28 and are now superseded]

Latency targets apply **from S0–S2 (device awake or in the warm window)**. From S4, only the < 100 ms feedback target applies, and the cold-boot targets cover the rest.

| # | Metric | Target | How it's met | Feasibility |
|---|---|---|---|---|
| L1 | Button press → feedback (LED / haptic-or-visual) | **< 100 ms** | MCU LED/haptic on the EXTI edge (< 10 ms, works even when the CM5 is off); UI listening overlay < 100 ms in S0–S1, < 150 ms from S2 (panel power-up) | ✅ (UI from S2: panel wake time to verify. The MCU LED satisfies the criterion) |
| L2 | End of speech → local action result (note saved, reminder card, timer) | **≤ 750 ms** | VAD endpoint 250–300 ms; streaming ASR leaves only the last chunk; fast-path intent/date grammar ≤ 50 ms; DB write ≤ 20 ms; UI ≤ 50 ms | ⚠ tight. Feasible for ≤ 5 s commands *only* with chunked streaming ASR at small/base size. **Infeasible with a medium-size IndicWhisper** or if the LLM is in the path. 2 GB SKU: Vosk result only |
| L3 | End of speech → progress cue (processing indicator or spoken filler) | **< 1.85 s, always** | the processing screen (03) is shown at endpoint, ≤ 300 ms; tone/filler if no result by 1.5 s | ✅ |
| L4 | Cloud answer | **≤ 4 s** from send to first result, otherwise cancel + local fallback + notice (20b) | timeout in pm-core; streaming providers | ✅ (enforced as a cap; the answer quality cost is accepted) |
| L5 | Local Q&A: question → first useful output | search hits with source chips ≤ 500 ms after the final transcript; first LLM token ≤ 1.5 s (250-token prompt) | §6.3 mitigations | ⚠ the 1.5 s TTFT depends on prefill speed (unmeasured). A full generated answer will take 3–8 s on a 1B model, so the progress cue covers it |
| L6 | OCR: shutter → text | ≤ 3 s doc, ≤ 4 s scene | | ⚠ IndicPhotoOCR on CPU unmeasured |
| L7 | Camera translation: shutter → first translated line | ≤ 2.5 s (≤ 30 words) | §9.2 | ⚠ IndicTrans2-dist on CM5 unmeasured |
| L8 | Search: query → results (50k chunks, cross-script) | ≤ 100 ms; tap → source opens ≤ 300 ms | FTS5 + xlit expansion ≤ 30 ms | ✅ |
| L9 | Cold boot S4 → listening (PTT latched) | < 10 s target, < 15 s hard | §10.1 | ⚠ < 10 s needs Yocto-level boot tuning |
| L10 | S2 → S0 wake | < 300 ms | | ✅ |
| T1 | CM5 SoC sustained | **< 65 °C** | skin governor T1 at 65 °C | ✅ at 25 °C; at 35–45 °C it's met by throttling (slower) |
| T2 | Skin | ≤ 43 °C sustained at 35 °C ambient; ≤ Ta+3 (48 °C) sustained at 45 °C; ≤ 48 °C peak | §10.4 | ⚠ at 45 °C ambient the sustained budget is ~0.6–0.8 W, so the device is only usable for short sessions |
| B1 | Battery | 16 h mixed use + ≥ 24 h standby (MCU holds, CM5 fully off) | §10.3 | ✅ 16 h light profile (~45 % margin) on 3.6 Ah. ⚠ heavy profile borderline at ~16 h. ✅ standby |

### 14.1 Feasibility flags (summary)
1. **IndicWhisper (medium) on CM5** is likely too slow for interactive use, so a small/base-size Hindi/Hinglish fine-tune is required. Hinglish WER on small models is unproven (§6.10 gate).
2. **≤ 750 ms local actions** require streaming ASR plus a non-LLM fast path. LLM-based parsing can't meet it.
3. **LLM prefill** on CM5 makes RAG answers with long context slow, so context is capped at ~250 tokens and sources are shown first.
4. **IndicPhotoOCR and IndicTrans2-dist** have no CM5 CPU latency data, and ARM packaging (IndicProcessor, SentencePiece, torch→ONNX/CT2) is a risk.
5. **16 h mixed use on 3.6 Ah** (v0.3.4): met for the light profile with margin. Heavy use is borderline at ~16 h, and thermally duty-limited at ≥ 35 °C.
6. **At 45 °C ambient**, sustained skin limits allow < 1 W, so local LLM use is effectively blocked and cloud is offered per request.
7. **Cold boot < 10 s from S4** is needed, because CM5 has no usable suspend.
8. **2 GB SKU** (deferred, not v1): Hindi/Hinglish ASR quality would likely miss the WER bars without cloud help.
9. **Measured CM5 idle 2.4–2.65 W > ~1.6–1.75 W passive budget** (v0.3.2): the device can't idle with the CM5 on. 16 h and the thermal limits hold only with CM5-off-by-default, a 30 s post-session hold and duty-cycled sessions (§10.3, §10.3b). Cold boot per session becomes the main latency cost, and §10.7 decides whether s2idle helps.

## 15. Repo layout and dev workflow
```
PocketMate/
  software/
    ARCHITECTURE.md
    os/         pi-gen stage + (later) yocto layer meta-pocketmate, rauc config, dts overlays
    ui/         Qt6/QML app (CMake)
    services/   python package `pocketmate` (core, audio, asr, llm, ocr, tts, memory, remind, power, cloud)
      pocketmate/engines/  protocols.py, backends/*
    mcu/        STM32U0 firmware (CMake, STM32CubeU0), host-side tests
    tools/      benchmarks, protocol fuzzer, flashing scripts
    tests/      pytest (unit), integration (on-device, HIL with MCU)
```
CI: lint (ruff, mypy --strict for protocols), unit tests, cross-builds (aarch64) of llama.cpp/whisper.cpp, MCU firmware build + host unit tests, image build nightly. Git flow per PRD: issue → branch → PR → merge as anand2532.

---

# Part B — Prototype plan (off-the-shelf CM5 IO Board)

## B1. Goals
Validate on existing hardware before the custom PCB [PRD strategy]: capture/search/OCR/reminders working end-to-end; measure performance, privacy behavior, battery life, and thermals; freeze the MCU protocol and power behavior; derive the custom carrier requirements.

## B2. BOM (prototype, ~1–2 units) [prices are rough estimates, A-29]

| # | Item | Purpose | Qty | Est. USD |
|---|---|---|---|---|
| 1 | Raspberry Pi CM5 4 GB/32 GB eMMC/wireless (CM5104032) **+ 1× CM5 2 GB/32 GB (CM5102032)** for the SKU benchmark | compute [PRD], SKUs [PM 2026-10-21] | 1+1 | 90 + 65 |
| 2 | Raspberry Pi CM5 IO Board | carrier | 1–2 | 25 |
| 3 | CM5 active cooler (official) + a passive heatsink/pad set (for the passive mock-enclosure test) | thermals | 1 | 15 |
| 4 | Antenna kit for CM5 | Wi-Fi/BT | 1 | 5 |
| 5 | **4.3" DSI capacitive 800×480 IPS** (e.g., Waveshare 4.3" DSI LCD) [PM 2026-10-21] | UI | 1 | 40 |
| 6 | Raspberry Pi Camera Module 3 (IMX708 AF) + 22-pin CM FFC | OCR/translation | 1 | 25 |
| 7 | 2× I2S MEMS mic breakout (ICS-43434 / SPH0645 / INMP441) | 2 mics [PRD] | 2 | 10 |
| 8 | MAX98357A I2S amp + 8 Ω 1–2 W speaker | audio out | 1 | 10 |
| 9 | **ST NUCLEO-U031R8** (STM32U031K8, on-board ST-LINK) [PM 2026-10-21] | low-power MCU (replaces the RP2040 Pico) | 2 | 2 × 12 |
| 10 | Charger/power path: **BQ25895 eval/breakout** (TS/JEITA, I2C, ship mode, power path) [Research] + 5 V ≥ 3 A boost (e.g., TPS61088-class module) + load switch for the CM5 5 V rail | power path | 1 | 30 |
| 11 | Fuel gauge breakout (MAX17055 or MAX17048) | battery monitoring | 1 | 10 |
| 12 | **Akyga LP655063 (prototype), 3000 mAh, 1C (3 A max), pack ≤ 65.5 × 51 × 7.0 mm, protected, 10k NTC (yellow wire, β unstated)**, plus a **1.5 mm foam spacer** for the 9.0 mm pocket [Tech Research 2026-10-21, v0.3.11]. Production: custom cell per `research/battery-rfq.md` Rev C (≥ 3000 mAh / 3100 mAh target, ≥ 2C, 3C/10 s, ≤ 8.5 × 50.5 × 62 mm, 10k B3435 ±1 %) | battery | 2 | 2 × 12 |
| 13 | 10k NTC thermistors (2–3: case/skin, ambient, spare) + thermal epoxy/Kapton | skin governor | 5 | 3 |
| 14 | INA226 breakout (5 V rail) + USB-C power meter | power budget | 1 | 12 |
| 15 | ~~LRA + DRV2605L~~: dropped, LRA is DNP in MVP [v0.3]. Keep 1 for firmware hook bring-up only | (optional) | 0–1 | 0–10 |
| 16 | Tactile buttons (large detented Action, Power, Vol±), mic-mute slide switch, DPDT slide switch (SW5 equivalent), red mute LED, status LED, **TPS22917 breakout (or equivalent) + green 0603 LED (product: Kingbright APTD1608LZGCK) + 1.3 kΩ + 100 kΩ** [Schematic netlist v3.1], resistors, MOSFETs | controls/privacy | kit | 10 |
| 17 | USB-C PD 5 V 5 A supply (official 27 W), wiring, standoffs, 3D-printed 125×75×20 mock enclosure | bench + thermal test | kit | 30 |
| 18 | Logic analyzer (8 ch), K-type thermocouples + logger (skin map), access to a 45 °C chamber (or a heated box with a controller) | test | 1 | 60 |
| | **Total (approx.)** | | | **~$520–580** (incl. 2 GB module and test gear) |

## B3. Wiring (prototype)

The NUCLEO-U031R8 pins below are **proposed** and must be checked against the NUCLEO-U031R8 user manual and the STM32U031K8 AF table before wiring. **PA5 goes to LD2** [A-31].

**Prototype vs. product differences** [Schematic netlist v3]:
1. **USART2 pins**: on the Nucleo, USART2 PA2/PA3 are wired to the ST-LINK VCP. Either:
   - **(a) preferred**: open the VCP solder bridges (per the UM) and wire PA2/PA3 to the CM5, keeping the product firmware pin map; or
   - **(b)** keep the VCP for logs and use another USART2 AF pin pair, if the AF table offers one, or LPUART1 behind a `BOARD_NUCLEO` build define.
   - With (a), debug logs move to LPUART1 on spare pins with a USB-UART dongle.
2. **I2C1**: the product uses PB6/PB7. On the Nucleo, PB6/PB7 are reachable on the morpho headers, so wire the same pins. The v0.3.5 table used PB8/PB9 (Arduino D15/D14); that's now dropped. Check for solder bridges or shields sharing PB6/PB7.
3. **Breakouts**: the BQ25895, MAX17055, STUSB4500 and VEML7700 are separate breakout boards on the Nucleo 3V3 (the Nucleo 3V3 stands in for the always-on rail). Each breakout usually has its own pull-ups, so keep one set (about 2.2–4.7 k total).
4. **CM5 side**: on the CM5 IO Board, GPIO14/15/4/2/3 are on the 40-pin header. Disable the serial console on UART0 (`enable_uart=0`; remove `console=serial0,115200` from cmdline.txt). Run `i2cdetect -y 1` to see which IO-board devices, if any, also sit on GPIO2/3 [A-69].

| From | To | Notes |
|---|---|---|
| CM5 GPIO18/19/20/21 (I2S BCLK/LRCLK/DIN/DOUT) | Mic1/Mic2 SCK/WS/SD, MAX98357A BCLK/LRC/DIN | Mic1 L/R → GND, Mic2 L/R → 3V3. Amp SD → CM5 GPIO16 |
| CM5 GPIO14 (UART0 TXD, IO Board 40-pin header pin 8) | Nucleo **USART2 RX** (see note) | 3.3 V logic both sides [Schematic netlist v3] |
| CM5 GPIO15 (UART0 RXD, header pin 10) | Nucleo **USART2 TX** (see note) | |
| CM5 GPIO4 (header pin 7, in, pull-up) | Nucleo GPIO `MCU_IRQ_N` (open-drain out) | active low; IRQ + s2idle wake |
| CM5 GPIO17 (in, header pin 11) | mute switch `MIC_MUTE` (high = muted), also to Nucleo **PA10** (EXTI, Arduino D2) [Schematic netlist v3] | GPIO17 is used for nothing else (the old gpio-shutdown/IRQ use moved; IRQ is GPIO4) |
| DPDT switch (SW5 stand-in) [Schematic netlist v3.2] | pole 1: IO-board 3V3 (as +3V3_PERIPH) → unmuted throw = MIC_SW_LIVE / muted throw = red LED D1 + resistor; MIC_SW_LIVE → small NPN/N-FET inverter (Q6 stand-in, pull-up to 3V3) → CM5 GPIO17 + Nucleo PA10 | matches netlist v3.2 |
| Nucleo **PA11** (morpho) `MIC_PWR_EN` [Schematic netlist v3.2] | EN of a **TPS22917 breakout** (or equivalent with output discharge) + 100 kΩ to GND; **IN = MIC_SW_LIVE** (after the DPDT); OUT = MIC_FEED → mic VDD **and** green LED + 1.3 kΩ | U14 is now *after* SW5 |
| Nucleo GPIO `CM5_PWR_EN` (via load switch / boost EN) | CM5 IO Board 5 V input (USB-C power-in path) | S4 = CM5 unpowered [A-31: confirm IO Board 5 V input] |
| Nucleo GPIO (open-drain via MOSFET) | IO Board `RUN` / power-button header | reset/wake |
| Nucleo I2C1 **PB6 SCL / PB7 SDA** (morpho CN10; same pins as the product [Schematic netlist v3]) | BQ25895 (0x6A), MAX17055 (0x36), STUSB4500 (0x28), VEML7700 (0x10), on breakouts | MCU owns the battery/sensor bus; one set of pull-ups only (remove the extra breakout pull-ups) |
| CM5 GPIO2/3 (I2C1, header pins 3/5) | DRV2605L breakout (optional, DNP in product) | haptics hook bring-up only |
| Nucleo PA0 (WKUP1, Arduino A0) | Power button to GND | active low, pull-up [Schematic netlist v3] |
| Nucleo PA1 (WKUP3, Arduino A1) | Action/PTT button to GND | active low, pull-up. The on-board B1 (PC13) can stand in only with a `BOARD_NUCLEO` remap |
| Nucleo PA4 (Arduino A2) | Vol+ to GND | active low, pull-up; EXTI only while awake |
| Nucleo PA5 (Arduino D13) | Vol− to GND | **⚠ PA5 drives LD2 on the Nucleo**: the LED + resistor to GND fights the pull-up. Open the LD2 solder bridge (per the UM), or the button reads unreliably |
| Nucleo **PB0** (ADC1_IN17, morpho) + **PA12** (bias, morpho) [Schematic netlist v3] | case NTC: PA12 → 10 kΩ 1 % → PB0 → NTC → GND. Cell NTC → BQ25895 breakout TS pin (with its RT1/RT2 divider), read via `TSPCT` | same pins as product. Check that PA12 isn't tied to anything on the MB1932 (it's a USB pin on some STM32s; U031 has no USB) |
| BQ25895 INT / gauge ALRT | Nucleo EXTI | |
| Nucleo 3V3 | from an always-on 3.3 V LDO off VSYS (battery) | remove the ST-LINK power jumper for current measurements (use IDD) |
| INA226 | in series with the CM5 5 V rail, read by the CM5 over I2C (dev only) | power budget |
| CAM1 / DSI1 FFC | Camera Module 3 / 4.3" DSI panel | |
| GND | common star ground at the charger | |

## B4. Milestones

| M | Duration [A-32] | Deliverables | Exit criteria |
|---|---|---|---|
| **M0 Bring-up** | 1 wk | pi-gen image, overlays, display/touch/camera/I2S mic/amp working, Qt EGLFS hello | All peripherals enumerate; `arecord`/`aplay` stereo OK; camera AF still capture |
| **M1 Skeleton** | 2 wk | D-Bus services skeleton, pm-ui shell screens, pm-memory schema + migrations, typed notes, FTS search | Create/search/edit/delete notes; unit tests ≥ 80 % for memory |
| **M2 Voice** | 2 wk | pm-audio PTT, Hinglish/Indic whisper.cpp + Vosk partials (EN/HI), Piper EN/HI, indicators, voice notes, fast-path intents | Voice note end-to-end; PM-L1/L2/L3 measured |
| **M2b ASR/OCR/translation benchmark gate** | 1.5 wk (parallel with M2–M4) | §6.10 benchmark on CM5 4G + 2G, EN/HI/Hinglish sets, report | model choice per SKU recorded; ⚠ flags resolved or escalated |
| **M3 Assistant + RAG** | 2 wk | llama.cpp service, model benchmark (≥ 3 models), hybrid retrieval, source chips, action-item extraction | Answers cite sources; latency targets §14 measured |
| **M4 OCR + Translation + Vision** | 2.5 wk | Scan flow, PaddleOCR/IndicPhotoOCR, pm-translate (IndicTrans2-dist), overlay, pm-xlit keyboard + cross-script FTS, local VLM trial | PM-X1, PM-K1, PM-S1 pass |
| **M5b Power reality + suspend decision (v0.3.2–v0.3.4)** | 2 wk (start right after M0; finishes before M5) | **Calibration on hardware (v0.3.4)**: (1) NTC: 2-point bath/chamber check of the case NTC and the cell NTC through the STM32U0 ADC (±0.3 K), store the offset; (2) hot-spot: v4_22 body with thermocouples at the SoC zone, the grip and the NTC site, run 1/2/3/5 W steps at 35 °C held/table/pocket, fit `k_hs` (initial 0.3 K/W) and `τ_hs`, write them with `SET_THERMAL_CAL`; (3) budgets: confirm 1.85/1.08/0.64 W at 35 °C and measure 45 °C (expected lower than the model); (4) trip timing: verify the 3 W/5 W soft/limit times against the §10.3b table (±20 %); (5) stage check: Warn/Soft/Hard/Protect and 1.5 K hysteresis observed; (6) case heuristic: validate display-off ⇒ pocket conservatism; (7) JEITA: charging inhibits at 45 °C, UI message shown; **(8) cell NTC β [Tech Research 2026-10-21]**: measure the LP655063 yellow-wire NTC at 25 °C and 50 °C (and 0 °C if possible) in a water bath or the chamber, against a reference thermometer. Compute β (B25/50), write it with `SET_CHARGE_CFG` (`beta_measured` = 1), recompute RT1/RT2 if β ≠ 3435 ±2 %, and re-verify the charger's hardware cold/hot trip points (beta-model expectation with RT1 5.21 kΩ / RT2 29.87 kΩ: **≈ 1.1–44.6 °C for B3435, ≈ 4.0–41.9 °C for B3950**, per `../research/components.md` (~L424–442)). **If B3950 (or β ≠ 3435 ±2 %): recompute RT1/RT2 with TI Eq. 2 using RTH(0 °C) ≈ 33.6 kΩ and RTH(45 °C) ≈ 4.35 kΩ** (or the measured R-T values), refit the prototype carrier/breakout, and re-verify the trip points **Run the §10.8 idle-power workplan (ranked levers, cumulative + attribution)**; measure our own CM5 4 GB idle, tuned idle (§10.6 levers one by one), burst, boot energy, S4. Run the §10.7 s2idle/deep/halt/rail-cut test matrix. Fit the thermal duty-cycle model on the mock unibody | PM-P1 + PM-P2 pass; §10.8 targets (S2 ≤ 1.6 W, S0 ≤ 2.0 W) met or gap reported; thickness recommendation (§10.3c) handed to mechanical; S3 adopt/reject recorded per the §10.7 rule; §10.3 table updated with measured values |
| **M5 Reminders + Power + MCU** | 2.5 wk | pm-remind + daily summary, pm-power + skin governor + 9 W cap, STM32U0 (NUCLEO-U031R8) firmware v0 (USART2 link, buttons, battery, JEITA charge_ctrl, NTCs, RTC alarm, IWDG, mic interlock, Stop2), S0–S5 + ship mode | PM-D1, PM-B2, PWR1, JE1–JE2 pass; reminder fires from S4 |
| **M6 Cloud adapter + privacy hardening** | 1.5 wk | pm-cloud, consent dialog/token, nftables egress, LUKS data, audit log, export/import | Privacy test suite passes; zero egress in local mode (pcap) |
| **M7 Updates + recovery** | 1.5 wk | RAUC A/B, signed bundles, health check, recovery partition, MCU FW update | Pull-power-during-update test passes 20/20 |
| **M8 Validation** | 2.5 wk | 25/35/45 °C chamber thermal tests, governor RC-model fit, 16 h battery runs, 1-week dogfooding, custom PCB requirements doc | Report + go/no-go for custom carrier |

## B5. Test and acceptance criteria

**Functional**
- F1: Voice note: PTT → transcript saved and searchable within 5 s of release (10 s utterance). WER ≤ 12 % EN / 20 % HI / 25 % Hinglish on quiet-room sets [A-33].
- F2: Q&A over memory returns at least one correct source chip for ≥ 80 % of a 50-question gold set. Tapping the chip opens the exact span.
- F3: OCR of a printed A4 page (EN and HI): CER ≤ 5 % at good lighting. Hindi scene photos: word accuracy ≥ 80 %.
- F4: Reminders fire within ±60 s of due time from S0, S2, and S4 (RTC wake). Missed reminders are shown after off-periods.
- F5: Export → factory reset → import restores all items, tags, reminders, and the consent log (hash chain verifies).
- F6: All features in §0 work with Wi-Fi disabled.

**Privacy (must pass, release-blocking)**
- PR1: Capture is impossible without a PTT event (fuzz pm-audio D-Bus API, attempt direct ALSA open from other service UIDs → EACCES).
- PR2 [Schematic netlist v3.2]: **Green D6 exactly tracks MIC_FEED > 0.1 V.** Logic analyser on MIC_FEED vs LED current (or a photodiode), over 1,000 PTT cycles plus mute toggles: zero samples where the rail is > 0.1 V and green is off, **and zero samples where green is on and the rail is < 0.1 V** (no over-indication, including while muted with PA11 forced high).
- PR2d [Schematic netlist v3.2]: **Red D1 is lit whenever muted with the CM5 up**, independent of PA11 (PA11 forced high and low): 100 toggles. With the CM5 off: D1, D6 and MIC_FEED are all off, and the MCU reports `EVT_MIC_MUTE{valid=0}` and refuses `MIC_ENABLE`.
- PR2a: **PA11 low at reset/brown-out.** Pulse NRST, sweep VDD through the BOR threshold, and power-cycle with a blank MCU: MIC_FEED stays < 0.1 V throughout (scope, 100 runs).
- PR2b: **No mic power without a PTT request.** With ACTION idle, inject `MIC_ENABLE{on}` without a hold or confirmed tap session, while muted, and fuzz the link: always NAK, and MIC_FEED < 0.1 V. ACTION held without a CM5 request also leaves the rail off.
- PR2c: **The timeout forces off.** Hold ACTION with `max_s` = 120 (and a request of 900 s): the rail drops at ≤ 120 s / ≤ 600 s dictation ± 1 s. Kill the UART, stop the heartbeat, and pull `RUN`/CM5 power: the rail drops within 2 s / immediately, and `EVT_MIC_RAIL` gives the reason.
- PR3 [Schematic netlist v3]: With the mute switch on (GPIO17/PA10 high), the PTT session refuses and the UI shows "Mic off (hardware)".
- PR3a: **No audio frames while muted.**
  - With the switch muted, press PTT 100× and inject `StartCapture` via D-Bus. The pm-audio frame counter stays at 0, and the ALSA capture device is never opened (`/proc/asound/card*/pcm*c/sub0/status` = closed). **Hardware check of SW5**: MIC_SW_LIVE and mic VDD < 0.1 V even with PA11 forced high, and the red D1 is lit (data-line grounding checked only if pole 2 still does it, A-77). Force-open ALSA as root on a test build: every sample = 0.
  - Mid-session mute: capture closes within 20 ms, and no frames after the edge reach ASR (frame timestamps checked).
  - `EVT_MIC_MUTE` arrives within 50 ms of each switch edge.
- PR3b: Fault injection: hold GPIO17 high but PA10 low (and the reverse) on a test jig. Capture is refused in both cases (muted wins).
- PR3c: With the CM5 off (S4), +3V3_PERIPH < 0.1 V at the mic VDD pins. An S4 → S0 → S4 cycle shows the rail (U12 output) up only while CM5_3V3 is up.
- PR3d [Schematic netlist v3.1]: `MIC_ENABLE{on}` while muted → NAK `muted`, and the mic VDD after SW5 stays off.
- SCH-T4 [Schematic netlist v3]: +3V3_PERIPH sequencing. Scope CM5_3V3, U12 EN and +3V3_PERIPH across 50 power cycles: the rail rises after CM5_3V3 and falls with it; no EN chatter; no rail while the CM5 is off.
- SCH-T5: Case NTC on PB0: PA12 is high only during sampling (scope: pulse ≤ 1 ms per sample). S4 MCU current with sampling ≤ 5 µA average.
- BAT-T1 [PM 2026-10-21, v0.3.8]: with the LP655063 at 3.4 V (bench supply via the cell input), a 9 W load gives cell current ≤ 2.7 A. Below 3.3 V, the cap scales and current stays ≤ 2.85 A. Measured Profile A/B runtime is recorded for both cells against the §10.2 table.
- PR4: In Local mode, zero packets leave the device from any pm-* UID except update checks (when enabled) over a 24 h pcap.
- PR5: Cloud requests without a valid token are rejected. Tokens can't be reused, the payload hash mismatch test passes, and every send has a `consent_log` row.
- PR6: Delete → item absent from FTS, vec, media, and page-level DB scan (`secure_delete`).
- PR7: No user content in journald (grep a test corpus of canary strings).

**Power / reliability**
- PW1: Measured power per state (S0 interactive, S0 AI burst, S2, S4, cold boot) vs the §10.3 table. Profile A/B runtime on the 3.6 Ah cell (see PM-B1).
- PW2: 500 S2↔S0 cycles and 200 S4→boot cycles without failure. Boot < 15 s.
- PW3: Battery at 3 % → controlled shutdown completes, no DB corruption (`PRAGMA integrity_check` ok) over 50 runs.
- PW4: Kill pm-core / hang the CM5 → the MCU WDT resets within 35 s, boot_reason=wdt logged.
- PW5: Update power-pull test (random power cuts during install) leaves a bootable slot 20/20.

**Performance / thermal**
- PT1: §14 targets met or documented with a gap analysis.
- PT2: superseded by TH1–TH5 below. Report both the active-cooler and the passive mock-enclosure results to guide enclosure design.

**PM acceptance criteria [PM 2026-10-21]**. Each is measured on the prototype in the 125×75×20 mock enclosure, ≥ 30 trials unless stated, and reported as P95.

- PM-L1: Button press → LED/visual feedback **< 100 ms** (no haptics in MVP, v0.3) (P99), in S0, S2 *and* S4. Logic analyzer from button edge to LED. The UI overlay is measured with a high-speed camera in S0–S2.
- PM-L2: Local actions (voice note saved, reminder card shown, timer set), end of speech → result **≤ 750 ms** P95 for ≤ 5 s utterances, EN/HI/Hinglish, on the 4 GB SKU. End of speech is taken from the audio waveform.
- PM-L3: **No request goes ≥ 1.85 s without a visible/audible progress cue**. 100 % of 200 mixed requests, including cloud and OCR.
- PM-L4: Cloud answers: first result **≤ 4 s**, or cancel + local fallback + notice. 100 % of trials with a network emulator at 200 ms RTT / 1 Mbps / 2 % loss.
- PM-B1 (backs the "all-day typical use" claim, v0.3): **16 h mixed use** on Profile A (§10.3), scripted on the robot rig or by a human tester, from 100 % at 25 °C, with ≥ 5 % remaining. Profile B runtime is reported. Pass/fail is recorded against the ⚠ in §10.3.
- PM-B2: **≥ 24 h standby** with the CM5 fully off (S4, MCU holding), with ≤ 3 % SoC drop. A reminder fires via RTC wake within ±60 s during the standby run.
- PM-T1: CM5 SoC **< 65 °C sustained** (10-min moving average) during Profile A at 25 °C ambient, with no firmware throttling events (`vcgencmd get_throttled` = 0).
- PM-S1: **Every search result opens its source**:
  - a note at the matched span;
  - a transcript at the **audio timestamp** (playback starts within ±0.5 s of the hit, if audio was kept; otherwise the transcript segment is highlighted);
  - an OCR doc/photo with the **bbox highlighted**.
  - Scored on a 100-query EN/HI/cross-script gold set: 100 % of results open their source, and recall@10 ≥ 90 %.
- PM-D1: Daily summary: produced locally at the set time from S0 and from S4 (RTC wake). Every highlight has ≥ 1 valid source link. Task and reminder lists match SQL exactly. A pcap shows zero egress. A deleted source item disappears from the summary.
- PM-X1 (camera translation, MVP #4):
  - 100 photos (60 Hindi signs/menus, 40 printed Hindi docs; Devanagari only, v0.3): first translated line **≤ 2.5 s** P95 (≤ 30 words); chrF++ ≥ 50 hi→en.
  - The overlay aligns with source lines (IoU ≥ 0.5 for ≥ 90 % of lines).
  - "Read translation" TTS works in EN and HI.
  - Works in airplane mode.
  - Saved translations are searchable in both languages.
- PM-X2: Translation with low OCR confidence offers cloud **only** through the consent dialog. No egress without a token (pcap).
- PM-K1 (transliteration): IndicXlit top-4 suggestion accuracy ≥ 90 % on the Hinglish typing set. Suggestions appear ≤ 50 ms after a keystroke (P95). A Roman query finds the Devanagari note (cross-script recall@10 ≥ 90 %).
- PM-C1 (cloud deletion):
  - For a provider with a deletion API: delete → `verify_deleted` confirms. `consent_log` has requested + confirmed rows. Offline deletes retry until they succeed and are still logged.
  - For a provider without one: the consent dialog shows the warning before the send.

**Power reality (v0.3.2)**:
- PM-P1: Measured CM5 4 GB power on our prototype is recorded:
  - untuned idle (compare with the sourced 2.4–2.65 W);
  - tuned idle with each §10.6 lever (rfkill, freq cap, cores offline, peripherals off, backlight off);
  - S0 interactive, AI burst, E_boot (J), t_boot, S4 at the cell.
  - Pass: tuned S0 interactive ≤ 2.6 W and E_boot ≤ 60 J. Otherwise re-run the §10.3 budget and escalate the 16 h claim.
- PM-P2: s2idle/deep/halt/rail-cut matrix (§10.7, S-1…S-8) completed, with the decision recorded against the rule (P_sleep, resume ≤ 1 s, 100/100 cycles).
- PM-P3: Duty-cycle validation at 35 °C:
  - 25 Profile-A sessions/h compressed into 2 h: skin ≤ 43 °C;
  - a single continuous 20 min session: Soft throttle allowed, no Protect stage;
  - the CM5 is off within 30 s of every session end (MCU log).
- PM/Enc-T1 [PM/Enclosure 2026-10-21]: v4_22 in a chamber at 35 °C and 40 °C (held, table, pocket fixtures): skin at the hottest point (thermocouple) never exceeds 43.0 °C. At 45 °C: never exceeds 48.0 °C. Each stage triggers within ±0.3 K of its threshold (after calibration). Release after 1.5 K hysteresis.
- PM/Enc-T2: The SoC is forced to 80 °C (heat gun or stress at Hard disabled in a test build), and Protect powers off to S4 within 5 s. The MCU blocks power-on until the NTC drops below Warn − 1.5 K.
- PM/Enc-T3: The case NTC is disconnected (open) or shorted. The MCU flags `adc_fault`, and pm-power falls back to SoC temperature − 25 K with the Warn stage forced and local AI disabled.
- PM/Enc-T4: Charging at 45 °C ambient → no charge current (charger JEITA), the UI shows "Too hot to charge", and charging resumes below 38 °C.
- PM/Enc-T6 (VEML7700): the sensor is detected at 0x10 on MCU I2C1 (PB6/PB7, via flex J11 9/10).
  - Lux, after window gain calibration, is within ±20 % of a reference lux meter at 10/100/1000 lx.
  - In a jeans pocket and in a bag, with the display off, pocket is classed within 10 s.
  - A dark room with active touch input stays held.
  - On a nightstand between 21:00 and 07:00 with the display off, it's classed as table unless the heat-rise check trips.
  - In a lux sweep, hysteresis shows no flapping.
  - Auto-brightness tracks 10 → 1000 lx within 5 s without visible flicker.
  - With the sensor unplugged, the system falls back to pocket with the display off.
  - The sensor's average current is < 1 µA in S4 (measured on the MCU rail delta).
- SCH-T1 [Schematic netlist v3]: MCU I2C1 scan shows exactly 0x0B, 0x10, 0x28, 0x36, 0x6A (no unexpected ACKs) with the CM5 both on and off. 1,000 back-to-back gauge/charger/ALS transactions complete without NACK or bus hang. Bus recovery (9-clock) is tested after an injected SDA-low.
- SCH-T2: UART link, 115200: the CM5→MCU wake-from-Stop2 frame is answered within 5 ms, 10⁴ frames with zero CRC errors. With the CM5 unpowered, the voltage on GPIO14/15/4 is < 0.3 V (no back-powering).
- SCH-T3: `MCU_IRQ_N` assert → pm-power receives the evdev/gpiod event in < 10 ms. In s2idle (if adopted), an assert resumes the CM5.
- PM/Enc-T5: Wi-Fi antenna: with `dtparam=ant2`, the external FPC antenna is in use. RSSI at 3 m / 10 m from a reference AP is within 3 dB of a reference CM5 + Raspberry Pi antenna kit, and is ≥ 10 dB better than with the FPC disconnected (this proves the external path is selected). `iw dev wlan0 link` throughput is ≥ 20 Mb/s at 10 m.
- PM-P4: Radios: the Wi-Fi/BT rfkill state is blocked ≥ 95 % of the time over a 16 h Profile A run, with radios up only during logged leases.

**Thermal and JEITA [PM 2026-10-21]**. Run in a 25 / 35 / 45 °C chamber, with thermocouples on 6 skin points plus the case NTC, on the mock enclosure.

- TH1: At **35 °C ambient**, a 60-min Profile-A-intensity loop plus a 15-min continuous Q&A stress: skin **≤ 43 °C sustained** (5-min average, every point) and **≤ 48 °C peak**.
- TH2: At **45 °C ambient**: the same loop gives skin **≤ 48 °C (= Ta+3) sustained and ≤ 48 °C peak**. The governor reaches T2/T3 as designed. A heavy request at T2+ shows the cloud offer through the consent dialog, never an automatic send.
- TH3: Governor stage transitions match §10.4 (logged). Hysteresis prevents oscillation (≤ 1 stage change per 30 s). At T4, controlled shutdown and power-on is blocked until skin < 43 °C.
- TH4: The case NTC reading tracks the thermocouple at the grip within ±1.5 K after calibration.
- TH5: CM5 SoC < 65 °C sustained at 25 °C. At 35 °C, it's held < 70 °C by the governor.
- PWR1: **9 W cap**: under a combined worst case (LLM + camera + max backlight + speaker at full volume), the 1 s average cell power is ≤ 9.0 W and the 10 s average ≤ 8.5 W. An injected 3 A load gives `EVT_OVERCURRENT` and a stage drop within 2 s.
- JE1: **Charging stops outside 10–40 °C**. Heat/cool the cell NTC (or substitute resistors) through 5, 9, 11, 13, 37, 39, 41, 46 °C. Charge current is 0 below 10 °C and above 40 °C, and resumes at ≥ 12 °C / ≤ 38 °C. The system stays powered from USB the whole time. `EVT_CHARGE_INHIBIT` is raised and screen 15 shows the reason.
- JE2: Hardware backstop: with MCU firmware halted (debugger), the charger's own JEITA still stops charging at 0 °C and 45 °C. An NTC open or short disables charging.
- JE3: 45 °C chamber, device plugged in: no charging, and the UI or LED shows "too hot to charge". At 35 °C, the charge rate is derated per §12.

---

## 16. Assumptions and open questions

### Resolved by PM [PM 2026-10-21]
| Former ID | Resolution |
|---|---|
| A-7 | 4.3" 800×480 landscape |
| A-14 | Pluggable providers, no lock-in. Sarvam is the opt-in cloud ASR (§6.7) |
| A-17 | Cloud is off by default. "Ask each time" is the only cloud mode, and there's no "always cloud" |
| A-18 | No default expiry. Keep until the user sets auto-delete |
| A-19 | Haptics: LRA DNP, not in the MVP UX (v0.3). Null driver hook only |
| A-24 | MCU RTC = STM32U0 internal RTC + LSE |
| A-25 | STM32U0 (prototype NUCLEO-U031R8) |
| A-30 / A-34 | Resolved v0.3.4: ~3.6 Ah cell in the 22 mm v4_22 body (capacity EST until the cell is sourced). Target 16 h mixed use + ≥ 24 h standby |
| A-12 (OCR) | PaddleOCR / IndicPhotoOCR default |
| A-28 | Latency/thermal targets set by PM (§14) |
| UX pending 1–3 | slot sizes (§2.1), transliteration (§6.12), provider + deletion API (§6.7) |
| v0.3 Q1 | UX adds 22-daily-summary + 09c-translate-overlay, and fixes 16f |
| v0.3 Q2 | 16 h accepted for light use; marketed as "all-day typical use"; validate after benchmarks |
| v0.3 Q3 | Rated 0–40 °C; limited use at 45 °C |
| v0.3 Q4 | Cloud with consent (Sarvam) is the fallback if no small Hinglish model passes |
| v0.3 Q5 | 2 GB: cloud off by default, per-request consent, "Hinglish works best with cloud" notice |
| v0.3 Q6 | Existing public GitHub repo, signed GitHub Releases |
| v0.3 Q7 | Anand is the sole custodian, with an offline backup and a recovery procedure (§2.2.1) |
| v0.3 Q8 | Sarvam first; OpenAI/Gemini optional plug-ins; terms in §6.7.1 |
| v0.3 Q9 / A-19 | LRA DNP on the PCB, not in MVP UX |
| v0.3 Q10 | Devanagari only in MVP; Tamil/Bengali/Telugu in v2 |
| v0.3.1 | A-50 resolved: BYO API key per user, no proxy. Emergency designee: none for now. Sarvam DPA is a pre-launch action for Anand |
| v0.3 Q11 | Audio not stored by default; transcripts only; opt-in audio saving |

### Still open (assumptions)
| ID | Assumption |
|---|---|
| A-1 | pi-gen for the prototype, Yocto for the product (needed for the < 10 s boot) |
| A-2 | PipeWire vs ALSA |
| A-3 | IMX708 camera (research mentions an OV5647 AF cost-down for v2) |
| A-4 | Secure-boot/OTP provisioning flow for LUKS keys and anti-rollback |
| A-6 | Recovery button combo |
| A-8, A-9, A-11, A-13 | memory budgets, model speeds, LLM/VLM choices: to be benchmarked (§6.10) |
| A-15 | Device tz default from onboarding |
| A-16 | **Resolved [Schematic netlist v3.1]**: SW5 DPDT cuts mic power/grounds data when muted; MCU-switched MIC_FEED (U14, PA11) with the green REC LED is implemented |
| A-20 | Idle timers: backlight dim 5 s / off 10 s; post-session hold 30 s (v0.3.2) |
| A-21 | CM5 suspend: decided by the §10.7 test (M5b). Until then, S4 + fast boot |
| A-54 | CM5 minimum CPU OPP for `arm_freq_min` |
| A-55 | Qt basic render loop / idle GPU savings |
| A-56 | RKNN conversion of fine-tuned Indic Whisper encoder |
| A-57 | No RKNN path for IndicTrans2 (CPU CT2 on Radxa) |
| A-58 | RKLLM multimodal availability |
| A-59 | Rockchip secure-boot chain for RAUC/LUKS |
| A-60 | Exact DT method to disable HDMI on CM5 KMS (overlay parameter) |
| A-61 | Amp quiescent current (MAX98357A datasheet) |
| A-62 | Superseded by the enclosure sweep (thermal_v3_ribs §v4); 22 mm chosen |
| A-63 | Resolved [Schematic netlist v3]: case NTC on PB0 ADC |
| A-64 | **Confirmed [Enclosure 2026-10-21]**: stage thresholds apply to the compensated hot-spot estimate for the prototype; relax after M5b |
| A-65 | **Resolved [Enclosure 2026-10-21]**: VEML7700 light sensor (no proximity sensor or IMU in v1) + display state for pocket detection (§10.4.3) |
| A-66 | **Resolved [Schematic netlist v3]**: VEML7700 on STM32U0 I2C1 PB6/PB7 (0x10). CM5-side fallback removed |
| A-68 | Whether STM32U031K8 USART2 can wake from **Stop2** natively (the datasheet lists USART1/2 Stop-mode wake; Stop2 scope unconfirmed); the design uses an EXTI on the RX pin regardless; LPUART1 shares PA2/PA3 as a fallback |
| A-69 | **Address part resolved [Schematic netlist v3]**: STUSB4500 at 0x28; bus map confirmed. Remaining **prototype-only** check: devices on the CM5 IO Board's GPIO2/3 (`i2cdetect -y 1`) vs DRV2605L 0x5A |
| A-70 | **Resolved [Schematic netlist v3]**: U12 TLV62585 from VSYS, EN = CM5_3V3 via 10 k/100 k; no GPIO control |
| A-71 | **Resolved per netlist v3**: PA0 = WKUP1, PA1 = WKUP3 (datasheet re-check at layout; the PDF couldn't be fetched from the box) |
| A-72 | **Resolved [Schematic netlist v3]**: case NTC PB0/PA12; cell NTC → BQ25895 TS |
| A-73 | QFN-32 pin budget: **PA11 now used for `MIC_PWR_EN`** [Schematic netlist v3.1]; the remaining ~9 free pins cover IRQ, power enables, INT/ALRT and the LED with ≤ 1 spare |
| A-74 | The application fits a 26 KB A/B slot; otherwise single slot + ROM-bootloader recovery |
| A-75 | Whether the MAX17055 TH pin senses a thermistor or only reports die temperature (affects how useful the backup is) |
| A-67 | **Resolved**: prototype Akyga LP655063 3000 mAh 1C; production per battery-rfq.md Rev C (≥ 3000/3100 mAh, ≥ 2C). 9 W cap kept (thermal); it holds on the 1C prototype to ~3.2 V and scales below 3.3 V |
| A-76 | Prototype LP655063 NTC β unknown: firmware uses configurable thresholds and a worst-of-two-β conversion until the M5b measurement |
| A-77 | Whether SW5 pole 2 still grounds the mic data line in netlist v3.2 |
| A-78 | **Resolved [Tech Research 2026-10-21, v0.3.11]**: no conflict. Prototype = LP655063 (1C, ≤ 65.5 × 51 × 7.0 mm); production = RFQ Rev C (≥ 2C, ≤ 8.5 × 50.5 × 62 mm, ≥ 3000/3100 mAh, B3435) |
| A-79 | **Resolved (Enclosure v4_22b):** prototype LP655063 fits with ~3.5 mm real end space and a lead U-turn over the cell face; no notch. |
| A-22 | (superseded by the locked 20/10/3 %) |
| A-23 | Closed [Schematic netlist v3]: UART0↔USART2 only |
| A-26 | Gauge/charger parts (BQ25895, MAX17055/48 candidates) |
| A-31 | IO Board power/RUN headers and NUCLEO-U031R8 pinout to verify |
| A-32 | Milestone durations |
| A-33 | WER pass bars EN 12 / HI 20 / Hinglish 25 %, and test-set licensing |
| A-35 | Piper `hi_IN` voice availability and quality |
| A-36 | IndicTrans2-dist / IndicPhotoOCR CM5 performance and script coverage |
| A-37 | Qt VKB Devanagari layouts + custom phonetic layout effort |
| A-38 | IndicXlit size/latency after CT2/ONNX export |
| A-39 | unicode61 behaviour on Devanagari matras |
| A-40 | Sarvam: no per-request deletion API found; docs (indefinite until set) vs privacy policy (30 days after last access) disagree on default retention |
| A-53 | The device can't verify the user's Sarvam retention/training settings, and no API-level training opt-out was found |
| A-51 | OpenAI stored-response delete endpoint semantics: verify in the current API reference |
| A-52 | Gemini unpaid-tier data-use wording, and detecting billing-enabled projects at setup |
| A-41 | Daily summary default time 20:30, opt-in |
| A-42, A-43 | Usable-energy factors and per-state power figures |
| A-44 | STM32U0 Stop2 current with RTC/LPTIM (datasheet check) |
| A-45 | Separate ambient NTC on the custom PCB |
| A-46 | Device thermal mass ≈ 225 J/K |
| A-47 | Charge derating above 35 °C |
| A-48 | MCU emergency cut at skin > 55 °C |

### Open questions / pre-launch actions (v0.3.1)
1. **Pre-launch action (Anand)**: sign a Sarvam DPA. Have it confirm default retention (docs and privacy policy disagree), whether a per-request deletion API exists, and the training opt-out for API customers. Until then, Sarvam terms are marked unconfirmed.
2. Compute (v0.3.3): staying on Pi CM5 is decided. M5b (the §10.8 idle levers plus the §10.7 suspend test) gates the 16 h claim and the final body thickness (22 vs 24–26 mm, §10.3c). The rev-2 Radxa option is parked.
3. Benchmarks (§6.10) still gate the final ASR/OCR/translation model choices and the "all-day typical use" claim.

---

## 17. Rev-2 portability: Radxa CM5 (RK3588S2, RKNN NPU) (v0.3.2)

**Status**: not v1, and **unfunded until after M5b** [PM/Enclosure 2026-10-21]. **Anand decided on 2026-10-21 to stay on Pi CM5.** This section is kept as a portability guardrail and an option for later. A rev-2 evaluation runs in parallel on a second carrier spin (research/compute-options.md recommendation). Rationale [Research]:
- idle **1.2 W vs 2.4 W**, which fits about a 2 W budget;
- a 6 TOPS NPU for LLM/ASR/OCR offload;
- India module price ≈ ₹7,732 + GST vs ₹15,000.

Risks [Research]:
- **not drop-in**: CM4-style pinout plus a third 100-pin connector, so a carrier respin;
- vendor kernel for the NPU;
- no libcamera/IMX708 AF pipeline (vendor rkaiq ISP);
- different DSI device tree;
- India stock was 0.

The goal of this section is to make v1 code **portable by construction**, so rev 2 is a platform port and not a rewrite.

### 17.1 Platform HAL (`pocketmate.platform`)

```python
@dataclass(frozen=True)
class PlatformCaps:
    soc: Literal["bcm2712", "rk3588s", "rk3576"]
    ram_mb: int
    accel: frozenset[Literal["cpu_neon", "rknpu", "vulkan", "gles"]]
    npu_tops: float | None
    camera_stack: Literal["libcamera", "rkaiq_v4l2"]
    suspend_states: frozenset[Literal["s2idle", "deep"]]      # from §10.7-style probe
    boot_ab: Literal["rpi_tryboot", "uboot_bootchooser"]
    secure_boot: Literal["rpi_otp", "rockchip_otp", "none"]

class Platform(Protocol):
    caps: PlatformCaps
    # power / thermal
    def set_cpu_policy(self, max_khz: int, online_cores: int) -> None: ...
    def set_gpu_policy(self, level: Literal["min", "auto", "max"]) -> None: ...
    def soc_temp_c(self) -> float: ...
    def suspend(self, state: str) -> None: ...
    # display / camera / audio
    def backlight(self, pct: int) -> None: ...
    def fan_set(self, pct: int) -> None: ...                   # unused hook: v1 baseline is fan-free (no-op)
    def panel_power(self, on: bool) -> None: ...
    def camera_open(self, mode: str) -> "CameraSession": ...   # libcamera (Pi) | rkaiq/v4l2 (Rockchip)
    def audio_devices(self) -> dict[str, str]: ...             # logical -> ALSA card names
    # system
    def watchdog_path(self) -> str: ...
    def rtc_path(self) -> str: ...
    def mcu_uart_path(self) -> str: ...
    def ab_mark_good(self) -> None: ...                         # tryboot vs U-Boot bootchooser (RAUC)
```
- Implementations: `platform/rpi_cm5.py` (v1) and `platform/radxa_cm5.py` (rev 2).
- `pm-profile` (§6.11) detects the platform from `/proc/device-tree/compatible` (`raspberrypi,5-compute-module` vs `radxa,cm5`/`rockchip,rk3588s`) before choosing models.
- No service may touch `/sys` power/thermal/backlight paths or `vcgencmd` directly. Everything goes through `Platform`. A lint rule and a CI grep enforce this.

### 17.2 Backend registry with capability flags

`EngineInfo` (§6.1) gains `requires: frozenset[str]` (e.g., `{"rknpu"}`), `formats: frozenset[str]`, and `est_power_w`. The registry picks the **highest-priority backend whose `requires ⊆ caps.accel` and whose model file is present in the models pack**, falling back to the CPU.

| Function | v1 Pi CM5 (CPU) | Rev 2 Radxa CM5 (NPU-first) | Fallback on Radxa |
|---|---|---|---|
| LLM | llama.cpp **GGUF** Q4_K_M | **RKLLM** runtime (`.rkllm`, w4a16 / w8a8) via `rkllm-server`/`librkllmrt` [Research: ~16 tok/s class on RK3588; Qwen-class rows to verify] | llama.cpp GGUF on 4× A76 |
| ASR | whisper.cpp ggml (Indic/Hinglish fine-tune) + Vosk | Whisper encoder on **RKNN** (`.rknn`, rknn_model_zoo-style) + decoder on CPU [A-56: fine-tuned Indic checkpoint conversion unverified] | whisper.cpp on CPU |
| OCR | PaddleOCR ONNX Runtime | PP-OCR det/rec on **RKNN** (`.rknn`, int8) | ONNX Runtime CPU |
| Translation | CTranslate2 int8 (IndicTrans2-dist) | CTranslate2 on CPU (seq2seq RKNN conversion not planned) [A-57] | — |
| Embeddings | llama.cpp / ONNX | RKNN (`.rknn`) | ONNX CPU |
| TTS | Piper ONNX | Piper ONNX (CPU, light) | — |
| Vision | llama.cpp mtmd GGUF | RKLLM multimodal if available, otherwise CPU [A-58] | CPU |

**GGUF vs RKNN in practice**:
- GGUF is a single portable file: quantize once, run on any ARM CPU.
- RKNN/RKLLM are **compiled per SoC and per toolkit version**. Conversion runs offline on x86 with `rknn-toolkit2` / `rkllm-toolkit` and a calibration set. Outputs aren't portable across runtime versions.
- Models packs therefore become per-platform: `pocketmate-models-<ver>-rpi-cm5-4g.raucb` vs `-radxa-cm5-4g.raucb`. The manifest records `format`, `soc`, `toolkit_version` and `runtime_version`, and pm-profile refuses a mismatched pack.
- Accuracy parity gate: every RKNN/RKLLM conversion must hold within +1 pt WER/CER (or within 2 % JSON-extraction accuracy) of the CPU reference on the §6.10 sets.

### 17.3 Kernel, device tree, boot and power HAL deltas

| Layer | Pi CM5 (v1) | Radxa CM5 (rev 2) |
|---|---|---|
| Kernel | RPi vendor 6.6+/6.12 | Radxa/Rockchip vendor 6.1 BSP with `rknpu` (NPU driver). Mainline RK3588 support exists, but NPU support in mainline is immature [Research]. Pin the vendor kernel for rev 2 |
| Device tree | `config.txt` + dtoverlays (§3) | U-Boot + `rockchip` DT overlays: a new `pocketmate-carrier-rk3588s.dtbo` for DSI panel timings, I2S codec, UART to MCU, GPIOs, NTC/ADC (SARADC) |
| Boot / A/B | `tryboot`/autoboot.txt + RAUC | U-Boot **RAUC bootchooser** (`BOOT_ORDER`/`BOOT_x_LEFT` env), RAUC unchanged. eMMC partitions (§2.1) are reused with an idbloader/U-Boot prefix |
| Secure boot | RPi OTP signed boot | Rockchip secure boot (OTP key hash, signed U-Boot/FIT) [A-59] |
| GPU / UI | VideoCore VII, Qt EGLFS on vc4-kms | Mali-G610: Qt EGLFS on KMS (Panthor mainline or vendor Mali blob). Re-verify 60 fps and the Devanagari text path |
| Camera | libcamera + IMX708 AF | rkaiq ISP / V4L2. **IMX708 AF unsupported**, so pick a vendor-supported AF sensor [Research]. `CameraSession` HAL hides the difference |
| Power / thermal | cpufreq on 4× A76; no usable suspend (pending §10.7) | big.LITTLE: UI pinned to A55 cores, A76 cores offline unless bursting. devfreq for DDR/GPU/NPU. **s2idle/deep likely available** (RK3588 SoM suspend 0.59 W) → rerun §10.7. PMIC RK806 |
| Watchdog / RTC | BCM2712 WDT, on-board RTC | RK WDT, PMIC RTC. The MCU RTC remains the source of truth |
| MCU protocol | §11 | **unchanged**. Only the UART device path differs (HAL) |

**Effort / milestone**: rev-2 port **R2-M1** (not in v1):
- board bring-up;
- Platform HAL implementation;
- RKLLM/RKNN conversions for the LLM, OCR and Whisper encoder;
- §6.10 benchmarks and §10.7 tests on Radxa;
- the parity gate.
Exit criterion: the same B5 acceptance suite passes with the platform-specific model pack.

