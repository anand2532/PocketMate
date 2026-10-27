#include "pm_app.h"
#include <string.h>
#include "pm_hal.h"

pm_app_t g_app;

static void tx(uint8_t type, uint8_t seq, const void *p, uint8_t len) {
    uint8_t out[PM_WIRE_MAX];
    size_t n = pm_frame_encode(type, seq, (const uint8_t *)p, len, out, sizeof out);
    if (n && g_app.cm5_on) hal_uart_write(out, n);    /* TX is Hi-Z while the CM5 is unpowered (§11) */
}

static void evt(uint8_t type, const void *p, uint8_t len) {
    g_app.tx_seq = (uint8_t)(g_app.tx_seq + 1);
    if (g_app.tx_seq == 0) g_app.tx_seq = 0x80;      /* MCU-originated seqs >= 0x80 (matches the Python sim) [impl] */
    if (g_app.tx_seq < 0x80) g_app.tx_seq = 0x80;
    tx(type, g_app.tx_seq, p, len);
    g_app.events_sent++;
    if (g_app.cm5_on) hal_irq_n(true);                /* released when the CM5 ACKs; Hi-Z while CM5 off */
}

static void ack(uint8_t seq, pm_status_t st) {
    pm_ack_t a = {seq, (uint8_t)st};
    if (st != STATUS_OK) g_app.nak_count++;
    tx(PM_MSG_ACK, seq, &a, sizeof a);
}

static void on_rail(bool on, pm_railreason_t why, uint16_t sid) {
    pm_evt_mic_rail_t e = {on, (uint8_t)why, sid};
    evt(PM_MSG_EVT_MIC_RAIL, &e, sizeof e);
}

/* Minimal power_fsm (§10.1/§12): S4 -> S0 on POWER/ACTION press; S5 cut timer; POWER 10 s hard cut. */
static void cm5_power(bool on) {
    g_app.cm5_cmd = on; g_app.cut_pending = false;
    if (!on) pm_privacy_force_off(&g_app.priv, RAILREASON_POWER_DOWN);   /* rail first */
    hal_cm5_power(on);
    g_app.pstate = on ? PSTATE_S0 : PSTATE_S4;
}

static void on_button(uint8_t id, pm_btnact_t act, uint32_t t) {
    if (!g_app.cm5_cmd && act == BTNACT_DOWN && (id == BTN_PWR || id == BTN_ACTION)) cm5_power(true);
    if (id == BTN_ACTION && (act == BTNACT_DOWN || act == BTNACT_UP)) pm_privacy_on_action(&g_app.priv, act == BTNACT_DOWN);
    /* VOL± are masked while the CM5 is off (pocket presses must not wake, §12) */
    if (!g_app.cm5_on && (id == BTN_VOL_UP || id == BTN_VOL_DOWN)) return;
    pm_evt_button_t e = {id, (uint8_t)act, t, 0};
    evt(PM_MSG_EVT_BUTTON, &e, sizeof e);
}

void pm_app_init(uint8_t boot_reason) {
    hal_init_safe_outputs();                      /* PA11 low before anything else */
    memset(&g_app, 0, sizeof g_app);
    g_app.boot_reason = boot_reason;
    g_app.pstate = PSTATE_S4;
    pm_deframer_init(&g_app.rx);
    pm_privacy_boot(&g_app.priv, on_rail);
    pm_buttons_init(&g_app.btn, on_button);
    pm_charge_init(&g_app.chg);
    pm_wdtsup_init(&g_app.wdt);
}

void pm_app_set_cm5_power_good(bool pg) {
    g_app.cm5_on = pg;
    pm_privacy_on_power_good(&g_app.priv, pg);
    pm_wdtsup_arm(&g_app.wdt, g_app.priv.now_ms, pg);
    if (!pg) hal_irq_n(false);                    /* Hi-Z: never back-power CM5 IO */
}

void pm_app_mute_edge(bool high) {
    pm_privacy_on_mute_pin(&g_app.priv, high);    /* rail cut first, report second */
    pm_evt_mic_mute_t e = {high, pm_privacy_mute_valid(&g_app.priv), g_app.priv.now_ms};
    evt(PM_MSG_EVT_MIC_MUTE, &e, sizeof e);
}

static uint32_t rd32(const uint8_t *p) { return (uint32_t)p[0] | (uint32_t)p[1] << 8 | (uint32_t)p[2] << 16 | (uint32_t)p[3] << 24; }
static uint16_t rd16(const uint8_t *p) { return (uint16_t)(p[0] | p[1] << 8); }

static pm_status_t need(const pm_frame_t *f, uint8_t n) { return f->len == n ? STATUS_OK : STATUS_BAD_LEN; }

static void dispatch(const pm_frame_t *f) {
    pm_privacy_on_frame_rx(&g_app.priv);
    pm_status_t st = STATUS_OK;
    switch (f->type) {
    case PM_MSG_ACK:
        hal_irq_n(false);
        return;                                   /* ACKs are never ACKed */
    case PM_MSG_HELLO: {
        if ((st = need(f, PM_LEN_HELLO)) != STATUS_OK) break;
        if (f->payload[0] != PM_PROTO_VER) { st = STATUS_BAD_VERSION; break; }
        ack(f->seq, STATUS_OK);
        uint8_t flags = (uint8_t)((g_app.priv.muted_pin << 1) | (pm_privacy_mute_valid(&g_app.priv) << 2));
        pm_hello_ack_t h = {PM_PROTO_VER, PM_MCU_FW_VER, g_app.boot_reason, flags, 0};
        evt(PM_MSG_HELLO_ACK, &h, sizeof h);
        return;
    }
    case PM_MSG_HEARTBEAT:
        if ((st = need(f, PM_LEN_HEARTBEAT)) != STATUS_OK) break;
        pm_privacy_on_heartbeat(&g_app.priv);
        pm_wdtsup_heartbeat(&g_app.wdt, g_app.priv.now_ms);
        break;
    case PM_MSG_SET_STATE:
        if ((st = need(f, PM_LEN_SET_STATE)) != STATUS_OK) break;
        if (f->payload[0] > PSTATE_SHIP) { st = STATUS_RANGE; break; }
        g_app.pstate = f->payload[0];
        break;
    case PM_MSG_SET_WAKE:
        if ((st = need(f, PM_LEN_SET_WAKE)) != STATUS_OK) break;
        g_app.wake_epoch = rd32(f->payload);     /* RTC Alarm A programming: target/hal (hardware) */
        break;
    case PM_MSG_MIC_ENABLE:
        if ((st = need(f, PM_LEN_MIC_ENABLE)) != STATUS_OK) break;
        st = pm_privacy_mic_enable(&g_app.priv, f->payload[0] != 0, rd16(&f->payload[1]), f->payload[3], rd16(&f->payload[4]));
        break;
    case PM_MSG_SHUTDOWN_READY:
        pm_privacy_force_off(&g_app.priv, RAILREASON_POWER_DOWN);
        g_app.cut_pending = true; g_app.cut_at_ms = g_app.priv.now_ms + PM_CUT_DELAY_MS;
        g_app.pstate = PSTATE_S5;
        break;
    case PM_MSG_BOOT_MODE:
        if ((st = need(f, PM_LEN_BOOT_MODE)) != STATUS_OK) break;
        g_app.boot_mode = f->payload[0];
        break;
    case PM_MSG_HAPTIC: case PM_MSG_HAPTIC_CFG:
        break;                                    /* LRA is DNP in MVP: accepted, no-op */
    case PM_MSG_LTE_CFG: {
        if ((st = need(f, PM_LEN_LTE_CFG)) != STATUS_OK) break;
        const uint8_t *p = f->payload;            /* present u8, vreg_max_mV u16 LE */
        if (!pm_charge_set_lte(&g_app.chg, p[0] != 0, rd16(p + 1))) st = STATUS_RANGE;
        break;
    }
    case PM_MSG_SET_CHARGE_CFG: {
        if ((st = need(f, PM_LEN_SET_CHARGE_CFG)) != STATUS_OK) break;
        pm_charge_cfg_t c;
        const uint8_t *p = &f->payload[14];
        c.cold_off = (int16_t)rd16(p); c.cold_on = (int16_t)rd16(p + 2); c.hot_on = (int16_t)rd16(p + 4);
        c.hot_off = (int16_t)rd16(p + 6); c.derate = (int16_t)rd16(p + 8);
        if (!pm_charge_cfg_valid(&c)) { st = STATUS_RANGE; break; }
        g_app.chg.cfg = c;                        /* config-flash write: target (hardware) */
        break;
    }
    case PM_MSG_LED: case PM_MSG_WDT_CFG: case PM_MSG_SET_THERMAL_CAL: case PM_MSG_SET_POWER_CAP:
    case PM_MSG_TIME: case PM_MSG_FW_UPDATE:
        break;                                    /* parsed/handled on target; TODO(fw) see firmware/README.md */
    default:
        st = STATUS_UNKNOWN_TYPE;
    }
    ack(f->seq, st);
}

void pm_app_rx_byte(uint8_t b) {
    pm_frame_t f;
    if (pm_deframer_feed(&g_app.rx, b, &f)) dispatch(&f);
}

void pm_app_tick(uint32_t now) {
    g_app.priv.now_ms = now;
    for (uint8_t i = 0; i < PM_BTN_N; i++) pm_buttons_sample(&g_app.btn, i, hal_button_raw_down(i), now);
    pm_buttons_tick(&g_app.btn, now);
    if (g_app.btn.hard_cut) { g_app.btn.hard_cut = false; if (g_app.cm5_cmd) cm5_power(false); }  /* + ship mode: TODO(I2C) */
    if (g_app.cut_pending && (int32_t)(now - g_app.cut_at_ms) >= 0) cm5_power(false);
    bool pg = hal_cm5_power_good();
    if (pg != g_app.cm5_on) pm_app_set_cm5_power_good(pg);
    bool mute = hal_mute_pin_high();
    if (mute != g_app.priv.muted_pin) pm_app_mute_edge(mute);
    pm_privacy_tick(&g_app.priv, now);
    if (pm_wdtsup_tick(&g_app.wdt, now)) pm_privacy_force_off(&g_app.priv, RAILREASON_WDT);
    hal_wdt_refresh();
}
