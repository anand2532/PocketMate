/* JEITA firmware layer (§12 charge_ctrl): charge only within 10..40 °C, re-enable at 12..38 °C,
 * derate above 35 °C, sensor disagreement > 10 K or NTC fault -> disabled. Values in deci-°C. */
#ifndef PM_CHARGE_H
#define PM_CHARGE_H
#include <stdbool.h>
#include <stdint.h>
typedef struct { int16_t cold_off, cold_on, hot_on, hot_off, derate; } pm_charge_cfg_t;
typedef enum { CHG_OK = 0, CHG_INHIBIT_COLD = 1, CHG_INHIBIT_HOT = 2, CHG_INHIBIT_FAULT = 3 } pm_charge_reason_t;
typedef struct { pm_charge_cfg_t cfg; bool enabled, derated; pm_charge_reason_t reason;
                 bool lte_present; uint16_t vreg_req_mV, vreg_mV; } pm_charge_t;
/* BQ25895 REG06 VREG = 3840 mV + 16 mV * code (datasheet SLUSC88). Default 4208 mV (code 23).
 * With the LTE board fitted VREG must stay <= 4240 mV (hardware/power-config.md, code 25).
 * The MCU assumes lte_present = true until pm-power says otherwise (fail-safe). */
#define PM_VREG_MIN_MV      3840u
#define PM_VREG_DEFAULT_MV  4208u
#define PM_VREG_LTE_MAX_MV  4240u
uint16_t pm_charge_vreg_clamp(uint16_t requested_mV, bool lte_present, uint16_t lte_max_mV);
uint8_t  pm_charge_vreg_code(uint16_t mV);              /* floor((mV-3840)/16), saturating 0..63 */
/* LTE_CFG handler: returns false (-> STATUS_RANGE) if lte_max_mV is outside 3840..4240. */
bool     pm_charge_set_lte(pm_charge_t *c, bool present, uint16_t lte_max_mV);
void pm_charge_init(pm_charge_t *c);
bool pm_charge_cfg_valid(const pm_charge_cfg_t *cfg);   /* bounds 0..45 °C, ordered */
/* Returns true if the enable/inhibit decision changed (caller sends EVT_CHARGE_INHIBIT). */
bool pm_charge_update(pm_charge_t *c, int16_t tspct_dC, int16_t gauge_dC, bool ntc_fault);
#endif
