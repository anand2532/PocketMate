#include "pm_privacy.h"
#include "pm_hal.h"

static void rail_off(pm_privacy_t *p, pm_railreason_t why) {
    if (!p->mic_pwr_en) return;
    p->mic_pwr_en = false;
    hal_mic_pwr_en(false);
    if (p->rail_cb) p->rail_cb(false, why, p->session_id);
}

void pm_privacy_boot(pm_privacy_t *p, pm_rail_cb cb) {
    hal_mic_pwr_en(false);
    *p = (pm_privacy_t){0};
    p->muted_pin = true;            /* fail closed until the first valid read */
    p->rail_cb = cb;
    if (cb) cb(false, RAILREASON_RESET, 0);
}

bool pm_privacy_mute_valid(const pm_privacy_t *p) { return p->power_good; }  /* pull-up is on CM5_3V3 */

void pm_privacy_on_frame_rx(pm_privacy_t *p) { p->last_rx_ms = p->now_ms; }
void pm_privacy_on_heartbeat(pm_privacy_t *p) { p->last_hb_ms = p->last_rx_ms = p->now_ms; }

void pm_privacy_on_action(pm_privacy_t *p, bool down) {
    p->action_held = down;
    if (down) { p->have_press = true; p->last_press_ms = p->now_ms; }
    else if (p->mic_pwr_en && p->mode == MICMODE_HOLD) rail_off(p, RAILREASON_RELEASE);
}

void pm_privacy_on_mute_pin(pm_privacy_t *p, bool high) {
    p->muted_pin = high;
    if (high) rail_off(p, RAILREASON_MUTE);
}

void pm_privacy_on_power_good(pm_privacy_t *p, bool pg) {
    p->power_good = pg;
    if (!pg) rail_off(p, RAILREASON_POWER_DOWN);
}

void pm_privacy_force_off(pm_privacy_t *p, pm_railreason_t why) { rail_off(p, why); }

pm_status_t pm_privacy_mic_enable(pm_privacy_t *p, bool on, uint16_t sid, uint8_t mode, uint16_t max_s) {
    pm_privacy_on_frame_rx(p);
    if (!on) { rail_off(p, RAILREASON_OFF_CMD); return STATUS_OK; }
    if (!pm_privacy_mute_valid(p)) return STATUS_MUTE_INVALID;
    if (p->muted_pin) return STATUS_MUTED;
    if (!p->power_good) return STATUS_NOT_POWER_GOOD;
    if (mode > MICMODE_DICTATION) return STATUS_RANGE;
    uint16_t cap = (mode == MICMODE_DICTATION) ? PM_CAP_DICTATION_S : PM_CAP_HOLD_S;
    if (max_s == 0) max_s = cap;
    if (max_s > cap) return STATUS_RANGE;
    if (mode == MICMODE_HOLD) {
        if (!p->action_held) return STATUS_NO_PTT;
    } else {
        if (!p->have_press || (uint32_t)(p->now_ms - p->last_press_ms) > PM_TAP_WINDOW_MS) return STATUS_NO_PTT;
        p->have_press = false;      /* one press -> at most one tap session */
    }
    p->session_id = sid; p->mode = mode;
    p->deadline_ms = p->now_ms + (uint32_t)max_s * 1000u;
    if (!p->mic_pwr_en) {
        p->mic_pwr_en = true;
        hal_mic_pwr_en(true);
        if (p->rail_cb) p->rail_cb(true, RAILREASON_REQUEST, sid);
    }
    return STATUS_OK;
}

void pm_privacy_tick(pm_privacy_t *p, uint32_t now) {
    p->now_ms = now;
    if (!p->mic_pwr_en) return;
    if (p->muted_pin || !pm_privacy_mute_valid(p)) rail_off(p, RAILREASON_MUTE);
    else if ((int32_t)(now - p->deadline_ms) >= 0) rail_off(p, RAILREASON_TIMEOUT);
    else if (now - p->last_rx_ms > PM_LINK_LOSS_MS) rail_off(p, RAILREASON_LINK_LOSS);
    else if (now - p->last_hb_ms > PM_HEARTBEAT_LOSS_MS) rail_off(p, RAILREASON_LINK_LOSS);
}
