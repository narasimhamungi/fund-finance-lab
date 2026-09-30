# NAV facility stress: Hypothetical buyout fund NAV facility with concentration and diversity covenants (illustrative inputs, not market terms)

*Hypothetical inputs for illustration. Not observed market terms, not advice, and not any rating agency's methodology.*

Units: USD millions

## Position
- Total NAV 1,000.0; eligible NAV 876.0 after concentration limits (excluded 40.0 by the 20% single-asset cap, 84.0 by the top-5 limit); largest asset Asset A at 24.0% of NAV
- Loan 150.0; LTV 17.1% (ok); cash sweep at 20.0%, breach at 25.0%, cure target 15.0%
- Uniform drawdown to reach the sweep level: 14.4%; to reach breach: 31.5%
- Concentration limit: the 5 largest assets count for at most 60% of eligible NAV
- Diversity covenant: fewer than 10 assets with value triggers a cash sweep

## Uniform drawdowns (`nav_uniform_stress.csv`)
| Drawdown | Eligible NAV | LTV | Status | Cure to target |
|---|---|---|---|---|
| 0% | 876.0 | 17.1% | ok | 0.0 |
| 5% | 832.2 | 18.0% | ok | 0.0 |
| 10% | 788.4 | 19.0% | ok | 0.0 |
| 15% | 744.6 | 20.1% | cash sweep | 0.0 |
| 20% | 700.8 | 21.4% | cash sweep | 0.0 |
| 25% | 657.0 | 22.8% | cash sweep | 0.0 |
| 30% | 613.2 | 24.5% | cash sweep | 0.0 |
| 35% | 569.4 | 26.3% | breach | 64.6 |
| 40% | 525.6 | 28.5% | breach | 71.2 |
| 45% | 481.8 | 31.1% | breach | 77.7 |
| 50% | 438.0 | 34.2% | breach | 84.3 |

First grid point in breach: 35.0%.

## Largest assets written down by 100% (`nav_single_name_stress.csv`)
| Assets | Names | Eligible NAV | LTV | Status | Further uniform drawdown to breach |
|---|---|---|---|---|---|
| 1 | Asset A | 676.0 | 22.2% | cash sweep (LTV) | 11.2% |
| 2 | Asset A, Asset B | 516.0 | 29.1% | breach (diversity also failed) | 0.0% |
| 3 | Asset A, Asset B, Asset C | 382.8 | 39.2% | breach (diversity also failed) | 0.0% |

Limits: see docs/limitations.md. Each concentration limit is measured against the aggregate before it is applied; valuation lag, FX and cross-default terms are not modelled.
