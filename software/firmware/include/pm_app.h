/* Application glue: link dispatch (ACK/NAK within 50 ms), event emission, module wiring (§11/§12). */
#ifndef PM_APP_H
#define PM_APP_H
#include <stdbool.h>
#include <stdint.h>
#include "pm_buttons.h"
#include "pm_charge.h"
#include "pm_frame.h"
#include "pm_privacy.h"
#include "pm_wdtsup.h"

#define PM_MCU_FW_VER 0x00000400u   /* 0.4.0 */

typedef struct {
    pm_deframer_t rx;
    pm_privacy_t priv;
    pm_buttons_t btn;
    pm_charge_t chg;
    pm_wdtsup_t wdt;
    uint8_t tx_seq, boot_reason, boot_mode, pstate;
    uint32_t wake_epoch, epoch_base, epoch_at_ms;
    uint32_t events_sent, nak_count;
    bool cm5_on, cm5_cmd, cut_pending;
    uint32_t cut_at_ms;
} pm_app_t;
#define PM_CUT_DELAY_MS 10000u   /* S5: no CM5_3V3 sense pin, so cut 10 s after SHUTDOWN_READY [impl] */

extern pm_app_t g_app;
void pm_app_init(uint8_t boot_reason);
void pm_app_rx_byte(uint8_t b);
void pm_app_tick(uint32_t now_ms);
void pm_app_set_cm5_power_good(bool pg);
void pm_app_mute_edge(bool high);
#endif
