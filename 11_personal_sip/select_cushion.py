"""Step 11a: choose each profile's Liquid cushion using 2010-2019 ONLY, then freeze it.

    python 11_personal_sip/select_cushion.py   -> results/cushions.json, results/selection_2010_2019.md

For every profile (λ = 2, 4, 8) and every candidate cushion (10% ... 70%) the Personal SIP is
run on Feb 2010 - Dec 2019 (monthly re-fit) and scored with U = return above Liquid − (λ/2)·variance.
Rule fixed in advance: the cushion with the highest U is that profile's cushion.
"""

import json
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))

import strategy as s8  # noqa: E402
from sip.data import read_returns_table  # noqa: E402
from sip.engine import contribution_schedule, run_sip  # noqa: E402
from sip.metrics import utility_score  # noqa: E402
from sip.report import AMOUNT, COST_BPS, sip_months  # noqa: E402

R = read_returns_table()                       # Feb 2000 - Dec 2019 only
assert str(R.index[-1]) == "2019-12"
idx = sip_months(R)
contrib = contribution_schedule(idx, AMOUNT)

results = {}
for L in s8.CANDIDATE_CUSHIONS:
    res = run_sip(R, s8.build(R, "moderate", liquid=L, refit_every=1), contrib, COST_BPS)
    results[L] = {p: utility_score(res, R["Liquid"], lam) for p, lam in s8.PROFILES.items()}
table = pd.DataFrame(results).T            # rows: cushion, columns: profile
chosen = {p: float(table[p].idxmax()) for p in s8.PROFILES}

(HERE / "results").mkdir(exist_ok=True)
s8.CUSHION_FILE.write_text(json.dumps(chosen, indent=2) + "\n", encoding="utf-8")
shown = table.copy()
shown.index = [f"{L:.0%}" for L in shown.index]
shown.columns = [f"U, {p} (λ={s8.PROFILES[p]:g})" for p in shown.columns]
lines = ["# Choosing the safety cushion for each investor (2010-2019 data only)\n",
         "Each row: the Personal SIP with that Liquid cushion, Feb 2010 - Dec 2019, re-fitted monthly. "
         "Rule fixed in advance: highest U for each profile.\n",
         shown.map(lambda v: f"{v:.2%}").to_markdown(), "",
         "**Chosen (frozen):** " + ", ".join(f"{p} {L:.0%}" for p, L in chosen.items())]
(HERE / "results" / "selection_2010_2019.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\n".join(lines))
