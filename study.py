import argparse
import csv
from dataclasses import dataclass
import json
from math import exp, inf, sqrt
from pathlib import Path
from random import Random
from statistics import mean

ROOT=Path(__file__).resolve().parent
LEV=(3,5,8,12,16)
CAP=(0,15,30,60,120)
EPS=1e-8


@dataclass
class Agent:
    name: str
    units: float = 0
    cash: float = 0
    debt: float = 0
    mark_loss: float = 0


def simulate(shock, leverage, capacity, impact=.16, order="batch", holdings=(100,80), sales=True, capture=False):
    total=sum(holdings)
    if not 0<=shock<=.2 or leverage<=1 or capacity<0 or impact<0:
        raise ValueError("Invalid parameters")
    funds=[Agent("Fund "+str(i+1),units,0,units*(1-1/leverage)) for i,units in enumerate(holdings)]
    dealer=Agent("Dealer",cash=total+1)
    outside=Agent("Outside investor",cash=total+1)
    lender=Agent("Repo lender")
    agents=(*funds,dealer,outside,lender)
    post=1-.25*shock
    advance=1-1/(1.3*leverage)-.5*shock
    price=post
    for agent in agents:
        agent.mark_loss = (1-post)*agent.units
    ledger=[]
    volumes=[]
    initial_fund_equity=sum(holdings)/leverage

    def snapshot(step,sold,from_dealer,to_outside):
        if capture:
            for a in agents:
                claim=sum(f.debt for f in funds) if a is lender else 0
                collateral=a.units*price if a in funds else 0
                ledger.append(dict(step=step,agent=a.name,price=round(price,10),cash=round(a.cash,8),
                    units=round(a.units,8),repo_payable=round(a.debt,8),repo_receivable=round(claim,8),
                    mark_loss=round(a.mark_loss,8),collateral=round(collateral,8),equity=round(a.cash+a.units*price+claim-a.debt,8),
                    round_sales=round(sold,8),dealer_buys=round(from_dealer,8),outside_buys=round(to_outside,8)))

    def repay(fund):
        payment=min(fund.cash,fund.debt)
        fund.debt-=payment
        fund.cash-=payment
        lender.cash+=payment

    def mark_settle(pairs):
        nonlocal price
        orders=sum(size for _,size in pairs)
        dealer_order=min(orders,max(0,capacity-dealer.units),dealer.cash/price)
        outside_order=orders-dealer_order
        new_price=max(.25,price*exp(-impact*outside_order/total))
        if outside_order*new_price > outside.cash + EPS:
            raise RuntimeError("Outside cash schedule exhausted")
        for agent in agents:
            agent.mark_loss += (price-new_price)*agent.units
        for fund,quantity in pairs:
            fund.units-=quantity
            fund.cash+=new_price*quantity
            repay(fund)
        for buyer,qty in ((dealer,dealer_order),(outside,outside_order)):
            buyer.cash-=qty*new_price
            buyer.units+=qty
        price=new_price
        return dealer_order,outside_order

    snapshot(0,0,0,0)
    reason="direct only"
    if sales:
        reason="round limit"
        for step in range(1,101):
            for fund in funds:
                repay(fund)
            gaps=[f.debt-advance*price*f.units for f in funds]
            pairs=[(fund,min(fund.units,max(0,gap)/(price*(1-advance))))
                   for fund,gap in zip(funds,gaps)]
            pairs=[(fund,size) for fund,size in pairs if size>EPS]
            if not pairs:
                reason="margin restored" if max(gaps)<EPS else "inventory exhausted"
                break
            if order=="batch":
                dealer_buys,outside_buys=mark_settle(pairs)
            elif order=="reverse":
                fills=[mark_settle([pair]) for pair in reversed(pairs)]
                dealer_buys,outside_buys=map(sum,zip(*fills))
            else:
                raise ValueError(f"Unknown order {order}")
            sold=dealer_buys+outside_buys
            volumes.append(sold)
            snapshot(step,sold,dealer_buys,outside_buys)
    residual=sum(max(0,f.debt-advance*price*f.units) for f in funds)
    loss=initial_fund_equity-sum(f.cash+f.units*price-f.debt for f in funds)
    return dict(second_round=sum(volumes[1:]),total_sales=sum(volumes),impact=(post-price)/post,
                equity_loss=loss,residual= residual,rounds=len(volumes),stop=reason,
                cash=sum(a.cash for a in agents),inventory=sum(a.units for a in agents),ledger=ledger)


def analyze(shocks,leverage,capacity,**opts):
    draws=[simulate(s,leverage,capacity,**opts) for s in shocks]
    p=mean(r["second_round"]>=5 for r in draws)
    return dict(n=len(draws),cascade=p,cascade_mcse=sqrt(p*(1-p)/len(draws)),
                avg_second_round=mean(r["second_round"] for r in draws),
                avg_sales=mean(r["total_sales"] for r in draws),
                avg_peak_impact=mean(r["impact"] for r in draws),
                avg_fund_loss=mean(r["equity_loss"] for r in draws),
                residual_count=sum(r["residual"]>1e-6 for r in draws),
                round_limit_count=sum(r["stop"]=="round limit" for r in draws))


def write_csv(path,rows):
    with path.open("w",newline="",encoding="utf-8") as file:
        writer=csv.DictWriter(file,fieldnames=rows[0],lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def heatmap(rows,path):
    lines=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 385" role="img">',
           '<title>Probability of at least five units sold after round one</title>',
           '<rect width="760" height="385" fill="#fbfaf6"/>',
           '<g font-family="Arial,sans-serif" fill="#163343">',
           '<text x="25" y="39" font-size="25">Liquidation cascades under funding stress</text>',
           '<text x="25" y="62" font-size="14">Synthetic scenarios · probability of ≥5 units sold after round one</text>',
           '<text x="425" y="356" text-anchor="middle" font-size="15">Dealer capacity (units)</text>']
    for j,cap in enumerate(CAP):
        lines.append(f'<text x="{210+j*107}" y="105" text-anchor="middle">{cap}</text>')
    for i,lev in enumerate(LEV):
        y=120+i*40
        lines.append(f'<text x="126" y="{y+25}" text-anchor="end">{lev}× leverage</text>')
        for j,cap in enumerate(CAP):
            p=next(row["cascade"] for row in rows if row["variant"]=="Limited" and row["leverage"]==lev and row["capacity"]==cap)
            x=158+j*107
            color=f"rgb({int(223-177*p)},{int(239-124*p)},{int(234-114*p)})"
            text="#fff" if p>.60 else "#163343"
            lines += [f'<rect x="{x}" y="{y}" width="104" height="37" rx="3" fill="{color}"/>',
                      f'<text x="{x+52}" y="{y+24}" fill="{text}" text-anchor="middle">{p:.1%}</text>']
    lines.append("</g></svg>")
    path.write_text("\n".join(lines)+"\n",encoding="utf-8")


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--quick",action="store_true")
    parser.add_argument("--output",type=Path,default=ROOT/"report")
    args=parser.parse_args()
    args.output.mkdir(exist_ok=True,parents=True)
    rng=Random(8808)
    shocks=[.20*rng.betavariate(2,5) for _ in range(20 if args.quick else 400)]
    rows=[dict(variant="Limited",leverage=lev,capacity=cap,**analyze(shocks,lev,cap)) for lev in LEV for cap in CAP]
    for lev in LEV:
        for variant, cap, settings in (("Direct only", 0, dict(sales=False)), ("Unlimited", inf, {})):
            rows.append(dict(variant=variant,leverage=lev,capacity=cap,**analyze(shocks,lev,cap,**settings)))
    cases=[("Reverse order",30,dict(order="reverse")),
           ("Half impact",30,dict(impact=.08)),("Double impact",30,dict(impact=.32)),
           ("Concentrated holdings",30,dict(holdings=(150,30)))]
    for label,cap,settings in cases:
        rows.append(dict(variant=label,leverage=8,capacity=cap,**analyze(shocks,8,cap,**settings)))
    result=simulate(.08,8,30,capture=True)
    write_csv(args.output/"grid.csv",[{k:round(v,9) if isinstance(v,float) and v!=inf else v for k,v in row.items()} for row in rows])
    write_csv(args.output/"ledger.csv",result["ledger"])
    heatmap(rows,args.output/"cascade.svg")
    replay=(ROOT/"replay.html").read_text(encoding="utf-8")
    (args.output/"replay.html").write_text(replay.replace("@LEDGER@",json.dumps(result["ledger"])),encoding="utf-8")
    if not args.quick:
        for row in rows:
            if row["leverage"]==8 and (row["variant"]!="Limited" or row["capacity"] in (0,30,120)):
                print(row)
    print({k:v for k,v in result.items() if k!="ledger"})


if __name__=="__main__":
    main()
