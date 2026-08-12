from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Quote:
    symbol: str
    bid: float
    ask: float
    timestamp: str

    @property
    def mid(self) -> float:
        return (self.bid + self.ask) / 2

    @property
    def spread(self) -> float:
        return self.ask - self.bid


@dataclass(frozen=True)
class Candle:
    symbol: str
    timeframe: str
    timestamp: str
    open: float
    high: float
    low: float
    close: float
    volume: float = 0.0


class MarketDataNormalizer:
    """Normalizes provider-neutral EUR/USD market observations."""

    SUPPORTED_TIMEFRAMES = {"4H", "1H", "15M", "5M"}

    def quote(self, symbol: str, bid: float, ask: float, timestamp: str | None = None) -> Quote:
        if symbol != "EURUSD":
            raise ValueError("only EURUSD is supported")
        if bid <= 0 or ask <= 0 or ask < bid:
            raise ValueError("invalid bid/ask")
        return Quote(symbol, bid, ask, timestamp or datetime.utcnow().isoformat() + "Z")

    def candle(self, symbol: str, timeframe: str, *, open: float, high: float, low: float,
               close: float, volume: float = 0.0, timestamp: str) -> Candle:
        if symbol != "EURUSD":
            raise ValueError("only EURUSD is supported")
        if timeframe not in self.SUPPORTED_TIMEFRAMES:
            raise ValueError(f"unsupported timeframe: {timeframe}")
        if min(open, high, low, close) <= 0 or high < max(open, close) or low > min(open, close):
            raise ValueError("invalid OHLC")
        return Candle(symbol, timeframe, timestamp, open, high, low, close, volume)
