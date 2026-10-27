#include "pm_wdtsup.h"
#include "pm_hal.h"
void pm_wdtsup_init(pm_wdtsup_t *w) { *w = (pm_wdtsup_t){0}; }
void pm_wdtsup_arm(pm_wdtsup_t *w, uint32_t now, bool armed) { w->armed = armed; w->last_hb = now; }
void pm_wdtsup_heartbeat(pm_wdtsup_t *w, uint32_t now) { w->last_hb = now; }
bool pm_wdtsup_tick(pm_wdtsup_t *w, uint32_t now) {
    if (!w->armed || now - w->last_hb <= PM_HB_TIMEOUT_MS) return false;
    hal_cm5_run_pulse();
    w->last_hb = now;
    w->resets[w->n % 3] = now; w->n++;
    if (w->n >= 3) {
        uint32_t oldest = w->resets[w->n % 3];    /* the 3rd-most-recent reset */
        if (now - oldest <= PM_WDT_WINDOW_MS) w->want_recovery = true;
    }
    return true;
}
