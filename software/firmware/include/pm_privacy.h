/* Microphone power interlock (§8.2, §12 `privacy`). Mirrors services/pocketmate/mcu/privacy_model.py;
 * test/test_privacy.c runs the same scenarios as services/tests/test_privacy_model.py. */
#ifndef PM_PRIVACY_H
#define PM_PRIVACY_H
#include <stdbool.h>
#include <stdint.h>
#include "pm_proto_gen.h"

#define PM_TAP_WINDOW_MS 1000u
#define PM_CAP_HOLD_S 120u
#define PM_CAP_DICTATION_S 600u
#define PM_LINK_LOSS_MS 2000u
#define PM_HEARTBEAT_LOSS_MS 30000u

typedef void (*pm_rail_cb)(bool on, pm_railreason_t reason, uint16_t session_id);

typedef struct {
    uint32_t now_ms;
    bool mic_pwr_en, action_held, have_press, power_good, muted_pin;
    uint32_t last_press_ms, deadline_ms, last_rx_ms, last_hb_ms;
    uint16_t session_id;
    uint8_t mode;
    pm_rail_cb rail_cb;
} pm_privacy_t;

void pm_privacy_boot(pm_privacy_t *p, pm_rail_cb cb);   /* PA11 low before anything else */
bool pm_privacy_mute_valid(const pm_privacy_t *p);
void pm_privacy_on_frame_rx(pm_privacy_t *p);
void pm_privacy_on_heartbeat(pm_privacy_t *p);
void pm_privacy_on_action(pm_privacy_t *p, bool down);
void pm_privacy_on_mute_pin(pm_privacy_t *p, bool high);
void pm_privacy_on_power_good(pm_privacy_t *p, bool pg);
void pm_privacy_force_off(pm_privacy_t *p, pm_railreason_t why);   /* SHUTDOWN_READY, RUN reset, WDT */
pm_status_t pm_privacy_mic_enable(pm_privacy_t *p, bool on, uint16_t sid, uint8_t mode, uint16_t max_s);
void pm_privacy_tick(pm_privacy_t *p, uint32_t now_ms);
#endif
