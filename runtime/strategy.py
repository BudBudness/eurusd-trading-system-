from dataclasses import dataclass
from .market_state import MarketState


@dataclass(frozen=True)
class Signal:
    symbol: str
    direction: str
    timeframe: str
    reason: str


class EURUSDStrategy:
    """Deterministic starter strategy; intentionally conservative and research-only."""

    def evaluate(self, state: MarketState) -> Signal | None:
        required = {"4H", "1H", "15M", "5M"}
        if not required.issubset(state.candles):
            return None

        h4 = state.close("4H")
        h1 = state.close("1H")
        m15 = state.close("15M")
        m5 = state.close("5M")

        if h4 < h1 < m15 < m5:
            return Signal("EURUSD", "LONG", "5M", "multi-timeframe bullish alignment")
        if h4 > h1 > m15 > m5:
            return Signal("EURUSD", "SHORT", "5M", "multi-timeframe bearish alignment")
        return None
