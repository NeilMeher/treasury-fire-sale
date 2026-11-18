# Sources and data dictionary

Both historical sources were accessed November 18, 2026. The simulation generates all observations and uses hypothetical values. No third-party files, trade observations or report text are reproduced.

- Federal Reserve, November 2020 Financial Stability Report. The section on Treasury disruption describes leverage, basis-trade unwinds, and changes in intermediation in March 2020. [Retrospective](https://www.federalreserve.gov/publications/2020-november-financial-stability-report-borrowing.htm)
- Aldasoro, Hüser and Kok, BIS Working Paper 908, Contagion Accounting. Motivates maintaining a ledger and tracking different channels. [Paper](https://www.bis.org/publ/work908.pdf)

Grid rows contain common shock count, leverage multiple, dealer inventory capacity in units, cascade probability, simulation standard error, mean second-round and all-round sales in units, mean peak price decline relative to the post-exogenous-shock mark, mean fund equity loss in dollars, count of remaining material funding gaps, and count of round-cap stops. Capacity inf denotes an unlimited inventory cap with the same initial dealer cash.

The ledger gives one record per modeled balance sheet per clearing round. Cash, payable, receivable, collateral, cumulative mark loss and equity are synthetic dollars. Units measure one homogeneous security initially worth $1. Round sale and purchase counts are round-level fields repeated per agent, so do not add across ledger rows. Collateral records the marked fund holdings. The repo lender holds the corresponding receivable, and cash and securities are conserved at settlement. No external cash flows or interest occur inside this event-time experiment. The exogenous mark loss reduces portfolio values without moving cash.
