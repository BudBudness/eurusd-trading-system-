from dataclasses import dataclass
from datetime import datetime
import csv
from pathlib import Path
from .market_data import MarketDataNormalizer, Quote, Candle

@dataclass(frozen=True)
class HistoricalDataset:
    quotes: list[Quote]
    candles_by_time: dict[str, list[Candle]]

class HistoricalCSVLoader:
    """Loads provider-neutral EUR/USD historical CSV data.

    Expected columns: timestamp,bid,ask,open_4h,high_4h,low_4h,close_4h,
    open_1h,high_1h,low_1h,close_1h,open_15m,high_15m,low_15m,close_15m,
    open_5m,high_5m,low_5m,close_5m
    """
    def __init__(self, normalizer=None):
        self.n = normalizer or MarketDataNormalizer()

    def load(self, path: str | Path) -> HistoricalDataset:
        quotes, candles = [], {}
        with open(path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                ts = row["timestamp"]
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
        return HistoricalDataset(quotes, candles)


def validate_dataset(dataset: HistoricalDataset) -> None:
    if not dataset.quotes:
        raise ValueError("historical dataset is empty")
    timestamps = [q.timestamp for q in dataset.quotes]
    if timestamps != sorted(timestamps):
        raise ValueError("historical timestamps must be sorted")
    if len(set(timestamps)) != len(timestamps):
        raise ValueError("historical timestamps must be unique")
    if any(q.symbol != "EURUSD" for q in dataset.quotes):
        raise ValueError("dataset contains non-EURUSD data")
