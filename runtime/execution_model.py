from dataclasses import dataclass
from enum import Enum
from .market_data import Quote
from .strategy import Signal
from .risk import RiskDecision


class VolatilityMode(str, Enum):
    NORMAL = "normal"
    ELEVATED = "elevated"
    EXTREME = "extreme"


@dataclass(frozen=True)
class ExecutionConditions:
    mode: VolatilityMode = VolatilityMode.NORMAL
    spread_multiplier: float = 1.0
    slippage_multiplier: float = 1.0
    reject_orders: bool = False


@dataclass(frozen=True)
class ExecutionReport:
    order_id: str
    requested_price: float
    fill_price: float | None
    spread: float
    slippage: float | None
    latency_ms: int
    status: str
    reason: str


class BrokerExecutionModel:
    """Simulation-only model for studying broker execution behaviour."""

    def __init__(self, base_latency_ms: int = 50, base_slippage: float = 0.0):
        self.base_latency_ms = base_latency_ms
        self.base_slippage = base_slippage
        self._counter = 0

    def execute(self, signal: Signal, risk: RiskDecision, quote: Quote,
                conditions: ExecutionConditions | None = None) -> ExecutionReport:
        if not risk.approved:
            raise ValueError("cannot execute a rejected risk decision")
        conditions = conditions or ExecutionConditions()
        self._counter += 1
        order_id = f"MODEL-EURUSD-{self._counter:06d}"
        requested = quote.ask if signal.direction == "LONG" else quote.bid
        effective_spread = quote.spread * conditions.spread_multiplier

        if conditions.reject_orders:
            return ExecutionReport(order_id, requested, None, effective_spread, None,
                                   self.base_latency_ms, "REJECTED", "execution conditions rejected order")

        slip = self.base_slippage * conditions.slippage_multiplier
        if signal.direction == "SHORT":
            slip = -slip
        fill = requested + slip
        return ExecutionReport(order_id, requested, fill, effective_spread,
                               slip, self.base_latency_ms, "FILLED", conditions.mode.value)
