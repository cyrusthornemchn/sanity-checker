# Market Price Sanity Checker

Pre-entry sanity check for prediction-market prices (Polymarket today,
Kalshi-ready structure). Pulls the live order book and answers the three
questions most losses ignore:

1. **Mid vs. print** — is the last trade lying about the real price?
2. **Depth at your size** — what will filling your position actually cost?
3. **Thin-book flags** — wide spreads, one-sided books, unfillable sizes.

**No wallet. No keys. Read-only** public market-data endpoints.

## Why

Most beginners lose to structure, not forecasting: they size off a thin
last-print, then discover their exit walks the book. This tool makes the
boring checks automatic — the same routine from my
[price sanity checklist](https://gist.github.com/cyrusthornemchn/2b2e132e06e3d7924be01ca28769562c).

## Usage

```bash
git clone https://github.com/cyrusthornemchn/sanity-checker.git
cd sanity-checker
python3 sanity_check.py --market <slug-or-id> --size 2000
```

## Sample output

```
Market : Will the Senate pass the bill by Nov 30?
  YES: bid 61.0¢ / ask 63.0¢ (mid 62.0¢, spread 2.0¢)
      fill 2000 shares → VWAP 63.4¢ (slippage +0.4¢ over 3 levels), cost $1,268
  NO : bid 36.0¢ / ask 38.5¢ (mid 37.2¢, spread 2.5¢)
      fill 2000 shares → VWAP 40.1¢ (slippage +1.6¢ over 5 levels), cost $802  ⚠ wide spread (>3¢)
```

## Reading the output

- **Slippage over levels** — if filling already walks several levels,
  your exit will be worse. Halve the position.
- **Wide-spread flag** — mid is your only honest quote; limit orders only.
- **"Book thinner than your size"** — the market is a lottery ticket at
  this size. Pass or split across venues
  ([why platforms price differently](https://brainresearchhub.net/research/perps/why-kalshi-polymarket-price-differently)).

## Related research

- [Markets vs polls: the full evidence review](https://brainresearchhub.net/research/access/prediction-markets-vs-polls-evidence)
- [Who actually makes money: leaderboard reality](https://brainresearchhub.net/research/sdk/who-makes-money-polymarket-leaderboard)
- [Seven mistakes that kill bankrolls](https://brainresearchhub.net/research/access/prediction-market-mistakes)

## License

MIT.

*Educational tool. Not financial advice. Not affiliated with Polymarket.*
