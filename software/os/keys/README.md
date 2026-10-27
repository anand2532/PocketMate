# os/keys — PLACEHOLDERS ONLY

**No keys are generated, stored or committed here** (ARCHITECTURE.md §2.2 / §2.2.1: never in the repo, in
GitHub Actions secrets, or on the build box).

| Path | What goes here | Who creates it |
|---|---|---|
| `public/keyring.pem` | public root CA cert (+ CRL) that devices trust; copied to `/etc/rauc/keyring.pem` | Anand, on the offline laptop (§2.2.1). **Not present yet** — the image build fails closed without it unless `PM_DEV_KEYRING=1` |
| `public/mcu-ed25519.pub` | public key the MCU bootloader/pm-power uses to verify `mcu-firmware` bundles | Anand |
| `CUSTODY.md` | fingerprints, token serials, validity, generic locations, last drill date | Anand (template below) |

The stage script `pi-gen/stage-pm/03-rauc/00-run.sh` refuses to build a production image if
`public/keyring.pem` is missing.
