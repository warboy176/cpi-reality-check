# CPI Reality Check

A free, open tool that checks the viral **"MT5 CPI HACK"** claim with real numbers instead of a highlight reel.

A clip going around (an MT5 "trade management bot" sold as a CPI *hack* with "100% free — DM me on Telegram for access") shows someone turning a CPI gold trade into "+200K, withdrew 170K." The bot sets a 70-pip stop, moves it to break-even at +50 pips, then trails. The pitch is **guaranteed wins**.

This tool runs **those exact rules** on **real gold data from the actual CPI release in the clip**, and shows the honest outcome distribution. No broker, no account, no orders — it only reads public price data and does arithmetic.

## Run it

```
python3 cpi_reality_check.py
```

No dependencies, no API key, Python 3 standard library only. Options:
- `--day 2026-11-10` the CPI release day to replay on real data (UTC).
- `--release 13:30` release time in UTC (US CPI = 13:30 UTC / 8:30 ET).
- `--runs 20000` Monte-Carlo sample size.

## What it shows

1. **Real data, his own event.** Replaying his 6-buy grid + 70-pip-stop + trailing rules on the real **Nov 10 2026** CPI gold session: gold ranged **$124** that day — **17.8× his $7 (70-pip) stop** — and **all six positions stopped out**. He posted the one day it worked; this is what the rules actually did on the event he's bragging about.
2. **No guarantee.** Across many simulated CPI events with a coin-flip entry (the bot predicts nothing), ~**43% lose**, with a fat tail past **−320 pips**. A trailing stop has positive *skew* (cut losers, ride winners) — that's a known property of trailing stops, **not** a secret and **not** a guarantee.

## What it is NOT

- **Not a trading bot.** It places no orders, connects to no broker, holds no keys, runs no strategy on a live account.
- **Not financial advice.** Nothing here tells you to trade anything.
- **Not a claim that the method always loses.** It doesn't. The honest point is narrower and stronger: the *bot* adds no edge, and "guaranteed" is false.

## The honest limits

- The real-data replay uses **free Yahoo gold-futures (GC=F)** bars, which are delayed and approximate, and models news spread/slippage with fixed assumptions you can read in the source. Your broker's fills will differ.
- The Monte-Carlo is a **model**, not a prophecy. It's deliberately built to be fair (it does **not** assume you lose). Read the code — the assumptions are all at the top.
- "Pip" on gold is defined here as **$0.10** of price (1 point = $0.01; 1 pip = 10 points). State your own broker's convention if it differs.
- One real CPI day is one sample. The point of [2] is the *distribution*, not the single day.

## The actual takeaway

- A break-even / trailing stop manages **exits**. It cannot make a bad **entry** good. Your result tracks *your* entry — not the bot.
- **"Guaranteed wins" is false.** The initial stop can hit before break-even ever triggers; during CPI, slippage and spread blowout fill stops *through* their level.
- Trailing stops are a **free, built-in MT5 feature**. The "secret bot" is a standard thing with a new name.
- The real product being sold is the **Telegram funnel** — "free" is the hook; the money is on the other side (signal upsells, broker / prop-firm affiliate links that pay on your volume and losses, paid VIP).

Keep your $7 stop. Keep your money off the Telegram link.

---

Built and released free by **Warboy** — no tier, no wall, no DM-me-on-Telegram.
More free rebuilds of the stuff the "gurus" sell: https://github.com/warboy176 · https://www.patreon.com/warboy176
