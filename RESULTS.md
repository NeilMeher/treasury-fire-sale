# Results

At 8× leverage the 30-unit dealer case produced 130 cascades in 400 common shocks (32.5%, 2.34 pp Monte Carlo standard error), with 13.84 units sold on average after the first round. With no dealer capacity the corresponding figures were 256 of 400 (64.0%, 2.40 pp) and 63.64 units. The unlimited dealer acquired an average of 19.89 units in the first round and generated no additional price impact or second-round liquidation. The direct-mark-only comparison shares the first exogenous repricing and omits settlement. Average fund equity loss was $2.51 direct, $2.51 unlimited, $4.66 at 30 units and $11.31 at zero capacity.

| 8×, 30-unit comparison | Cascade rate | Avg. second-round and later sales | Avg. additional price decline |
|---|---:|---:|---:|
| Baseline batch | 32.50% | 13.84 | 1.68% |
| Reverse sequential execution | 32.25% | 11.71 | 1.51% |
| Half price impact | 25.00% | 4.07 | 0.43% |
| Double price impact | 33.00% | 43.75 | 7.72% |
| Change initial holdings to 150/30 | 32.50% | 13.84 | 1.68% |

Monte Carlo standard errors describe sampling of the chosen shock distribution. The parameter variants change that conditional mechanism, and the historical episode does not identify the parameters. Holdings concentration is neutral under the symmetric terms and batch clearing tested here. In the 30-unit baseline at 8×, 5 of 400 runs reached the 100-round cap, all with residual funding gaps below $0.000001. Inventory exhaustion can leave much larger gaps. The CSV reports these states separately. Zero observed cascades in the unlimited case reflects the no-impact mechanism and the stated threshold under the tested settings.

## Hand check the first round

At a funding shock of 0.08 the mark starts at $0.98 and the advance fraction drops to 1 − 1/(1.3 × 8) − 0.04 ≈ 0.863846. A fund with 100 units owes $87.50. Its order is (87.50 − 0.863846 × 0.98 × 100) ÷ (0.98 × (1 − 0.863846)) ≈ 21.31 units. The smaller fund submits 17.05. In the capacity-limited case the dealer buys 30, outside investors buy 8.35, and the first-clearing price is 0.98 × exp(−0.16 × 8.35/180) ≈ $0.97275. Compare round 1 in the ledger. The replay sold 70.92 units total, including 32.57 after the first round. It restored margin in 46 rounds, with a 3.57% additional asset decline.
