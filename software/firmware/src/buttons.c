#include "pm_buttons.h"
#include <string.h>
void pm_buttons_init(pm_buttons_t *b, pm_btn_cb cb) { memset(b, 0, sizeof *b); b->cb = cb; }
void pm_buttons_sample(pm_buttons_t *b, uint8_t id, bool down, uint32_t now) {
    if (id >= PM_BTN_N || b->raw[id] == down) return;
    b->raw[id] = down; b->changed_at[id] = now;
}
void pm_buttons_tick(pm_buttons_t *b, uint32_t now) {
    for (uint8_t i = 0; i < PM_BTN_N; i++) {
        if (b->raw[i] != b->stable[i] && now - b->changed_at[i] >= PM_DEBOUNCE_MS) {
            b->stable[i] = b->raw[i];
            if (b->stable[i]) { b->down_at[i] = now; b->long_sent[i] = false; b->cb(i, BTNACT_DOWN, now); }
            else {
                b->cb(i, BTNACT_UP, now);
                if (!b->long_sent[i]) b->cb(i, BTNACT_SHORT, now);
            }
        }
        if (b->stable[i] && !b->long_sent[i] && now - b->down_at[i] >= PM_LONG_MS) {
            b->long_sent[i] = true; b->cb(i, BTNACT_LONG, now);
        }
        if (i == BTN_PWR && b->stable[i] && now - b->down_at[i] >= PM_VERY_LONG_MS) b->hard_cut = true;
    }
}
