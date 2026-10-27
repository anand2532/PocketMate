/* Debounce + press classification (§12 buttons). 5 ms debounce, long press 2 s, very long 10 s (hard cut). */
#ifndef PM_BUTTONS_H
#define PM_BUTTONS_H
#include <stdbool.h>
#include <stdint.h>
#include "pm_proto_gen.h"
#define PM_BTN_N 4u
#define PM_DEBOUNCE_MS 5u
#define PM_LONG_MS 2000u
#define PM_VERY_LONG_MS 10000u
typedef void (*pm_btn_cb)(uint8_t id, pm_btnact_t act, uint32_t t_ms);
typedef struct {
    bool raw[PM_BTN_N], stable[PM_BTN_N], long_sent[PM_BTN_N];
    uint32_t changed_at[PM_BTN_N], down_at[PM_BTN_N];
    pm_btn_cb cb;
    bool hard_cut;     /* POWER held 10 s: power_fsm cuts power independent of the CM5 */
} pm_buttons_t;
void pm_buttons_init(pm_buttons_t *b, pm_btn_cb cb);
void pm_buttons_sample(pm_buttons_t *b, uint8_t id, bool down, uint32_t now);
void pm_buttons_tick(pm_buttons_t *b, uint32_t now);
#endif
