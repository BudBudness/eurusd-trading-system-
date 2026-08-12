from dataclasses import dataclass
from .historical_data import HistoricalDataset, validate_dataset

@dataclass(frozen=True)
class ReplayFrame:
    index: int
    timestamp: str
    quote: object
    candles: list

class ReplayEngine:
    """Sequential, deterministic historical-data iterator."""
    def frames(self, dataset: HistoricalDataset):
        validate_dataset(dataset)
        for i, quote in enumerate(dataset.quotes):
            yield ReplayFrame(i, quote.timestamp, quote, dataset.candles_by_time[quote.timestamp])

    def run(self, dataset: HistoricalDataset, callback):
        count = 0
        for frame in self.frames(dataset):
            callback(frame)
            count += 1
        return count
