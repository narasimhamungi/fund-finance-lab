# Leveraged closed-end fund: asset-coverage tests, preferred-share covenants and remedies

**Case:** Calamos Strategic Total Return Fund (NASDAQ: CSQ) · **Prepared by:** Narasimha Mungi, September 2026

> Independent review of public documents. Not legal advice, not a credit rating and not any rating agency's
> methodology. The EDGAR filings below are HTML documents without stable page numbers, so references are to the
> section named. Figures are as filed; the calculator in this repo reproduces the reported ones.

## Why this fund

CSQ has both kinds of senior security a leveraged closed-end fund can carry: borrowings under a bank liquidity
agreement, and Mandatory Redeemable Preferred Shares (MRPS). In September 2026, CEF Connect showed $1,090.0m of debt
and $322.2m of preferred, 27.9% effective leverage [G].

## Sources

| Ref | Document |
|---|---|
| A | Investment Company Act of 1940, section 18, as summarised in SEC releases [IC-34084](https://www.sec.gov/files/rules/final/2020/ic-34084.pdf) (2020) and [IC-28721](https://www.sec.gov/files/rules/ic/2009/ic-28721.pdf) (2009) |
| B | CSQ prospectus supplement, Form 424B3, 2022, section on MRP Shares: [EDGAR](https://www.sec.gov/Archives/edgar/data/1275214/000110465922104686/tm2226808d1_424b3.htm) |
| C | CSQ Form N-CSR/A, fiscal year to 31 Oct 2021, Financial Highlights: [EDGAR](https://www.sec.gov/Archives/edgar/data/1275214/000110465922068612/tm2217714d3_ncsra.htm) |
| D | CSQ Form N-CSR, fiscal year to 31 Oct 2025, leverage risk disclosures: [EDGAR](https://www.sec.gov/Archives/edgar/data/1275214/000110465925124683/tm2532074d5_ncsr.htm) |
| E | CSQ Form N-CSRS, six months to 30 Apr 2026, Financial Highlights: [EDGAR](https://www.sec.gov/Archives/edgar/data/1275214/000110465926080392/tm2610083d4_ncsrs.htm) |
| F | KBRA rating action on CSQ's MRPS, 2026: [KBRA](https://www.kbra.com/publications/QYqTXFPW/kbra-assigns-and-affirms-ratings-for-mandatory-redeemable-preferred-shares-issued-by-calamos-strategic-total-return-fund?format=web) |
| G | CEF Connect fund page for CSQ, data as of 21 Sep 2026: [CEF Connect](https://www.cefconnect.com/fund/CSQ) |

## The tests and what happens on failure

| Test | Level | When tested | Ref | Consequence of failure |
|---|---|---|---|---|
| Debt coverage: coverage assets ÷ debt, s.18(a)(1)(A) | At least 300% | Immediately after issuing or incurring debt | A | Cannot add debt |
| Common distributions, debt test, s.18(a)(1)(B) | 300% after the distribution | At declaration | A | Common distributions barred |
| Preferred dividends, s.18(a)(1)(B) | Debt coverage of at least 200% | At declaration | A | Preferred dividends barred |
| Total coverage: coverage assets ÷ (debt + preferred), s.18(a)(2)(A) | At least 200% | Immediately after issuing preferred | A | Cannot issue preferred |
| Common distributions, preferred test, s.18(a)(2)(B) | 200% after the distribution | At declaration | A | Common distributions barred |
| **MRPS Asset Coverage Test** | At least 225%, on the s.18(h) basis, covering all senior securities | **Monthly** | B | **Mandatory redemption** of MRPS, subject to cure periods |
| **MRPS Overcollateralization Test** | Set in the MRPS terms (parameters not reviewed here) | **Weekly** | B | **Mandatory redemption** of MRPS, subject to cure periods |
| MRPS distribution covenant | Total coverage above 225% | At declaration | F | Common distributions prohibited |
| Preferred rating and other covenants | Maintain the rating on the preferred | Ongoing | D | The fund may be required to redeem some or all of the preferred |
| Term redemption | Fixed date per series, e.g. Series C on 6 Sep 2027 | Scheduled | B | Refinancing need |

"Coverage assets" means total assets less liabilities not represented by senior securities. That equals net assets
to common shareholders plus debt plus preferred at liquidation value.

**The contractual tests are the binding ones.** The statute sets 200% for preferred and tests it at issuance and at
declaration. The MRPS terms raise the level to 225%, test it monthly, and add a weekly overcollateralisation test.
Their remedy is forced redemption, not just a dividend block. The fund's own disclosures warn that it may be forced
to redeem preferred shares to meet regulatory and asset-coverage requirements, at a time that may be unfavourable [D].

## The numbers, and a reporting convention to watch

For FY2021 [C], the calculator in this repo reproduces the fund's reported figures from its financial highlights:

| Measure | Reported | This repo |
|---|---|---|
| Coverage per $1,000 of loan | $4,673 | 4,673.3 |
| Coverage per $25 MRPS | $338 | 338.2 |
| **Total coverage, debt + preferred (the statutory preferred test)** | not reported | **347.3%** |

- The fund's footnote defines the per-$25 figure as coverage assets divided by the MRPS outstanding alone [C].
- Read as a ratio, $338 per $25 is 13.5x. The statutory and contractual preferred tests divide by debt plus preferred,
  which gave 347% at the same date.
- **An analyst who reads the per-share line as the preferred test overstates the cushion roughly fourfold.** The
  ratio that governs redemption is the total-coverage figure.
- The same convention runs through the 2026 semi-annual report: $323.0m of MRPS at $379 per $25 [E]. So the
  total-coverage figure has to be computed, or taken from a source that states it.

**Current cushion:**
- KBRA reports total asset coverage of 342.3% at 30 June 2026, up from 332.3% at 31 July 2025 [F].
- With senior securities unchanged, coverage assets could fall 34.3% before reaching the 225% MRPS test, and 41.6%
  before the 200% statutory level: 1 − 2.25 ÷ 3.423 and 1 − 2.00 ÷ 3.423.
- KBRA also reports a proposed issuance that takes pro-forma coverage to 322.6% [F]. That reduces the room to the
  225% test to 30.3%.

**Cure arithmetic.** Repaying senior securities out of assets lowers both sides of the ratio. Restoring coverage
level T requires repaying R = (T × S − A) ÷ (T − 1). A fund at 200% total coverage must repay 20% of its senior
securities to get back to 225%, and it usually has to sell assets in a falling market to do it. This is the
procyclical risk the redemption triggers create (`deleveraging_to_restore` in
[`asset_coverage.py`](../src/fundfinancelab/asset_coverage.py)).

## What would raise a downgrade-style concern

1. **Total coverage trending toward about 250%.** The cushion to the 225% monthly test would then be roughly 10%.
   KBRA describes the portfolio as mainly US common stocks and convertible securities [F], so the path to a breach is
   an equity drawdown, and a fall of about a third is within the range of past equity bear markets.
2. **A failed overcollateralisation test.** It is tested weekly, so it can bite before the monthly coverage test.
   Its parameters are in the MRPS terms and were not reviewed here.
3. **Forced deleveraging** that crystallises losses for common shareholders and cuts distributions. Distributions
   stop below 225% under the MRPS covenant [F].
4. **Refinancing of term dates** (e.g. Series C on 6 Sep 2027) in weak markets, or leverage added at lower coverage,
   as the proposed issuance does.
5. **Loss of the preferred rating** or another covenant breach that permits or requires redemption [D].

## Not covered

- The bank liquidity agreement itself: its covenants and events of default.
- The parameters of the overcollateralisation test (discount factors).
- How rule 18f-4 treats derivatives and reverse repurchase agreements.

Fitch's own closed-end fund ratings rest on asset coverage measured against its published criteria. A Fitch
affirmation cited criteria titled *Rating Closed-End Fund Debt and Preferred Stock*. The current edition should be
read before relying on any threshold here.

**Run it:**
`fund-finance-lab coverage --config examples/cef_coverage_csq_fy2021.json --out outputs/coverage_csq_fy2021`
