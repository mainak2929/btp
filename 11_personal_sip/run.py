"""Step 11b: test the Personal SIP on 2020-2025 (data never used to choose its cushions).

    python 11_personal_sip/run.py      -> results/results.md, results/personal_2020_2025.csv

For each profile, U on Jan 2020 - Dec 2025 for: the Personal SIP (monthly and yearly re-fit) and
every earlier strategy (01-06, 08's Fixed Optimized, 10's Max-Utility for that λ).
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "08_forward_test"))

import strategy as s8  # noqa: E402
from run_forward import all_strategies  # noqa: E402
from sip.engine import contribution_schedule, run_sip  # noqa: E402
from sip.forward_data import read_combined  # noqa: E402
from sip.metrics import max_drawdown, sip_xirr, utility_score  # noqa: E402
from sip.report import AMOUNT, COST_BPS, LOOKBACK  # noqa: E402

sys.path.insert(0, str(ROOT / "10_max_utility"))
import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location("s7", ROOT / "10_max_utility" / "strategy.py")
s7 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(s7)

OUT = HERE / "results"


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    R = read_combined()
    idx = R.loc["2020-01":"2025-12"].index
    contrib = contribution_schedule(idx, AMOUNT)
    cush = s8.cushions()
    base = all_strategies(R)
    rows = []
    L = ["# Personal SIP: out-of-sample test, Jan 2020 – Dec 2025\n",
         f"Cushions chosen on 2010-2019 only: " + ", ".join(f"{p} {c:.0%}" for p, c in cush.items()) + ".\n"]
    for profile, lam in s8.PROFILES.items():
        cands = base + [s7.build(R, lam, LOOKBACK),
                        s8.build(R, profile, refit_every=1), s8.build(R, profile, refit_every=12)]
        t = []
        for st in cands:
            res = run_sip(R, st, contrib, COST_BPS)
            tw = res.twr
            t.append({"Strategy": st.name, "U": utility_score(res, R["Liquid"], lam),
                      "Return above Liquid": float((tw - R["Liquid"].reindex(tw.index)).mean() * 12),
                      "Volatility": float(tw.std() * np.sqrt(12)), "XIRR": sip_xirr(res),
                      "Worst fall": max_drawdown((1 + tw).cumprod()),
                      "Final value": float(res.total.iloc[-1])})
        t = pd.DataFrame(t).set_index("Strategy").sort_values("U", ascending=False)
        t.insert(0, "Rank", range(1, len(t) + 1))
        mine = t.loc[s8.name(profile, 1)]
        rows.append({"Profile": profile, "λ": lam, "Cushion": cush[profile],
                     "Personal SIP rank (of 11)": int(mine["Rank"]), "Personal SIP U": mine["U"],
                     "Personal SIP XIRR": mine["XIRR"], "Personal SIP worst fall": mine["Worst fall"],
                     "Best strategy": t.index[0], "Best U": t["U"].iloc[0]})
        shown = t.copy()
        for c in shown.columns[1:]:
            shown[c] = shown[c].map((lambda v: f"₹{v:,.0f}") if c == "Final value" else (lambda v: f"{v:.2%}"))
        L += [f"## {profile.capitalize()} (λ = {lam:g}, cushion {cush[profile]:.0%})\n", shown.to_markdown(), ""]
    S = pd.DataFrame(rows).set_index("Profile")
    S.to_csv(OUT / "personal_2020_2025.csv")
    L = L[:2] + ["## Summary\n", S.to_markdown(floatfmt=".4f"), ""] + L[2:]
    (OUT / "results.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
