# Subscription line stress: Hypothetical closed-end fund subscription line (illustrative inputs, not market terms)

*Hypothetical inputs for illustration. Not observed market terms, not advice, and not any rating agency's methodology.*

Units: USD millions

## Position
- Facility 300.0; outstanding 180.0; borrowing base 358.8; availability 120.0
- Uncalled commitments 455.0: 2.53x the outstanding loan; a call of 39.6% of uncalled capital repays it
- Largest contributor to the borrowing base: Public pension A (32.6%)

## Scenarios (`subline_scenarios.csv`)
| Scenario | Borrowing base | Mandatory prepayment | Coverage | Call needed |
|---|---|---|---|---|
| base | 358.8 | 0.0 | 2.53x | 39.6% |
| largest contributor excluded (Public pension A) | 241.8 | 0.0 | 2.53x | 39.6% |
| two largest contributors excluded | 154.1 | 25.9 | 2.53x | 39.6% |
| all designated investors excluded | 292.5 | 0.0 | 2.53x | 39.6% |
| largest contributor defaults (Public pension A) | 241.8 | 0.0 | 1.81x | 55.4% |

Limits: see docs/limitations.md. Exclusion events, cure periods and investor-level concentration terms are simplified.
