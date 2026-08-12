from dataclasses import dataclass
from datetime import datetime, timezone
import csv
import hashlib
import json
from pathlib import Path
from .market_data import MarketDataNormalizer, Quote, Candle


@dataclass(frozen=True)
class HistoricalDataset:
    quotes: list[Quote]
    candles_by_time: dict[str, list[Candle]]


@dataclass(frozen=True)
class DatasetManifest:
    """Reproducibility metadata for an immutable historical input file."""
    source_file: str
    sha256: str
    rows: int
    first_timestamp: str
    last_timestamp: str


class HistoricalCSVLoader:
    """Loads provider-neutral EUR/USD historical CSV data.

    Expected columns: timestamp,bid,ask,open_4h,high_4h,low_4h,close_4h,
    open_1h,high_1h,low_1h,close_1h,open_15m,high_15m,low_15m,close_15m,
    open_5m,high_5m,low_5m,close_5m
    """
    REQUIRED_COLUMNS = (
        "timestamp", "bid", "ask",
        "open_4h", "high_4h", "low_4h", "close_4h",
        "open_1h", "high_1h", "low_1h", "close_1h",
        "open_15m", "high_15m", "low_15m", "close_15m",
        "open_5m", "high_5m", "low_5m", "close_5m",
    )

    def __init__(self, normalizer=None):
        self.n = normalizer or MarketDataNormalizer()

    def load(self, path: str | Path) -> HistoricalDataset:
        path = Path(path)
        quotes, candles = [], {}
        with path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            missing = [c for c in self.REQUIRED_COLUMNS if c not in (reader.fieldnames or [])]
            if missing:
                raise ValueError(f"historical CSV missing columns: {', '.join(missing)}")
            for row in reader:
                ts = normalize_timestamp(row["timestamp"])
                q = self.n.quote("EURUSD", float(row["bid"]), float(row["ask"]), ts)
                quotes.append(q)
                bars = []
                for tf in ("4H", "1H", "15M", "5M"):
                    bars.append(self.n.candle("EURUSD", tf,
                        open=float(row[f"open_{tf.lower()}"]),
                        high=float(row[f"high_{tf.lower()}"]),
                        low=float(row[f"low_{tf.lower()}"]),
                        close=float(row[f"close_{tf.lower()}"]), timestamp=ts))
                candles[ts] = bars
        dataset = HistoricalDataset(quotes, candles)
        validate_dataset(dataset)
        return dataset

    @staticmethod
    def manifest(path: str | Path, dataset: HistoricalDataset) -> DatasetManifest:
        path = Path(path)
        if not dataset.quotes:
            raise ValueError("cannot create manifest for empty dataset")
        return DatasetManifest(
            source_file=path.name,
            sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
            rows=len(dataset.quotes),
            first_timestamp=dataset.quotes[0].timestamp,
            last_timestamp=dataset.quotes[-1].timestamp,
        )


def normalize_timestamp(value: str) -> str:
    """Normalize an ISO-8601 timestamp to UTC with a canonical Z suffix."""
    raw = value.strip()
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    dt = datetime.fromisoformat(raw)
    if dt.tzinfo is None:
        raise ValueError("historical timestamps must include a timezone")
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def validate_dataset(dataset: HistoricalDataset) -> None:
    if not dataset.quotes:
        raise ValueError("historical dataset is empty")
    timestamps = [normalize_timestamp(q.timestamp) for q in dataset.quotes]
    if timestamps != sorted(timestamps):
        raise ValueError("historical timestamps must be sorted")
    if len(set(timestamps)) != len(timestamps):
        raise ValueError("historical timestamps must be unique")
    if any(q.symbol != "EURUSD" for q in dataset.quotes):
        raise ValueError("dataset contains non-EURUSD data")
    for q in dataset.quotes:
        if q.bid <= 0 or q.ask <= 0 or q.ask < q.bid:
            raise ValueError("dataset contains invalid bid/ask")
    for timestamp, candles in dataset.candles_by_time.items():
        if len(candles) != 4:
            raise ValueError(f"expected four timeframes at {timestamp}")
        for candle in candles:
            if candle.symbol != "EURUSD":
                raise ValueError("dataset contains non-EURUSD candles")
            if min(candle.open, candle.high, candle.low, candle.close) <= 0:
                raise ValueError(f"invalid OHLC at {timestamp}")
            if candle.high < max(candle.open, candle.close) or candle.low > min(candle.open, candle.close):
                raise ValueError(f"invalid OHLC at {timestamp}")


def write_manifest(path: str | Path, manifest: DatasetManifest) -> None:
    Path(path).write_text(json.dumps(manifest.__dict__, indent=2) + "\n", encoding="utf-8")
