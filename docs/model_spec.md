# Model specification

Notation: NAV_i = value of asset i; N = Σ NAV_i; L = loan outstanding.

## NAV facility

| Quantity | Formula | Note |
|---|---|---|
| Eligible NAV after single-asset cap | E₁ = Σ min(NAV_i, c × N) | c = single-asset cap; N measured before exclusions |
| Top-N limit (optional) | E = E₁ − max(0, T_N − s × E₁) | T_N = sum of the N largest capped values; s = top-N share; measured against E₁ |
| LTV | L / E | |
| Status | breach if LTV ≥ breach level; cash sweep if LTV ≥ sweep level or the diversity covenant fails; else ok | levels are inputs |
| Diversity covenant (optional) | fails if the number of assets with value < minimum | a failure triggers a cash sweep |
| Uniform drawdown to level ℓ | d* = max(0, 1 − L / (ℓ × E)) | exact: a uniform drawdown scales every NAV_i, N, the cap and the top-N limit, so E scales by (1 − d) |
| Cure to target t | max(0, L − t × E) | paydown (or equity used to repay) that restores LTV = t |
| Single-name stress | write down the k largest assets by loss x, recompute N and E | the cap is recomputed on the smaller portfolio |

## Closed-end fund asset coverage

| Quantity | Formula | Note |
|---|---|---|
| Coverage assets | A = net assets to common + debt + preferred | total assets less liabilities not represented by senior securities |
| Debt coverage | A / D | statutory minimum 300% |
| Total coverage | A / (D + P) | statutory preferred test, minimum 200%; contractual tests (e.g. 225%) are inputs |
| Per-$25 convention | A / P × 25 | as funds report it; not the statutory test |
| Fall in A to level ℓ | 1 − ℓ × S / A | S = D + P (or D for the debt test) |
| Cure by repaying senior securities | R = (ℓ × S − A) / (ℓ − 1) | repaying R lowers A and S together |
| Common distribution capacity | A − max(3 × D, t × S) | t = binding total-coverage level |

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
