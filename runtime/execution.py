from dataclasses import dataclass
from datetime import datetime, timezone

from .market_data import Quote
from .strategy import Signal
from .risk import RiskDecision


@dataclass(frozen=True)
class Order:
    order_id: str
    symbol: str
    direction: str
    units: int
    requested_price: float
    created_at: str


@dataclass(frozen=True)
class Fill:
    order_id: str
    fill_price: float
    units: int
    slippage: float
    spread: float
    latency_ms: int
    filled_at: str


class PaperExecutionEngine:
    """Deterministic paper broker. Never connects to a live broker."""

    def __init__(self, slippage: float = 0.0, latency_ms: int = 50):
        if slippage < 0 or latency_ms < 0:
            raise ValueError("slippage and latency must be non-negative")
        self.slippage = slippage
        self.latency_ms = latency_ms
        self._counter = 0

    def submit(self, signal: Signal, risk: RiskDecision, quote: Quote) -> tuple[Order, Fill]:
        if not risk.approved:
            raise ValueError("cannot execute a rejected risk decision")
        if signal.symbol != "EURUSD" or quote.symbol != "EURUSD":
            raise ValueError("only EURUSD is supported")

        self._counter += 1
        now = datetime.now(timezone.utc).isoformat()
        requested = quote.ask if signal.direction == "LONG" else quote.bid
        signed_slippage = self.slippage if signal.direction == "LONG" else -self.slippage
        slippage = round(signed_slippage, 5)
        fill_price = round(requested + slippage, 5)
        order = Order(f"PAPER-EURUSD-{self._counter:06d}", "EURUSD", signal.direction, risk.units, requested, now)
        fill = Fill(order.order_id, fill_price, risk.units, slippage, quote.spread, self.latency_ms, now)
        return order, fill
