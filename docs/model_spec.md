# Model specification

Notation: NAV_i = value of asset i; N = Σ NAV_i; L = loan outstanding.

## NAV facility

| Quantity | Formula | Note |
|---|---|---|
| Eligible NAV | E = Σ min(NAV_i, c × N) | c = single-asset cap; N measured before exclusions |
| LTV | L / E | |
| Status | breach if LTV ≥ breach level; cash sweep if LTV ≥ sweep level; else ok | levels are inputs |
| Uniform drawdown to level ℓ | d* = max(0, 1 − L / (ℓ × E)) | exact: a uniform drawdown scales every NAV_i and N, so E scales by (1 − d) |
| Cure to target t | max(0, L − t × E) | paydown (or equity used to repay) that restores LTV = t |
| Single-name stress | write down the k largest assets by loss x, recompute N and E | the cap is recomputed on the smaller portfolio |

## Subscription line

| Quantity | Formula | Note |
|---|---|---|
| Uncalled commitment | U_j = commitment_j × (1 − called_j) | |
| Borrowing base | B = Σ a(category_j) × U_j, optionally capped per investor at p × B_uncapped | a = advance rate by category |
| Capacity | min(facility size, B) | |
| Availability | max(0, capacity − L) | |
| Mandatory prepayment | max(0, L − capacity) | |
| Coverage | Σ U_j / L | investors still obliged to fund calls, including excluded ones |
| Call needed | L / Σ U_j | share of uncalled capital a call must raise to repay the loan |
| Exclusion | investor's advance rate set to 0; still counts in coverage | e.g. an exclusion event under the facility |
| Default | investor removed from the borrowing base and from coverage | it no longer funds calls |
