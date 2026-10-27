/* CM5 heartbeat supervisor (§11 Watchdog): heartbeat every 5 s; miss > 30 s -> RUN reset;
 * 3 resets in 10 min -> request recovery boot mode. */
#ifndef PM_WDTSUP_H
#define PM_WDTSUP_H
#include <stdbool.h>
#include <stdint.h>
#define PM_HB_TIMEOUT_MS 30000u
#define PM_WDT_WINDOW_MS 600000u
typedef struct { uint32_t last_hb, resets[3]; uint8_t n; bool armed, want_recovery; } pm_wdtsup_t;
void pm_wdtsup_init(pm_wdtsup_t *w);
void pm_wdtsup_arm(pm_wdtsup_t *w, uint32_t now, bool armed);   /* armed only in S0..S2 */
void pm_wdtsup_heartbeat(pm_wdtsup_t *w, uint32_t now);
/* Returns true if the CM5 was reset on this tick. */
bool pm_wdtsup_tick(pm_wdtsup_t *w, uint32_t now);
#endif
