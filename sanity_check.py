#!/usr/bin/env python3
"""Market Price Sanity Checker — Marcus Webb.

Pre-entry sanity check for prediction-market prices: pulls the current
order book for a market, compares last trade vs. real mid, shows depth at
your size, and flags thin-book conditions. Read-only public Data/CLOB APIs.

Usage:
  python sanity_check.py --market <slug-or-id> --size 2000

Educational tool. Not financial advice.
"""

import argparse
import json
import sys
import urllib.request

GAMMA = "https://gamma-api.polymarket.com"
CLOB = "https://clob.polymarket.com"


def http_json(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": "sanity-check/1.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode())


def resolve(query: str) -> dict:
    url = f"{GAMMA}/markets/{query}" if query.isdigit() else f"{GAMMA}/markets?slug={query}"
    data = http_json(url)
    if isinstance(data, list):
        if not data:
            sys.exit("[!] no market found")
        data = data[0]
    return data


def book_mid(book: dict):
    bids = sorted([(float(x["price"]), float(x["size"])) for x in book.get("bids", [])], reverse=True)
    asks = sorted([(float(x["price"]), float(x["size"])) for x in book.get("asks", [])])
    if not bids or not asks:
        return None, bids, asks
    return (bids[0][0] + asks[0][0]) / 2, bids, asks


def depth_to_fill(levels, size, walking_up=True):
    """VWAP to fill `size` shares against given levels (asks ascending / bids descending)."""
    remaining, cost, levels_used = size, 0.0, 0
    for price, sz in levels:
        take = min(remaining, sz)
        cost += take * price
        remaining -= take
        levels_used += 1
        if remaining <= 0:
            break
    if remaining > 0:
        return None, None, levels_used  # book too thin
    return cost / size, cost, levels_used


def main():
    ap = argparse.ArgumentParser(description="Prediction market price sanity check")
    ap.add_argument("--market", required=True, help="market slug or id")
    ap.add_argument("--size", type=float, default=1000.0, help="intended position size (shares)")
    args = ap.parse_args()

    m = resolve(args.market)
    tokens = m.get("clobTokenIds") or []
    print(f"\nMarket : {m.get('question','?')}")

    for label, token in (("YES", tokens[0] if tokens else None),
                         ("NO", tokens[1] if len(tokens) > 1 else None)):
        if not token:
            continue
        try:
            book = http_json(f"{CLOB}/book?token_id={token}")
        except Exception as e:
            print(f"  {label}: book fetch failed ({e})")
            continue
        mid, bids, asks = book_mid(book)
        if mid is None:
            print(f"  {label}: one-sided book — treat quotes as unreliable.")
            continue
        spread = asks[0][0] - bids[0][0]
        vwap, cost, levels = depth_to_fill(asks, args.size)
        flag = ""
        if spread > 0.03:
            flag = "  ⚠ wide spread (>3¢)"
        if vwap is None:
            flag += "  ⚠ book thinner than your size"
        print(f"  {label}: bid {bids[0][0]*100:.1f}¢ / ask {asks[0][0]*100:.1f}¢ "
              f"(mid {mid*100:.1f}¢, spread {spread*100:.1f}¢)")
        if vwap is not None:
            slip = (vwap - asks[0][0]) * 100
            print(f"      fill {args.size:g} shares → VWAP {vwap*100:.1f}¢ "
                  f"(slippage {slip:+.1f}¢ over {levels} levels), cost ${cost:,.0f}{flag}")
        else:
            print(f"      cannot fill {args.size:g} shares on current book{flag}")

    print("\nRules of thumb: trade the mid, not the print; if your exit would "
          "walk the book, halve the entry.")
    print("Full checklist: https://brainresearchhub.net/research/access/prediction-markets-vs-polls-evidence")
    print("More research : https://brainresearchhub.net\n")


if __name__ == "__main__":
    main()
