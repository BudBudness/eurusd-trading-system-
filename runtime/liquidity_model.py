from dataclasses import dataclass
from enum import Enum
from .market_data import Quote
from .strategy import Signal


class LiquidityTier(str, Enum):
    DEEP = "deep"
    NORMAL = "normal"
    THIN = "thin"
    DISCONNECTED = "disconnected"


@dataclass(frozen=True)
class LiquidityProvider:
    provider_id: str
    name: str
    tier: LiquidityTier = LiquidityTier.NORMAL
    available_units: int = 1_000_000
    price_offset: float = 0.0


@dataclass(frozen=True)
class RoutedLiquidity:
    provider_id: str
    requested_units: int
    filled_units: int
    requested_price: float
    fill_price: float | None
    status: str


class LiquidityRouter:
    """Simulation-only abstraction for provider routing and finite liquidity."""

    def route(self, signal: Signal, quote: Quote, units: int,
              providers: list[LiquidityProvider]) -> RoutedLiquidity:
        if signal.symbol != "EURUSD" or quote.symbol != "EURUSD":
            raise ValueError("only EURUSD is supported")
        if units <= 0:
            raise ValueError("units must be positive")
        if not providers:
            return RoutedLiquidity("NONE", units, 0, quote.ask if signal.direction == "LONG" else quote.bid, None, "NO_LIQUIDITY")

        available = [p for p in providers if p.tier != LiquidityTier.DISCONNECTED and p.available_units > 0]
        if not available:
            return RoutedLiquidity("NONE", units, 0, quote.ask if signal.direction == "LONG" else quote.bid, None, "NO_LIQUIDITY")

        provider = max(available, key=lambda p: p.available_units)
        requested = quote.ask if signal.direction == "LONG" else quote.bid
        filled = min(units, provider.available_units)
        if filled < units:
            status = "PARTIAL"
        else:
            status = "FILLED"
        signed_offset = provider.price_offset if signal.direction == "LONG" else -provider.price_offset
        return RoutedLiquidity(provider.provider_id, units, filled, requested,
                                requested + signed_offset if filled else None, status)
