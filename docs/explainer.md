# Subscription lines vs NAV loans: a credit explainer

**Prepared by:** Narasimha Mungi, September 2026 · Companion to this repo's models ([spec](model_spec.md))

> Market terms below are cited from public sources and change over time. The figures in this repo's `examples/`
> are hypothetical. Not advice, and not any rating agency's methodology.

## The short version

Both are loans to a fund, but they are secured on different things and fail in different ways.

- **Subscription line (capital call facility):** secured on investors' promises to pay. It is used early in a
  fund's life to bridge capital calls, and it is repaid by calling capital. It fails when investors don't fund.
- **NAV loan:** secured on the value of investments the fund already owns. It is used later, once there is a
  portfolio to lend against, and it is repaid from exits and distributions. It fails when the portfolio loses value.

| | Subscription line | NAV loan |
|---|---|---|
| Collateral | Uncalled capital commitments of the fund's investors (LPs) and the right to call them [1] | Net asset value of the fund's investments, e.g. pledged equity interests and distribution rights [1][6] |
| When used | Investment period, to smooth and delay capital calls [9] | Later in the fund's life, once the portfolio is large and diverse enough [3] |
| How it is sized | Borrowing base: an advance rate times the uncalled commitments of eligible investors [4][5] | Loan-to-value (LTV) cap against eligible NAV, typically low: roughly 5–25% [1] or 5–30% [7] |
| Repaid from | Capital calls | Asset sales, distributions, cash sweeps [6][8] |
| Main credit risk | Investors fail to fund; concentration in a few investors | Portfolio value falls; valuation lag; concentration in a few assets |
| Lender protections | Advance rates, exclusion events, investor concentration limits | Maximum-LTV covenant, cash sweep, diversity covenants, eligibility criteria and haircuts [2][3][8] |

## Subscription lines

**Borrowing base.**
- Lenders sort investors into classes and apply an advance rate to each class's uncalled commitments.
- *Included* investors, usually rated or large institutions, typically get 90%. *Designated* investors, with less
  available financial information, get a lower rate, typically 60% or 65% [4][5].
- A 2024 market survey found the 90%/65% split still the most common. It also found flat-rate structures, which
  include almost all investors at one rate, ranging from 25% to 90%, with most at 60–70% [5].
- A filed example: a 2022 SEC filing for a private credit fund describes exactly this construct, with 90% for
  included and 65% for designated investors [10].

**Exclusion events.**
- Investors drop out of the borrowing base automatically on defined negative events. Losing the required rating is
  a standard one: rated-investor thresholds are often BBB (S&P) or Baa2 (Moody's) [11].
- Exclusion shrinks the borrowing base immediately. If the loan then exceeds the base, the fund must repay the
  difference.

**Concentration.**
- Facilities cap how much of the borrowing base any one investor can support.
- Affiliated investors are treated as one [12].

**How an agency looks at it.** Fitch published Subscription Finance Rating Criteria in June 2023 [13]:
- *Quantitative:* the credit quality and diversification of the investor pool, and modelled losses against the
  facility's overcollateralisation.
- *Qualitative:* the manager, the fund's characteristics and the facility's structural terms. Ratings can be
  capped [14].

## NAV loans

**LTV and eligibility.**
- The loan is sized against the NAV of eligible investments. Assets can be excluded, or haircut, for concentration,
  jurisdiction, sector, leverage or liquidity [8].
- LTV covenants are usually tested on a maintenance basis, with cure mechanics and cash-sweep consequences if a
  threshold is breached [8].
- LTV is typically measured on the manager's own valuations, and the lender has a right to challenge them [15].

**Diversity and concentration.**
- Covenants commonly require a minimum number, or diversity, of portfolio assets. A breach can trigger a 100% cash
  sweep [3].
- *A filed example:* the NAV facility agreement filed by Blackstone Private Equity Strategies Fund (2024):
  - The ten largest eligible investments may count for no more than 55% of adjusted eligible NAV.
  - A cash sweep event occurs on a sweep-LTV breach, an excess-loan event or a minimum-diversity breach [16].

**Life cycle.** LTV tends to fall over a fund's life as assets are sold and residual equity shrinks [6].

## What the models in this repo show, and where they are simpler

With the hypothetical inputs in `examples/` (see [`outputs/`](../outputs/)):

**NAV facility** (loan 150 against NAV 1,000):
- LTV is 15.6% after a 20% single-asset cap.
- A 37.5% uniform fall in NAV reaches the 25% breach level.
- Losing the two largest assets alone pushes LTV into the cash-sweep band.

**Subscription line** (180 drawn):
- The borrowing base is 358.8.
- Uncalled capital covers the loan 2.53x.
- If the largest contributor defaults, coverage falls to 1.81x. Excluding the two largest contributors forces a
  mandatory prepayment of 25.95.

These are directional. Real facilities differ in ways the models do not yet capture:

| Real-facility feature | This repo |
|---|---|
| Top-N concentration limits (e.g. ten largest ≤55% of eligible NAV) [16] | One single-asset cap, measured before exclusions |
| Minimum-diversity covenant, with a cash sweep on breach [3][16] | Not modelled |
| Haircuts by asset type, sector or jurisdiction [8] | Not modelled |
| Uneven, correlated asset declines | Uniform drawdowns plus largest-asset losses |
| Affiliated investors aggregated for concentration [12] | Each investor separate |
| Hurdle mechanics that add investors over time [5] | Static investor list |

**Next model upgrade:** a top-N concentration limit and a diversity covenant. Those are the terms most likely to
bind in a stress, and the filed Blackstone agreement shows how they are drafted.

## Questions an analyst asks

**Subscription line:**
- How concentrated and how creditworthy is the investor pool?
- What do the side letters let investors excuse themselves from?
- Does the partnership agreement let the fund call more from other investors if one defaults?
- Does the facility's term run past the investment period?

**NAV loan:**
- Whose valuations set the LTV, how stale are they, and what challenge rights does the lender have?
- How concentrated is the portfolio in its largest names?
- Where do the sweep and breach levels sit against realistic drawdowns?
- Is the lender secured on the assets, or only on the cash flows?

## Sources

1. Moonfare, *NAV loans: net asset value financing in private equity explained*: https://www.moonfare.com/blog/what-is-nav-lending
2. Mayer Brown, *NAV Credit Facility Primer*: https://www.mayerbrown.com/-/media/nav-credit-facility-primer.pdf?rev=-1
3. Neuberger Berman, *A Perspective on Private Equity NAV Loans*: https://www.nb.com/handlers/documents.ashx?id=da1f212f-183c-4341-85e4-cbdd1e2b41c9&name=Perspective_on_PE_NAV_Loans_Insights_POSTING.pdf
4. Mayer Brown, *Subscription Credit Facilities: A Comparison of Borrowing Base Structures* (2019): https://www.mayerbrown.com/-/media/files/perspectives-events/publications/2019/10/subscription-credit-facilities--a-comparison-of-borrowing-base-structures.pdf
5. Haynes Boone, *Fund Finance Insights: Borrowing Base Constructs in First Half of 2024*: https://www.haynesboone.com/news/alerts/fund-finance-insights-borrowing-base-constructs-in-first-half-of-2024
6. ILPA, *NAV-Based Facilities Guidance for Limited Partners and General Partners* (2024): https://go.ilpa.org/ILPA-Guidance-on-NAV-Facilities
7. Oaktree, *NAV Finance 101*: https://www.oaktreecapital.com/docs/default-source/default-document-library/nav-finance-101.pdf?sfvrsn=6e1e5766_2
8. Ropes & Gray, *NAV facilities in 2026: structuring, governance and market practice considerations for sponsors*: https://www.ropesgray.com/en/insights/viewpoints/102mrf1/nav-facilities-in-2026-structuring-governance-and-market-practice-consideration
9. Loan Market Association, fund finance ratings article: https://www.lma.eu.com/download_file/66667/0
10. NC SLF Inc., Form POS AMI (2022), SEC EDGAR: https://www.sec.gov/Archives/edgar/data/1844684/000162828022027326/ncslfn-2posami1.htm
11. Mondaq, *Subscription Credit Facilities: Understanding Funding Ratios in the Applicable Requirement*: https://www.mondaq.com/unitedstates/fund-finance/1403216/subscription-credit-facilities-understanding-funding-ratios-in-the-applicable-requirement
12. Lafayette Square USA, Inc., Form 8-K exhibit 10.1 (2024), SEC EDGAR: https://www.sec.gov/Archives/edgar/data/1849089/000110465924074554/tm2418111d1_ex10-1.htm
13. Travers Smith, *Rated subscription lines* (Global Legal Insights, Fund Finance 2024): https://traverssmith.com/media/aqlndlke/gli-fund-finance-2024.pdf
14. Fund Finance Association, Fitch subscription finance criteria exposure draft webinar (2023): https://events.fundfinanceassociation.com/events/past-events/03-01-2023-fitch-ratings-webinar
15. Private Capital Solutions, *NAV facilities to private equity and private credit borrowers*: https://www.privatecapitalsolutions.com/insights/nav-facilities-to-private-equity-and-private-credit-borrowers
16. Blackstone Private Equity Strategies Fund L.P., Form 10-Q exhibit 10.1 (2024), SEC EDGAR: https://www.sec.gov/Archives/edgar/data/1930054/000119312524257190/d889278dex101.htm
