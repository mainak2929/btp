# Website: Personal SIP Planner

The end point of the thesis: the Personal SIP rule (Strategy 8, [`../11_personal_sip`](../11_personal_sip))
as a one-page tool.

**Inputs:** risk level (aggressive / moderate / conservative), monthly SIP amount, what the three
funds are worth today. Optionally, last month's returns of the three funds, which roll the 120-month
window forward by one month.

**Output:** the target split, how much to buy (or sell) in each fund this month, and the three steps
that produced it.

| File | What it is |
|---|---|
| `index.html` | the page |
| `sip.js` | the engine in JavaScript: target (½ risk parity + ½ max Sharpe, cushion by risk level), smart split, 5% band |
| `data.js` | generated: the latest 120 months of returns (Jan 2016 – Dec 2025), the frozen cushions, the 2020–2025 test results |
| `build.py` | builds `data.js` and `reference.json` from the thesis data |
| `reference.json` | the same targets and trades computed by the Python engine |

`tests/test_sip.py` checks that `sip.js` gives the Python engine's numbers (targets within 1e-6,
trades within ₹0.50) and that `data.js` is the latest window of the thesis data.

Open `index.html` in a browser to use it locally. Months added on the page are kept in that browser only.

Educational output from a back-test model, not investment advice.

## Public site

Hosted with GitHub Pages from the separate public repo `mainak2929/personal-sip-planner`
(https://mainak2929.github.io/personal-sip-planner/). To update it after changing the page or data:

```bash
python website/build.py
python website/export_site.py ../personal-sip-planner    # writes a full HTML page + sip.js + data.js
```

then commit and push that repo.
