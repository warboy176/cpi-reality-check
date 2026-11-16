#!/usr/bin/env python3
"""
CPI Reality Check  —  does the viral "MT5 CPI HACK" trailing-stop bot give "guaranteed wins"?

No. And you don't have to take my word for it — this runs HIS EXACT RULES on REAL gold data from
the actual CPI release his clip is about, and separately shows that the bot itself adds zero edge.

The clip (jdwalkerofficial, "MT5 CPI HACK", Nov 2026) sells an MT5 "trade management bot": you pick
the trade, it sets a 70-pip stop, moves it to break-even at +50, then trails. Pitch: "100% free,
guaranteed wins — DM me on Telegram for access."

Here is what's actually true, with numbers:
  1. A break-even/trailing stop manages EXITS. It cannot make a bad ENTRY good. Your P&L tracks YOUR
     entry skill — not the bot (see the edge sweep: the bot's own contribution is ~zero, minus costs).
  2. "Guaranteed" is false: there is always a loss tail, and during CPI it's fat.
  3. Trailing stops are a FREE, built-in MT5 feature. The "secret bot" is a standard thing.
  4. On the real CPI day, gold's intraday range dwarfs his 70-pip ($7) stop — which is why those
     stops get chopped out. This tool shows that on the actual bars.
  5. "Free, but DM Telegram" is a lead funnel (signals / broker + prop-firm affiliate / paid VIP).

No broker, no account, no orders. It only reads public price data and does arithmetic.
Convention: XAUUSD 1 "pip" = $0.10 of price (1 point = $0.01; 1 pip = 10 points).
"""
import argparse, json, random, statistics, urllib.request, datetime

PIP = 0.10
class R:   # his rules, from the clip
    sl=70; be=50; trail_start=100; trail_lock=50; trail_step=50; grid=6; spacing=30

SPREAD_NORMAL=2; SPREAD_NEWS=25; SLIP_NEWS=20     # pips; gold news conditions


def _trail_exit(entry, bars):
    """Run his break-even + trailing-stop rules over a price path (list of prices, in pips vs entry).
    Returns (exit_pips, stopped_bool). bars[i] = (price_pips, is_news_bar)."""
    sl = entry - R.sl; peak = entry
    for price, news in bars:
        peak = max(peak, price); prof = peak - entry
        if prof >= R.trail_start:
            sl = max(sl, entry + R.trail_lock + int((prof-R.trail_start)//R.trail_step)*R.trail_step)
        elif prof >= R.be:
            sl = max(sl, entry)
        if price <= sl:
            fill = sl - (SLIP_NEWS if news else 0) - (SPREAD_NEWS if news else SPREAD_NORMAL)/2
            return fill-entry, True
    return bars[-1][0]-entry-SPREAD_NORMAL/2, False


def fetch_gold(day, interval="5m"):
    d0=datetime.datetime.strptime(day,"%Y-%m-%d").replace(tzinfo=datetime.timezone.utc)
    p1=int(d0.timestamp()); p2=p1+86400
    u=("https://query1.finance.yahoo.com/v8/finance/chart/GC=F?period1=%d&period2=%d&interval=%s"%(p1,p2,interval))
    j=json.load(urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"Mozilla/5.0"}),timeout=25))
    r=j["chart"]["result"][0]; ts=r["timestamp"]; q=r["indicators"]["quote"][0]
    return [(t,c) for t,c in zip(ts,q["close"]) if c is not None]


def replay_real(day, release="13:30"):
    """Replay his grid of buys + trailing rules on the REAL gold bars after the CPI release."""
    rows=fetch_gold(day)
    if not rows: return None
    hh,mm=map(int,release.split(":"))
    rel=datetime.datetime.strptime(day,"%Y-%m-%d").replace(hour=hh,minute=mm,tzinfo=datetime.timezone.utc).timestamp()
    after=[(t,c) for t,c in rows if t>=rel-300]
    if len(after)<4: return None
    prices=[c for _,c in after]
    base=prices[0]                              # he buys "the zone" at the release
    dayhi=max(c for _,c in rows); daylo=min(c for _,c in rows)
    # convert to pips vs base; first ~6 bars (30 min) flagged news
    path=[((c-base)/PIP, i<6) for i,c in enumerate(prices)]
    tot=0.0; stopped=0
    for g in range(R.grid):
        entry=-g*R.spacing
        ex,st=_trail_exit(entry, path)
        ex-=(SPREAD_NEWS/2 + SLIP_NEWS*0.5)     # entry cost during the release
        tot+=ex; stopped+=st
    return {"day":day, "bars":len(after), "entry_price":round(base,2),
            "day_range_usd":round(dayhi-daylo,2), "day_lo":round(daylo,2), "day_hi":round(dayhi,2),
            "stop_usd":round(R.sl*PIP,2), "positions":R.grid, "stopped_out":stopped,
            "net_pips":round(tot,1), "net_usd_per_0p01lot":round(tot*PIP,2)}


def edge_sweep(n=15000, seed=11):
    """Monte Carlo: hold his rules fixed, vary only YOUR entry skill. If the bot had an edge, P&L
    would be positive at zero skill. It isn't — the result tracks YOU, and costs drag it down."""
    rng=random.Random(seed); out=[]
    for edge in (-0.10,-0.05,0.0,0.05,0.10,0.20):
        res=[]
        for _ in range(n):
            favour = rng.random() < 0.5+edge
            d=1 if favour else -1
            spike=max(50,min(abs(rng.lognormvariate(5.2,0.6)),900))
            p=0.0; path=[]
            for i in range(1,121):
                if i<5: s=rng.gauss(0,15); nw=False
                elif i<=7: s=d*spike/3+rng.gauss(0,35); nw=True
                elif i<=13: s=-d*rng.uniform(0.3,0.9)*spike/6+rng.gauss(0,22); nw=True
                else: s=rng.gauss(0,16); nw=False
                p+=s; path.append((p,nw))
            t0=rng.randint(6,8); base=path[t0][0]
            tot=0.0
            for g in range(R.grid):
                e=base-g*R.spacing
                ex,_=_trail_exit(e,[(pp-0,nw) for pp,nw in path[t0:]])
                # express path relative to this entry
                ex2,_=_trail_exit(e,[(pp,nw) for pp,nw in path[t0:]])
                tot+=ex2-(SPREAD_NEWS/2+SLIP_NEWS*0.5)
            res.append(tot)
        res.sort(); wins=sum(1 for x in res if x>0)
        out.append((edge, round(100*wins/n,1), round(statistics.median(res),0), round(res[int(0.05*n)],0)))
    return out


def main():
    ap=argparse.ArgumentParser(description="Reality-check the MT5 'CPI hack' trailing bot on real data.")
    ap.add_argument("--day", default="2026-11-10", help="CPI release day (UTC), YYYY-MM-DD")
    ap.add_argument("--release", default="13:30", help="release time UTC (US CPI = 13:30 UTC / 8:30 ET)")
    ap.add_argument("--runs", type=int, default=15000)
    a=ap.parse_args()
    print("="*78)
    print("CPI REALITY CHECK — his rules: %d buys, %dp stop ($%.0f), BE@+%d, trail +%d then +%d/step"
          % (R.grid,R.sl,R.sl*PIP,R.be,R.trail_lock,R.trail_step))
    print("="*78)
    print("\n[1] REAL DATA — his exact rules on the actual CPI release he's talking about:")
    try:
        r=replay_real(a.day,a.release)
        if r:
            print("    %s  gold @release $%.2f | that day gold ranged $%.2f ($%.2f–$%.2f)"
                  % (r["day"],r["entry_price"],r["day_range_usd"],r["day_lo"],r["day_hi"]))
            print("    his stop is $%.2f (70 pips). The day's range is %.1fx his stop."
                  % (r["stop_usd"], r["day_range_usd"]/r["stop_usd"]))
            print("    replaying the %d-position grid on real bars: %d of %d positions stopped out, net %+0.0f pips (%+.2f per 0.01 lot)."
                  % (r["positions"],r["stopped_out"],r["positions"],r["net_pips"],r["net_usd_per_0p01lot"]))
            print("    one day is one coin flip. He posted the day it worked. See [2] for the honest distribution.")
        else:
            print("    (no intraday data returned for that day; try another --day within ~60 days)")
    except Exception as e:
        print("    real-data fetch failed (%r); the structural result in [2] stands without it."%(repr(e)[:70]))
    print("\n[2] THE BOT ADDS NO EDGE — hold his rules fixed, vary only YOUR entry skill (%d runs each):"%a.runs)
    print("    your_edge   win%%    median_pips   5th_pctile")
    for edge,win,med,p5 in edge_sweep(a.runs):
        tag = "  <- coin-flip entry; the bot on its own" if edge==0.0 else ""
        print("     %+5.0f%%     %5.1f    %+8.0f      %+7.0f%s"%(edge*100,win,med,p5,tag))
    print("    read it: the ONLY thing that moves the outcome is YOUR entry. The bot's own contribution")
    print("    is a coin flip minus costs. It cannot manufacture an edge — that's not what exits do.")
    print("\nVERDICT: 'guaranteed wins' is false (there's always a loss tail, fat during CPI). The bot is a")
    print("free, built-in feature that adds no edge. The product being sold is the Telegram funnel, not the bot.\n")

if __name__=="__main__":
    main()
