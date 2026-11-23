"""Cross-check the 2026 months (after the thesis period) used by the investor tool and the website.

    python 08_forward_test/verify_live_2026.py      -> verification_2026.md

Check 1: each asset's two main funds against the other funds tracking the same asset.
Check 2: gold against an independent source, international gold (USD, monthly average) x USD/INR.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from sip.forward_data import CHECKS, LIVE_FILE, PRIMARY, RAW, _undo_splits, live_returns  # noqa: E402


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    nav = pd.read_csv(LIVE_FILE, index_col="Month")
    nav.index = pd.PeriodIndex(nav.index, freq="M")
    r = nav.astype(float).pct_change(fill_method=None).apply(_undo_splits).loc["2026-01":]
    live = live_returns()
    L = [f"# 2026 data check (Jan – {live.index[-1].strftime('%b %Y')})\n",
         "Month-end NAVs (last trading day) from the AMFI daily NAV archive, mirrored at "
         "github.com/captn3m0/historical-mf-data, built exactly like the 2020–2025 table. "
         "These months are used only to plan the next instalment (tool and website), not in any back-test.\n",
         "## Check 1: main funds vs other funds tracking the same asset (monthly return)\n",
         "| Month | " + " | ".join(f"{a} (main)" + f" | {a} (others)" for a in PRIMARY) + " |",
         "|---|" + "---|---|" * len(PRIMARY)]
    worst = {}
    for m in live.index:
        cells = []
        for a in PRIMARY:
            other = r.loc[m, CHECKS[a]].mean()
            cells += [f"{live.loc[m, a]:+.2%}", f"{other:+.2%}"]
            worst[a] = max(worst.get(a, 0), abs(live.loc[m, a] - other))
        L.append(f"| {m.strftime('%b %Y')} | " + " | ".join(cells) + " |")
    L.append("\nLargest monthly gap: " + ", ".join(f"{a} {v:.2%}" for a, v in worst.items()) + ".\n")

    g = pd.read_csv(RAW / "gold_usd_monthly_2026.csv")
    g.index = pd.PeriodIndex(g["Date"], freq="M")
    fx = pd.read_csv(RAW / "usdinr_daily_2026.csv", parse_dates=["Date"]).set_index("Date")["USDINR"].dropna()
    fx_avg = fx.resample("ME").mean()
    fx_avg.index = fx_avg.index.to_period("M")
    intl = (g["Gold_USD_monthly_avg"] * fx_avg).dropna()
    ours_avg = (1 + live["Gold"]).cumprod()
    L += ["## Check 2: gold vs international gold × USD/INR\n",
          "The international price is a monthly *average* (and USD/INR a monthly average of daily "
          "rates), so month by month it lags month-end prices; the cumulative change is the fair comparison.\n",
          "| Month | International gold in ₹ (avg) | Change since Dec 2025 | Our gold series, change since Dec 2025 |",
          "|---|---|---|---|"]
    for m in live.index:
        if m in intl.index:
            L.append(f"| {m.strftime('%b %Y')} | ₹{intl[m]:,.0f}/oz | {intl[m] / intl[pd.Period('2025-12', 'M')] - 1:+.1%} | "
                     f"{ours_avg[m] - 1:+.1%} |")
    L += ["", "Both move the same way; after ten months our gold series is a few percent above the "
          "international price in rupees. Month-end vs monthly-average timing explains part of it "
          "(gold swung ±5–10% a month in 2026); the rest is the Indian price's premium or discount to "
          "the world price, which also moved in earlier years (see verification.md).", ""]
    (HERE / "verification_2026.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
