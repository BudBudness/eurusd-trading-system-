from dataclasses import dataclass
from .market_data import Candle, Quote


@dataclass(frozen=True)
class MarketState:
    quote: Quote
    candles: dict[str, Candle]

    @property
    def spread(self) -> float:
        return self.quote.spread

    @property
    def mid(self) -> float:
        return self.quote.mid

    def close(self, timeframe: str) -> float:
        return self.candles[timeframe].close


def build_market_state(quote: Quote, candles: list[Candle]) -> MarketState:
    if quote.symbol != "EURUSD":
        raise ValueError("only EURUSD is supported")
    by_tf = {c.timeframe: c for c in candles}
    return MarketState(quote=quote, candles=by_tf)
