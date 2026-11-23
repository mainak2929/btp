# 11 · Personal SIP (Strategy 8): the end point of the thesis

> **What this folder does:** it turns the study into one rule that depends on the investor. The
> Nifty/Gold split comes from the fixed optimiser (08). How much is kept safe in the liquid fund
> (the **cushion**) depends on the investor's risk level λ. The website ([`../website`](../website))
> runs this rule.

## Why a cushion that depends on λ

In `10_max_utility` the Fixed Optimized SIP had the highest U for every investor, so the tool gave
an aggressive and a conservative investor **the same split**. A risk question whose answer changes
nothing is not much use. Tobin's separation (1958) suggests two separate decisions:

1. **How much to keep safe** → the cushion L, set by λ.
2. **How to split the rest** → the same for everyone: ½ risk parity + ½ max Sharpe (vs Liquid) on
   Nifty and gold, fitted on the last 120 months (`sip/optimize.py`, `optimized_cash_buffer`).

```
target = [ (1−L) × n,  (1−L) × (1−n),  L ]      n = ½ n_riskparity + ½ n_maxSharpe
risk parity (2 assets):  n·σ_Nifty = (1−n)·σ_Gold        max Sharpe: best mean(r − r_Liquid)/σ
each of Nifty and Gold stays within 10%–70% of the whole portfolio
```

Same engine as before: new money fills gaps first, full reset only if a fund drifts more than 5%.
The split is re-fitted **every month** (rolling window: the newest month in, the oldest out).

## Choosing the cushion: 2010–2019 only ([`select_cushion.py`](select_cushion.py))

Candidates 10%, 20%, …, 70%. For each λ, the cushion with the highest U on Feb 2010 – Dec 2019 was
chosen and frozen ([`results/selection_2010_2019.md`](results/selection_2010_2019.md)):

| | U, aggressive (λ=2) | U, moderate (λ=4) | U, conservative (λ=8) |
|---|---|---|---|
| 10% | **1.52%** | 0.68% | −0.99% |
| 30% | 1.31% | **0.80%** | −0.21% |
| 70% | 0.69% | 0.59% | **0.40%** |

**Chosen:** aggressive 10%, moderate 30% (narrowly ahead of 40%), conservative 70%.

## Out-of-sample test: 2020–2025 ([`run.py`](run.py) → [`results/results.md`](results/results.md))

| Investor | Personal SIP: U / XIRR / worst fall | Rank of 11 | Fixed Optimized SIP: U / XIRR / worst fall |
|---|---|---|---|
| Aggressive (10%) | 9.99% / 20.4% / −11.8% | 3 | 10.25% / 20.3% / −12.2% |
| Moderate (30%) | 7.25% / 17.2% / −9.0% | 5 | 9.18% / 20.3% / −12.2% |
| Conservative (70%) | 3.24% / 11.0% / −3.4% | 9 | 7.04% / 20.3% / −12.2% |

**What this shows**

1. **It personalises the advice.** A conservative investor's worst fall drops from −12.2% to −3.4%.
2. **It did not beat the fixed optimiser on U.** The cushions were set on 2010–2019, when gold and
   Nifty earned little above the liquid fund; 2020–2025 rewarded holding them (gold +21%/yr). A
   cushion chosen on one period can be too cautious for the next, which is the same estimation
   problem seen in `10_max_utility`.
3. **Monthly and yearly re-fits give almost the same result**, so the monthly rolling window costs
   nothing and keeps the split current.

## Run

```bash
python 11_personal_sip/select_cushion.py   # 2010-2019: choose and freeze the cushions
python 11_personal_sip/run.py              # 2020-2025: the test
```
