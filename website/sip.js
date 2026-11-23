// Personal SIP engine: the thesis's final rule (Strategy 8), written in JavaScript for the website.
// It mirrors the Python code exactly and is checked against it in tests/test_sip.py:
//   target  -> sip/optimize.py  optimized_cash_buffer   (½ risk parity + ½ max Sharpe vs Liquid)
//   buys    -> sip/engine.py    _smart_split            (fill the gaps first)
//   selling -> sip/engine.py    5% band                 (reset to target only if drift > 5%)
(function (root) {
  "use strict";
  var LOOKBACK = 120, LO = 0.10, HI = 0.70, BAND = 0.05;

  function mean(a) { var s = 0; for (var i = 0; i < a.length; i++) s += a[i]; return s / a.length; }
  function cov(a, b) {             // sample covariance (n - 1), as pandas .cov()
    var ma = mean(a), mb = mean(b), s = 0;
    for (var i = 0; i < a.length; i++) s += (a[i] - ma) * (b[i] - mb);
    return s / (a.length - 1);
  }
  function clip(x, lo, hi) { return Math.min(hi, Math.max(lo, x)); }

  // rows: [[nifty, gold, liquid], ...] monthly returns, oldest first; uses the latest 120.
  // liquid: the safety cushion L. Returns {weights:[n,g,l], parts:{...}} for the explanation.
  function target(rows, liquid) {
    var win = rows.slice(-LOOKBACK);
    var n = win.map(function (r) { return r[0]; }), g = win.map(function (r) { return r[1]; });
    var xn = win.map(function (r) { return r[0] - r[2]; }), xg = win.map(function (r) { return r[1] - r[2]; });
    var vN = cov(n, n), vG = cov(g, g), cNG = cov(n, g);
    var sleeve = 1 - liquid, lo = LO / sleeve, hi = Math.min(HI / sleeve, 1 - LO / sleeve);

    // Risk parity with two assets: equal risk contributions <=> wN·σN = wG·σG
    var sN = Math.sqrt(vN), sG = Math.sqrt(vG);
    var rp = clip(sG / (sN + sG), lo, hi);

    // Max Sharpe on returns above Liquid: best Nifty share in [lo, hi] (grid, then refine)
    var eN = mean(xn), eG = mean(xg);
    function sharpe(w) {
      var m = w * eN + (1 - w) * eG;
      var v = w * w * vN + 2 * w * (1 - w) * cNG + (1 - w) * (1 - w) * vG;
      return m / Math.sqrt(v);
    }
    var best = lo, bestS = -Infinity, steps = 2000, i, w;
    for (i = 0; i <= steps; i++) { w = lo + (hi - lo) * i / steps; if (sharpe(w) > bestS) { bestS = sharpe(w); best = w; } }
    var a = Math.max(lo, best - (hi - lo) / steps), b = Math.min(hi, best + (hi - lo) / steps);
    for (i = 0; i < 100; i++) {   // golden-section search on the bracket
      var c1 = b - (b - a) * 0.618034, c2 = a + (b - a) * 0.618034;
      if (sharpe(c1) > sharpe(c2)) b = c2; else a = c1;
    }
    var ms = (a + b) / 2;

    var nShare = 0.5 * rp + 0.5 * ms;
    return {
      weights: [sleeve * nShare, sleeve * (1 - nShare), liquid],
      parts: { riskParityNifty: rp, maxSharpeNifty: ms, sleeve: sleeve,
               volNifty: sN * Math.sqrt(12), volGold: sG * Math.sqrt(12),
               aboveLiquidNifty: eN * 12, aboveLiquidGold: eG * 12 }
    };
  }

  // This month's instruction. holdings and amount in rupees.
  function plan(holdings, amount, w) {
    var h = holdings.slice(), total = h[0] + h[1] + h[2] + amount, gap = [], need = 0, k;
    for (k = 0; k < 3; k++) { gap[k] = Math.max(w[k] * total - h[k], 0); need += gap[k]; }
    var buy = [];
    for (k = 0; k < 3; k++) {
      if (need <= 1e-12) buy[k] = w[k] * amount;
      else if (need >= amount) buy[k] = gap[k] / need * amount;
      else buy[k] = gap[k] + w[k] * (amount - need);
    }
    var after = [h[0] + buy[0], h[1] + buy[1], h[2] + buy[2]];
    var sum = after[0] + after[1] + after[2], drift = 0;
    for (k = 0; k < 3; k++) drift = Math.max(drift, Math.abs(after[k] / sum - w[k]));
    var rebalance = drift > BAND;
    var trade = rebalance ? [w[0] * sum - h[0], w[1] * sum - h[1], w[2] * sum - h[2]] : buy;
    return { buy: buy, drift: drift, rebalance: rebalance, trade: trade, total: sum };
  }

  var api = { target: target, plan: plan, LOOKBACK: LOOKBACK, BAND: BAND };
  if (typeof module !== "undefined" && module.exports) module.exports = api; else root.SIP = api;
})(this);
