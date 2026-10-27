#include "pm_charge.h"
#include "pm_hal.h"

static const pm_charge_cfg_t DEFAULTS = {100, 120, 380, 400, 350};

void pm_charge_init(pm_charge_t *c) {
    c->cfg = DEFAULTS; c->enabled = false; c->derated = false; c->reason = CHG_INHIBIT_FAULT;  /* until first read */
    hal_charger_enable(false);
    c->lte_present = true; c->vreg_req_mV = PM_VREG_DEFAULT_MV;
    c->vreg_mV = pm_charge_vreg_clamp(c->vreg_req_mV, true, PM_VREG_LTE_MAX_MV);
    hal_charger_vreg_mV(c->vreg_mV);
}

uint16_t pm_charge_vreg_clamp(uint16_t req, bool lte, uint16_t lte_max) {
    if (lte_max > PM_VREG_LTE_MAX_MV) lte_max = PM_VREG_LTE_MAX_MV;
    if (req < PM_VREG_MIN_MV) req = PM_VREG_MIN_MV;
    if (lte && req > lte_max) req = lte_max;
    return (uint16_t)(PM_VREG_MIN_MV + 16u * pm_charge_vreg_code(req));   /* round down to a real step */
}

uint8_t pm_charge_vreg_code(uint16_t mV) {
    if (mV <= PM_VREG_MIN_MV) return 0;
    uint32_t code = (uint32_t)(mV - PM_VREG_MIN_MV) / 16u;
    return (uint8_t)(code > 63u ? 63u : code);
}

bool pm_charge_set_lte(pm_charge_t *c, bool present, uint16_t lte_max) {
    if (lte_max < PM_VREG_MIN_MV || lte_max > PM_VREG_LTE_MAX_MV) return false;
    c->lte_present = present;
    uint16_t v = pm_charge_vreg_clamp(c->vreg_req_mV, present, lte_max);
    if (v != c->vreg_mV) { c->vreg_mV = v; hal_charger_vreg_mV(v); }
    return true;
}

bool pm_charge_cfg_valid(const pm_charge_cfg_t *g) {
    return g->cold_off >= 0 && g->hot_off <= 450 && g->cold_off < g->cold_on && g->cold_on < g->derate &&
           g->derate <= g->hot_on && g->hot_on < g->hot_off;
}

bool pm_charge_update(pm_charge_t *c, int16_t t, int16_t gauge, bool fault) {
    bool was = c->enabled;
    int d = t - gauge; if (d < 0) d = -d;
    if (fault || d > 100) { c->enabled = false; c->reason = CHG_INHIBIT_FAULT; }
    else if (t < c->cfg.cold_off) { c->enabled = false; c->reason = CHG_INHIBIT_COLD; }
    else if (t > c->cfg.hot_off) { c->enabled = false; c->reason = CHG_INHIBIT_HOT; }
    else if (!c->enabled) {
        if (t >= c->cfg.cold_on && t <= c->cfg.hot_on) { c->enabled = true; c->reason = CHG_OK; }
    }
    c->derated = c->enabled && t > c->cfg.derate;
    if (was != c->enabled) hal_charger_enable(c->enabled);
    return was != c->enabled;
}
