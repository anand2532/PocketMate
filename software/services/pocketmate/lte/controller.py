"""Turns LteGovernor decisions (from pm-power) into modem actions (§19.5). Pure: returns an action list,
the pm-lte service executes it. Idempotent: only state changes produce actions."""
from __future__ import annotations

from dataclasses import dataclass, field

from .quectel import AIRPLANE_OFF, AIRPLANE_ON, RAT_CMD

THROTTLE_RATE = "1mbit"     # [impl] tc tbf cap on the wwan interface while throttled; tune on hardware


@dataclass
class LteController:
    cfun_on: bool | None = None
    rat: str | None = None
    shaped: bool | None = None
    powered: bool = True
    log: list[tuple] = field(default_factory=list)

    def apply(self, d: dict) -> list[tuple]:
        """d = pm-power `lte_governor` reply: {tx, rat, throttled, reasons}."""
        acts: list[tuple] = []
        tx = d.get("tx", "block")
        if tx == "shutdown":
            if self.powered:
                acts.append(("power", "off"))      # pm-lte-power off: AT+QPOWD=1, wait, PWR_EN low
                self.powered, self.cfun_on, self.rat, self.shaped = False, None, None, None
            return acts
        if not self.powered:
            acts.append(("power", "on"))
            self.powered = True
            acts.append(("init",))                 # re-run the module profile after power-on
        want_cfun = tx in ("allow", "throttle")
        if want_cfun != self.cfun_on:
            acts.append(("at", AIRPLANE_OFF if want_cfun else AIRPLANE_ON))
            self.cfun_on = want_cfun
        rat = d.get("rat", "lte")
        if want_cfun and rat != self.rat and rat in RAT_CMD:
            acts.append(("at", RAT_CMD[rat]))
            self.rat = rat
        shaped = tx == "throttle"
        if shaped != self.shaped:
            acts.append(("shape", THROTTLE_RATE if shaped else None))
            self.shaped = shaped
        self.log += acts
        return acts
