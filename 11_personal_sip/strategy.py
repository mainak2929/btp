"""Strategy 8: Personal SIP (fixed optimiser + a safety cushion set by the investor's risk level).

Two separate decisions (Tobin 1958):
1. How much to keep safe: the Liquid "cushion" L depends on the investor's risk aversion λ.
   For each profile, L was chosen on 2010-2019 data only (select_cushion.py) as the cushion that
   gave the highest utility U = return above Liquid − (λ/2)·variance, then frozen.
2. How to split the rest: exactly as the Fixed Optimized SIP (08_forward_test): Nifty/Gold by
   ½ risk parity + ½ max Sharpe on returns above Liquid, fitted on the previous 120 months.
Same engine: smart instalments, 5% band. REFIT_EVERY = 1 re-fits every month on the latest
120 months (the rolling window: one month in at the head, one out at the tail).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from sip.engine import Strategy  # noqa: E402
from sip.optimize import optimized_cash_buffer, walk_forward_weights  # noqa: E402
from sip.report import LOOKBACK  # noqa: E402

LOWER, UPPER, BAND = 0.10, 0.70, 0.05
PROFILES = {"aggressive": 2.0, "moderate": 4.0, "conservative": 8.0}
CANDIDATE_CUSHIONS = (0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70)
CUSHION_FILE = HERE / "results" / "cushions.json"      # written by select_cushion.py


def cushions() -> dict[str, float]:
    return json.loads(CUSHION_FILE.read_text(encoding="utf-8"))


def name(profile: str, refit_every: int = 1) -> str:
    return f"Personal SIP ({profile}, {'monthly' if refit_every == 1 else 'yearly'} re-fit)"


def target(returns, liquid: float, refit_every: int = 1, lookback: int = LOOKBACK):
    fit = lambda window, lo, hi: optimized_cash_buffer(window, lo, hi, liquid=liquid)  # noqa: E731
    return walk_forward_weights(returns, fit, lookback, reoptimise_every=refit_every,
                                lo=LOWER, hi=UPPER)


def build(returns, profile: str, liquid: float | None = None, refit_every: int = 1,
          lookback: int = LOOKBACK) -> Strategy:
    liquid = cushions()[profile] if liquid is None else liquid
    return Strategy(name(profile, refit_every), target(returns, liquid, refit_every, lookback),
                    contribution="smart", rebalance="band", band=BAND,
                    description=f"Liquid cushion {liquid:.0%} ({profile}); Nifty/Gold by ½ RP + "
                                "½ max Sharpe vs Liquid; smart instalments; 5% band.")
