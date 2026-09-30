# NAV facility stress: Hypothetical buyout fund NAV facility (illustrative inputs, not market terms)

*Hypothetical inputs for illustration. Not observed market terms, not advice, and not any rating agency's methodology.*

Units: USD millions

## Position
- Total NAV 1,000.0; eligible NAV 960.0 after concentration limits (excluded 40.0 by the 20% single-asset cap); largest asset Asset A at 24.0% of NAV
- Loan 150.0; LTV 15.6% (ok); cash sweep at 20.0%, breach at 25.0%, cure target 15.0%
- Uniform drawdown to reach the sweep level: 21.9%; to reach breach: 37.5%

## Uniform drawdowns (`nav_uniform_stress.csv`)
| Drawdown | Eligible NAV | LTV | Status | Cure to target |
|---|---|---|---|---|
| 0% | 960.0 | 15.6% | ok | 0.0 |
| 5% | 912.0 | 16.4% | ok | 0.0 |
| 10% | 864.0 | 17.4% | ok | 0.0 |
| 15% | 816.0 | 18.4% | ok | 0.0 |
| 20% | 768.0 | 19.5% | ok | 0.0 |
| 25% | 720.0 | 20.8% | cash sweep | 0.0 |
| 30% | 672.0 | 22.3% | cash sweep | 0.0 |
| 35% | 624.0 | 24.0% | cash sweep | 0.0 |
| 40% | 576.0 | 26.0% | breach | 63.6 |
| 45% | 528.0 | 28.4% | breach | 70.8 |
| 50% | 480.0 | 31.2% | breach | 78.0 |

First grid point in breach: 40.0%.

## Largest assets written down by 100% (`nav_single_name_stress.csv`)
| Assets | Names | Eligible NAV | LTV | Status | Further uniform drawdown to breach |
|---|---|---|---|---|---|
| 1 | Asset A | 760.0 | 19.7% | ok | 21.1% |
| 2 | Asset A, Asset B | 610.0 | 24.6% | cash sweep (LTV) | 1.6% |
| 3 | Asset A, Asset B, Asset C | 488.0 | 30.7% | breach | 0.0% |

Limits: see docs/limitations.md. Each concentration limit is measured against the aggregate before it is applied; valuation lag, FX and cross-default terms are not modelled.
