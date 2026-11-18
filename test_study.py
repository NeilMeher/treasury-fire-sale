import unittest
from math import inf

from study import simulate


class FireSaleTests(unittest.TestCase):
    def test_no_shock_and_direct_only(self):
        self.assertEqual(simulate(0,8,30)["total_sales"],0)
        loss=simulate(.08,8,0,sales=False)
        self.assertAlmostEqual(loss["equity_loss"],3.6)
        self.assertEqual(loss["impact"],0)

    def test_unlimited_case_hand_calculation(self):
        r=simulate(.08,8,inf,capture=True)
        a=1-1/(1.3*8)-.04
        expected=(.875-.98*a)*180/(.98*(1-a))
        self.assertAlmostEqual(r["total_sales"],expected)
        self.assertEqual(r["second_round"],0)
        self.assertEqual(r["impact"],0)
        self.assertEqual(r["stop"],"margin restored")

    def test_dealer_and_lender_ledger(self):
        r=simulate(.08,8,30,capture=True)
        for step in range(r["rounds"]+1):
            rows=[x for x in r["ledger"] if x["step"]==step]
            self.assertAlmostEqual(sum(x["cash"] for x in rows),362,places=6)
            self.assertAlmostEqual(sum(x["units"] for x in rows),180,places=6)
            self.assertAlmostEqual(sum(x["repo_payable"]-x["repo_receivable"] for x in rows),0,places=6)
        self.assertGreaterEqual(r["second_round"],5)
        self.assertNotEqual(r["stop"],"round limit")

    def test_price_floor_and_exhaustion(self):
        r=simulate(.2,16,0,impact=5,capture=True)
        self.assertAlmostEqual(r["ledger"][-1]["price"],.25)
        self.assertEqual(r["stop"],"inventory exhausted")
        self.assertGreater(r["residual"],0)
