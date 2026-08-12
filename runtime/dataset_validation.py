from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class ValidationReport:
    rows: int
    duplicate_timestamps: int
    ordering_errors: int
    invalid_ohlc: int
    invalid_prices: int
    unexpected_gaps: int

    @property
    def passed(self) -> bool:
        return not any(
            (
                self.duplicate_timestamps,
                self.ordering_errors,
                self.invalid_ohlc,
                self.invalid_prices,
                self.unexpected_gaps,
            )
        ) and self.rows > 0


def normalize_utc(value: str) -> str:
    raw = value.strip()
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    dt = datetime.fromisoformat(raw)
    if dt.tzinfo is None:
        raise ValueError("timestamp must contain timezone information")
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def validate_ohlc(rows: Iterable[dict]) -> ValidationReport:
    rows = list(rows)
    timestamps: list[str] = []
    duplicate = 0
    ordering = 0
    invalid_ohlc = 0
    invalid_prices = 0

    previous = None
    for row in rows:
        ts = normalize_utc(str(row["timestamp"]))
        timestamps.append(ts)
        if previous is not None:
            if ts <= previous:
                ordering += 1
            if ts == previous:
                duplicate += 1
        previous = ts

        try:
            o, h, l, c = (float(row[k]) for k in ("open", "high", "low", "close"))
        except (KeyError, TypeError, ValueError):
            invalid_prices += 1
            continue

        if min(o, h, l, c) <= 0:
            invalid_prices += 1
        if h < max(o, c) or l > min(o, c) or h < l:
            invalid_ohlc += 1

    return ValidationReport(
        rows=len(rows),
        duplicate_timestamps=duplicate,
        ordering_errors=ordering,
        invalid_ohlc=invalid_ohlc,
        invalid_prices=invalid_prices,
        unexpected_gaps=0,
    )


def sha256_file(path: str | Path) -> str:
    digest = sha256()
    with Path(path).open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
