#include <string.h>
#include "hal_mock.h"
#include "pm_app.h"
#include "pm_cobs.h"
#include "pm_crc16.h"
#include "pm_frame.h"
#include "pm_proto_vectors.h"
#include "tinytest.h"

int tt_fail, tt_checks, tt_tests;

/* ---- codec: cross-language vectors generated from the Python implementation ---- */
static void test_crc_check(void) { CHECK_EQ(pm_crc16((const uint8_t *)"123456789", 9, 0xFFFF), PM_CRC_CHECK_123456789); }

static void test_vectors_encode(void) {
    for (unsigned i = 0; i < PM_N_VECTORS; i++) {
        const pm_vector_t *v = &pm_vectors[i];
        uint8_t out[PM_WIRE_MAX];
        size_t n = pm_frame_encode(v->type, v->seq, v->payload, v->payload_len, out, sizeof out);
        CHECK_EQ(n, v->wire_len);
        CHECK(n == v->wire_len && memcmp(out, v->wire, n) == 0);
    }
}

static void test_vectors_decode_stream(void) {
    pm_deframer_t d; pm_frame_t f; pm_deframer_init(&d);
    unsigned got = 0;
    pm_deframer_feed(&d, 0x00, &f);                         /* wake preamble */
    for (unsigned i = 0; i < PM_N_VECTORS; i++) {
        const pm_vector_t *v = &pm_vectors[i];
        for (unsigned k = 0; k < v->wire_len; k++)
            if (pm_deframer_feed(&d, v->wire[k], &f)) {
                got++;
                CHECK_EQ(f.type, v->type); CHECK_EQ(f.seq, v->seq); CHECK_EQ(f.len, v->payload_len);
                CHECK(memcmp(f.payload, v->payload, f.len) == 0);
            }
    }
    CHECK_EQ(got, PM_N_VECTORS); CHECK_EQ(d.bad, 0);
}

static void test_corrupt_and_oversize_dropped(void) {
    pm_deframer_t d; pm_frame_t f; pm_deframer_init(&d);
    const pm_vector_t *v = &pm_vectors[1];
    uint8_t w[64]; memcpy(w, v->wire, v->wire_len); w[6] ^= 0x01;
    bool any = false;
    for (unsigned k = 0; k < v->wire_len; k++) any |= pm_deframer_feed(&d, w[k], &f);
    CHECK(!any); CHECK_EQ(d.bad, 1);
    for (unsigned k = 0; k < 300; k++) pm_deframer_feed(&d, 0x55, &f);
    CHECK(!pm_deframer_feed(&d, 0x00, &f)); CHECK_EQ(d.bad, 2);
    for (unsigned k = 0; k < v->wire_len; k++) any |= pm_deframer_feed(&d, v->wire[k], &f);
    CHECK(any);                                              /* recovers on the next frame */
}

static void test_cobs_roundtrip_254(void) {
    uint8_t in[300], enc[310], dec[300];
    for (int i = 0; i < 300; i++) in[i] = (uint8_t)(i % 7 ? i : 0);
    size_t n = pm_cobs_encode(in, 300, enc, sizeof enc);
    CHECK(n > 0);
    for (size_t i = 0; i < n; i++) CHECK(enc[i] != 0);
    CHECK_EQ(pm_cobs_decode(enc, n, dec, sizeof dec), 300);
    CHECK(memcmp(in, dec, 300) == 0);
}

/* ---- privacy interlock: same scenarios as services/tests/test_privacy_model.py ---- */
static int rail_on_events, rail_off_events; static pm_railreason_t last_reason;
static void rail(bool on, pm_railreason_t r, uint16_t sid) { (void)sid; if (on) rail_on_events++; else rail_off_events++; last_reason = r; }
static pm_privacy_t P;
static void up_unmuted(void) {
    rail_on_events = rail_off_events = 0;
    pm_privacy_boot(&P, rail);
    pm_privacy_on_power_good(&P, true);
    pm_privacy_on_mute_pin(&P, false);
    pm_privacy_on_heartbeat(&P);
}

static void test_boot_pa11_low_and_fail_closed(void) {
    M.pa11 = true;
    pm_privacy_boot(&P, rail);
    CHECK(!M.pa11); CHECK_EQ(last_reason, RAILREASON_RESET);
    CHECK_EQ(pm_privacy_mic_enable(&P, true, 1, MICMODE_HOLD, 0), STATUS_MUTE_INVALID);
    P.muted_pin = false;   /* even a low pin is not trusted without power-good */
    CHECK_EQ(pm_privacy_mic_enable(&P, true, 1, MICMODE_HOLD, 0), STATUS_MUTE_INVALID);
    CHECK(!M.pa11);
}

static void test_hold_requires_ptt_and_release_cuts(void) {
    up_unmuted();
    CHECK_EQ(pm_privacy_mic_enable(&P, true, 5, MICMODE_HOLD, 0), STATUS_NO_PTT);
    pm_privacy_on_action(&P, true);
    CHECK_EQ(pm_privacy_mic_enable(&P, true, 5, MICMODE_HOLD, 0), STATUS_OK);
    CHECK(M.pa11); CHECK_EQ(rail_on_events, 1);
    pm_privacy_on_action(&P, false);
    CHECK(!M.pa11); CHECK_EQ(last_reason, RAILREASON_RELEASE);
}

static void test_muted_refused_and_mute_edge_cuts(void) {
    up_unmuted();
    pm_privacy_on_action(&P, true);
    pm_privacy_on_mute_pin(&P, true);
    for (int i = 0; i < 100; i++) CHECK_EQ(pm_privacy_mic_enable(&P, true, 1, MICMODE_HOLD, 0), STATUS_MUTED);
    CHECK_EQ(M.pa11_on_count, 0);
    pm_privacy_on_mute_pin(&P, false);
    CHECK_EQ(pm_privacy_mic_enable(&P, true, 1, MICMODE_HOLD, 0), STATUS_OK);
    pm_privacy_on_mute_pin(&P, true);
    CHECK(!M.pa11); CHECK_EQ(last_reason, RAILREASON_MUTE);
}

static void test_tap_window_single_use(void) {
    up_unmuted();
    P.now_ms = 1000; pm_privacy_on_action(&P, true); pm_privacy_on_action(&P, false);
    P.now_ms = 2500; P.last_rx_ms = P.last_hb_ms = 2500;
    CHECK_EQ(pm_privacy_mic_enable(&P, true, 1, MICMODE_TAP, 0), STATUS_NO_PTT);   /* > 1 s */
    P.now_ms = 3000; pm_privacy_on_action(&P, true); pm_privacy_on_action(&P, false);
    P.now_ms = 3500;
    CHECK_EQ(pm_privacy_mic_enable(&P, true, 2, MICMODE_TAP, 0), STATUS_OK);
    pm_privacy_mic_enable(&P, false, 2, 0, 0);
    CHECK_EQ(pm_privacy_mic_enable(&P, true, 3, MICMODE_TAP, 0), STATUS_NO_PTT);   /* press consumed */
}

static void test_caps_and_timeouts(void) {
    up_unmuted();
    pm_privacy_on_action(&P, true);
    CHECK_EQ(pm_privacy_mic_enable(&P, true, 1, MICMODE_HOLD, 121), STATUS_RANGE);
    CHECK_EQ(pm_privacy_mic_enable(&P, true, 1, 9, 0), STATUS_RANGE);
    CHECK_EQ(pm_privacy_mic_enable(&P, true, 1, MICMODE_HOLD, 0), STATUS_OK);
    for (uint32_t t = 1000; t < 120000; t += 1000) { P.last_rx_ms = P.last_hb_ms = t; pm_privacy_tick(&P, t); }
    CHECK(M.pa11);
    P.last_rx_ms = P.last_hb_ms = 120000; pm_privacy_tick(&P, 120000);
    CHECK(!M.pa11); CHECK_EQ(last_reason, RAILREASON_TIMEOUT);
    /* dictation allows 600 s (needs a fresh press: non-hold modes use the 1 s tap window) */
    P.now_ms = 120000; pm_privacy_on_action(&P, true);
    CHECK_EQ(pm_privacy_mic_enable(&P, true, 2, MICMODE_DICTATION, 600), STATUS_OK);
    /* link loss > 2 s */
    pm_privacy_tick(&P, 120000 + 2001);
    CHECK(!M.pa11); CHECK_EQ(last_reason, RAILREASON_LINK_LOSS);
}

static void test_power_down_cuts(void) {
    up_unmuted();
    pm_privacy_on_action(&P, true);
    pm_privacy_mic_enable(&P, true, 1, MICMODE_HOLD, 0);
    pm_privacy_on_power_good(&P, false);
    CHECK(!M.pa11); CHECK_EQ(last_reason, RAILREASON_POWER_DOWN);
}

/* ---- charge control (JEITA firmware layer) ---- */
static void test_charge_hysteresis(void) {
    pm_charge_t c; pm_charge_init(&c);
    CHECK(!M.charger);
    pm_charge_update(&c, 250, 250, false); CHECK(c.enabled && M.charger);
    pm_charge_update(&c, 99, 99, false);   CHECK(!c.enabled && c.reason == CHG_INHIBIT_COLD);
    pm_charge_update(&c, 110, 110, false); CHECK(!c.enabled);                 /* < 12 °C: still off */
    pm_charge_update(&c, 120, 120, false); CHECK(c.enabled);
    pm_charge_update(&c, 360, 360, false); CHECK(c.enabled && c.derated);
    pm_charge_update(&c, 401, 401, false); CHECK(!c.enabled && c.reason == CHG_INHIBIT_HOT);
    pm_charge_update(&c, 390, 390, false); CHECK(!c.enabled);                 /* > 38 °C: still off */
    pm_charge_update(&c, 380, 380, false); CHECK(c.enabled);
    pm_charge_update(&c, 250, 370, false); CHECK(!c.enabled && c.reason == CHG_INHIBIT_FAULT);  /* >10 K */
    pm_charge_update(&c, 250, 250, true);  CHECK(!c.enabled);
    pm_charge_cfg_t bad = {100, 90, 380, 400, 350}; CHECK(!pm_charge_cfg_valid(&bad));
    pm_charge_cfg_t hot = {100, 120, 380, 460, 350}; CHECK(!pm_charge_cfg_valid(&hot));
    CHECK(pm_charge_cfg_valid(&c.cfg));
}

/* ---- CM5 heartbeat supervisor ---- */
static void test_wdt_supervisor(void) {
    pm_wdtsup_t w; pm_wdtsup_init(&w);
    CHECK(!pm_wdtsup_tick(&w, 100000));                      /* not armed */
    pm_wdtsup_arm(&w, 0, true);
    for (uint32_t t = 5000; t <= 60000; t += 5000) { pm_wdtsup_heartbeat(&w, t); CHECK(!pm_wdtsup_tick(&w, t)); }
    CHECK(!pm_wdtsup_tick(&w, 90000));
    CHECK(pm_wdtsup_tick(&w, 90001)); CHECK_EQ(M.run_pulses, 1); CHECK(!w.want_recovery);
    CHECK(pm_wdtsup_tick(&w, 120002)); CHECK(pm_wdtsup_tick(&w, 150003));
    CHECK(w.want_recovery);                                  /* 3 resets within 10 min */
}

/* ---- buttons ---- */
static int ev[8][3], nev;
static void bcb(uint8_t id, pm_btnact_t a, uint32_t t) { if (nev < 8) { ev[nev][0] = id; ev[nev][1] = a; ev[nev][2] = (int)t; nev++; } }
static void test_buttons_debounce_long(void) {
    pm_buttons_t b; nev = 0; pm_buttons_init(&b, bcb);
    pm_buttons_sample(&b, BTN_ACTION, true, 0); pm_buttons_tick(&b, 2);
    pm_buttons_sample(&b, BTN_ACTION, false, 3); pm_buttons_tick(&b, 9);   /* 3 ms bounce: ignored */
    CHECK_EQ(nev, 0);
    pm_buttons_sample(&b, BTN_ACTION, true, 10); pm_buttons_tick(&b, 15);
    CHECK_EQ(nev, 1); CHECK_EQ(ev[0][1], BTNACT_DOWN);
    pm_buttons_tick(&b, 2015); CHECK_EQ(ev[1][1], BTNACT_LONG);
    pm_buttons_sample(&b, BTN_ACTION, false, 2100); pm_buttons_tick(&b, 2105);
    CHECK_EQ(nev, 3); CHECK_EQ(ev[2][1], BTNACT_UP);           /* no SHORT after LONG */
    pm_buttons_sample(&b, BTN_PWR, true, 3000); pm_buttons_tick(&b, 3005); pm_buttons_tick(&b, 13005);
    CHECK(b.hard_cut);
}

/* ---- app: frames in, ACK/NAK + events out ---- */
static size_t send_frame(uint8_t type, uint8_t seq, const void *p, uint8_t n) {
    uint8_t w[PM_WIRE_MAX];
    size_t k = pm_frame_encode(type, seq, p, n, w, sizeof w);
    pm_app_rx_byte(0x00);
    for (size_t i = 0; i < k; i++) pm_app_rx_byte(w[i]);
    return k;
}
static int find_ack(uint8_t seq) {   /* returns status or -1 */
    pm_deframer_t d; pm_frame_t f; pm_deframer_init(&d); int st = -1;
    for (size_t i = 0; i < M.tx_len; i++) if (pm_deframer_feed(&d, M.tx[i], &f) && f.type == PM_MSG_ACK && f.payload[0] == seq) st = f.payload[1];
    return st;
}
static int count_type(uint8_t type) {
    pm_deframer_t d; pm_frame_t f; pm_deframer_init(&d); int n = 0;
    for (size_t i = 0; i < M.tx_len; i++) if (pm_deframer_feed(&d, M.tx[i], &f) && f.type == type) n++;
    return n;
}

static void test_app_mic_enable_flow(void) {
    pm_app_init(BOOT_PWR_BUTTON);
    CHECK_EQ(M.safe_init_calls, 1); CHECK(!M.pa11);
    M.pg = true; M.mute_high = false; M.now = 10; pm_app_tick(10);
    CHECK(g_app.cm5_on); CHECK_EQ(count_type(PM_MSG_EVT_MIC_MUTE), 1);
    pm_hello_t h = {PM_PROTO_VER, 0x00040000}; send_frame(PM_MSG_HELLO, 1, &h, sizeof h);
    CHECK_EQ(find_ack(1), STATUS_OK); CHECK_EQ(count_type(PM_MSG_HELLO_ACK), 1);
    pm_mic_enable_t me = {1, 0x1234, MICMODE_HOLD, 0};
    send_frame(PM_MSG_MIC_ENABLE, 2, &me, sizeof me);
    CHECK_EQ(find_ack(2), STATUS_NO_PTT); CHECK(!M.pa11);
    M.btn[BTN_ACTION] = true; pm_app_tick(11); pm_app_tick(20);
    CHECK_EQ(count_type(PM_MSG_EVT_BUTTON), 1);
    send_frame(PM_MSG_MIC_ENABLE, 3, &me, sizeof me);
    CHECK_EQ(find_ack(3), STATUS_OK); CHECK(M.pa11); CHECK_EQ(count_type(PM_MSG_EVT_MIC_RAIL), 1);
    M.mute_high = true; pm_app_tick(30);
    CHECK(!M.pa11); CHECK_EQ(count_type(PM_MSG_EVT_MIC_RAIL), 2); CHECK_EQ(count_type(PM_MSG_EVT_MIC_MUTE), 2);
    send_frame(PM_MSG_MIC_ENABLE, 4, &me, sizeof me);
    CHECK_EQ(find_ack(4), STATUS_MUTED);
    send_frame(0x7E, 5, NULL, 0); CHECK_EQ(find_ack(5), STATUS_UNKNOWN_TYPE);
    send_frame(PM_MSG_MIC_ENABLE, 6, &me, 3); CHECK_EQ(find_ack(6), STATUS_BAD_LEN);
    pm_hello_t bad = {9, 0}; send_frame(PM_MSG_HELLO, 7, &bad, sizeof bad); CHECK_EQ(find_ack(7), STATUS_BAD_VERSION);
}

static void test_vreg_clamp(void) {
    CHECK_EQ(pm_charge_vreg_code(4240), 25); CHECK_EQ(pm_charge_vreg_code(4208), 23);
    CHECK_EQ(pm_charge_vreg_code(3000), 0);  CHECK_EQ(pm_charge_vreg_code(5000), 63);
    CHECK_EQ(pm_charge_vreg_clamp(4352, true, 4240), 4240);
    CHECK_EQ(pm_charge_vreg_clamp(4352, true, 4400), 4240);     /* lte_max itself capped */
    CHECK_EQ(pm_charge_vreg_clamp(4352, false, 4240), 4352);
    CHECK_EQ(pm_charge_vreg_clamp(4250, false, 4240), 4240);    /* rounds down to a 16 mV step */
    CHECK_EQ(pm_charge_vreg_clamp(4208, true, 4240), 4208);
    pm_charge_t c; pm_charge_init(&c);
    CHECK(c.lte_present); CHECK_EQ(M.vreg_mV, 4208); CHECK(M.vreg_mV <= PM_VREG_LTE_MAX_MV);
    CHECK(!pm_charge_set_lte(&c, true, 4300)); CHECK(!pm_charge_set_lte(&c, true, 3000));
    c.vreg_req_mV = 4352; CHECK(pm_charge_set_lte(&c, true, 4240)); CHECK_EQ(M.vreg_mV, 4240);
    CHECK(pm_charge_set_lte(&c, false, 4240)); CHECK_EQ(M.vreg_mV, 4352);
}

static void test_app_lte_cfg(void) {
    pm_app_init(BOOT_PWR_BUTTON);
    M.pg = true; M.mute_high = false; pm_app_tick(10);
    uint8_t ok[3] = {1, 4240 & 0xFF, 4240 >> 8}, bad[3] = {1, 4300 & 0xFF, 4300 >> 8};
    send_frame(PM_MSG_LTE_CFG, 9, ok, 3);  CHECK_EQ(find_ack(9), STATUS_OK);
    send_frame(PM_MSG_LTE_CFG, 10, bad, 3); CHECK_EQ(find_ack(10), STATUS_RANGE);
    send_frame(PM_MSG_LTE_CFG, 11, ok, 2); CHECK_EQ(find_ack(11), STATUS_BAD_LEN);
    CHECK(g_app.chg.lte_present); CHECK(g_app.chg.vreg_mV <= 4240);
}

static void test_app_power_fsm(void) {
    pm_app_init(BOOT_POR);
    CHECK(!M.cm5_power);
    M.btn[BTN_VOL_UP] = true; pm_app_tick(1); pm_app_tick(10); CHECK(!M.cm5_power);   /* VOL never wakes */
    M.btn[BTN_VOL_UP] = false; pm_app_tick(20);
    M.btn[BTN_PWR] = true; pm_app_tick(30); pm_app_tick(40);
    CHECK(M.cm5_power); CHECK_EQ(g_app.pstate, PSTATE_S0);
    M.btn[BTN_PWR] = false; pm_app_tick(50);
    M.pg = true; pm_app_tick(60);
    send_frame(PM_MSG_SHUTDOWN_READY, 20, NULL, 0); CHECK_EQ(find_ack(20), STATUS_OK);
    CHECK_EQ(g_app.pstate, PSTATE_S5);
    pm_app_tick(60 + PM_CUT_DELAY_MS - 1); CHECK(M.cm5_power);
    pm_app_tick(60 + PM_CUT_DELAY_MS);     CHECK(!M.cm5_power); CHECK_EQ(g_app.pstate, PSTATE_S4);
    /* POWER held 10 s = hard cut independent of the CM5 */
    M.btn[BTN_PWR] = true; pm_app_tick(20000); pm_app_tick(20010); CHECK(M.cm5_power);
    pm_app_tick(31000); CHECK(!M.cm5_power); CHECK(!M.pa11);
    M.btn[BTN_PWR] = false; pm_app_tick(31100); pm_app_tick(31200);
    M.btn[BTN_PWR] = true; pm_app_tick(32000); pm_app_tick(32010); pm_app_tick(32100);
    CHECK(M.cm5_power);                                                     /* latch consumed */
}

static void test_app_tx_silent_when_cm5_off(void) {
    pm_app_init(BOOT_POR);
    M.btn[BTN_VOL_UP] = true; pm_app_tick(1); pm_app_tick(10);
    CHECK_EQ(M.tx_len, 0); CHECK(!M.irq_low);
}

int main(void) {
    RUN(test_crc_check); RUN(test_vectors_encode); RUN(test_vectors_decode_stream);
    RUN(test_corrupt_and_oversize_dropped); RUN(test_cobs_roundtrip_254);
    RUN(test_boot_pa11_low_and_fail_closed); RUN(test_hold_requires_ptt_and_release_cuts);
    RUN(test_muted_refused_and_mute_edge_cuts); RUN(test_tap_window_single_use); RUN(test_caps_and_timeouts);
    RUN(test_power_down_cuts); RUN(test_charge_hysteresis); RUN(test_vreg_clamp); RUN(test_app_lte_cfg); RUN(test_app_power_fsm); RUN(test_wdt_supervisor);
    RUN(test_buttons_debounce_long); RUN(test_app_mic_enable_flow); RUN(test_app_tx_silent_when_cm5_off);
    printf("\n%d tests, %d checks, %d failures\n", tt_tests, tt_checks, tt_fail);
    return tt_fail ? 1 : 0;
}
