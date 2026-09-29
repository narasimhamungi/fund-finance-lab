# Limitations

- **Hypothetical inputs.** The example facilities, portfolios and investor lists are invented for illustration.
  No figure in `examples/` or `outputs/` describes a real fund, lender or market standard.
- **Not a rating or credit opinion**, and not any rating agency's methodology.
- **NAV facility simplifications.** One concentration test (a single-asset cap measured against pre-exclusion NAV);
  no sector, geography or vintage limits; no valuation lag between reported and realisable NAV; no FX; interest,
  PIK and fees are not accrued; the cash sweep is shown as a status, not simulated over time; cure periods and
  cross-default terms are not modelled.
- **Subscription line simplifications.** The per-investor cap is applied once, against the uncapped borrowing base;
  exclusion events are treated as immediate; capital-call timing, investor credit quality and the fund's
  ability to call again after a shortfall are not modelled.
- **Uniform drawdowns** move every asset by the same percentage; real stresses are uneven, which is why the
  largest-asset loss scenarios are shown alongside.
