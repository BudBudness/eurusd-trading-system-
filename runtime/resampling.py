from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone


@dataclass(frozen=True)
class Bar:
    timestamp: str
    open: float
    high: float
    low: float
    close: float
    volume: float = 0.0


_MINUTES = {"M5": 5, "M15": 15, "H1": 60, "H4": 240}


def _parse(value: str) -> datetime:
    raw = value[:-1] + "+00:00" if value.endswith("Z") else value
    dt = datetime.fromisoformat(raw)
    if dt.tzinfo is None:
        raise ValueError("canonical timestamps must be timezone-aware")
    return dt.astimezone(timezone.utc)


def _bucket(ts: datetime, minutes: int) -> datetime:
    epoch = int(ts.timestamp())
    size = minutes * 60
    return datetime.fromtimestamp((epoch // size) * size, tz=timezone.utc)


def resample_m1(rows: list[Bar], timeframe: str) -> list[Bar]:
    """Deterministically aggregate canonical M1 bars into a higher timeframe."""
    if timeframe not in _MINUTES:
        raise ValueError(f"unsupported derived timeframe: {timeframe}")
    if not rows:
        return []

    ordered = sorted(rows, key=lambda r: _parse(r.timestamp))
    groups: dict[datetime, list[Bar]] = defaultdict(list)
    for row in ordered:
        groups[_bucket(_parse(row.timestamp), _MINUTES[timeframe])].append(row)

    result: list[Bar] = []
    for bucket in sorted(groups):
        bars = groups[bucket]
        result.append(
            Bar(
                timestamp=bucket.isoformat().replace("+00:00", "Z"),
                open=bars[0].open,
                high=max(x.high for x in bars),
                low=min(x.low for x in bars),
                close=bars[-1].close,
                volume=sum(x.volume for x in bars),
            )
        )
    return result
