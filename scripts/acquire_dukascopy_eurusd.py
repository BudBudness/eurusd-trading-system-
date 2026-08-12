#!/usr/bin/env python3
"""Acquire real EUR/USD M1 candles from Dukascopy's documented historical API.

Usage:
  python scripts/acquire_dukascopy_eurusd.py --start 2026-01-01 --end 2026-02-01

The script stores raw JSON responses unchanged and writes SHA-256 metadata. It
never overwrites an existing raw artifact. The API currently documents a
maximum of 5000 records per historicalPrices request, so requests are chunked.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

API = "https://freeserv.dukascopy.com/2.0/"


def parse_date(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%d").replace(tzinfo=timezone.utc)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fetch(url: str) -> bytes:
    request = Request(url, headers={"User-Agent": "eurusd-trading-system/dukascopy-acquisition"})
    with urlopen(request, timeout=60) as response:
        return response.read()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", required=True, help="UTC date YYYY-MM-DD")
    parser.add_argument("--end", required=True, help="exclusive UTC date YYYY-MM-DD")
    parser.add_argument("--instrument", default="EURUSD")
    parser.add_argument("--chunk-days", type=int, default=7)
    parser.add_argument("--output", default="data/historical/dukascopy/raw/M1")
    args = parser.parse_args()

    start, end = parse_date(args.start), parse_date(args.end)
    if start >= end:
        parser.error("--start must precede --end")
    if args.chunk_days <= 0:
        parser.error("--chunk-days must be positive")

    root = Path(args.output)
    root.mkdir(parents=True, exist_ok=True)
    records = []
    cursor = start
    while cursor < end:
        chunk_end = min(cursor + timedelta(days=args.chunk_days), end)
        params = {
            "path": "api/historicalPrices",
            "instrument": args.instrument,
            "timeFrame": "1min",
            "count": 5000,
            "start": int(cursor.timestamp() * 1000),
            "end": int(chunk_end.timestamp() * 1000),
            "dayStartTime": "UTC",
            "offerSide": "B",
        }
        url = API + "?" + urlencode(params)
        raw = fetch(url)
        name = f"{args.instrument}_M1_{cursor:%Y%m%dT%H%M%SZ}_{chunk_end:%Y%m%dT%H%M%SZ}.json"
        destination = root / name
        if destination.exists():
            raise FileExistsError(f"refusing to overwrite immutable artifact: {destination}")
        destination.write_bytes(raw)
        records.append({
            "path": str(destination),
            "sha256": sha256_bytes(raw),
            "bytes": len(raw),
            "start": cursor.isoformat().replace("+00:00", "Z"),
            "end": chunk_end.isoformat().replace("+00:00", "Z"),
            "url": url,
        })
        cursor = chunk_end

    manifest = {
        "schema_version": "1",
        "provider": "Dukascopy",
        "instrument": args.instrument,
        "timeframe": "1min",
        "offer_side": "B",
        "timezone": "UTC",
        "start": start.isoformat().replace("+00:00", "Z"),
        "end": end.isoformat().replace("+00:00", "Z"),
        "artifacts": records,
    }
    manifest_path = root.parent / "manifests" / f"{args.instrument}_M1_acquisition.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(manifest_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
