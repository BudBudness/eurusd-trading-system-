from dataclasses import dataclass
from enum import Enum
from .market_data import Quote
from .strategy import Signal
from .risk import RiskDecision
from .liquidity_model import LiquidityProvider, LiquidityRouter, RoutedLiquidity


class BrokerMode(str, Enum):
    NORMAL = "normal"
    WIDE_MARKET = "wide_market"
    EXTREME = "extreme"


@dataclass(frozen=True)
class BrokerPolicy:
    name: str = "simulated-broker"
    spread_markup: float = 0.0
    max_spread: float = 0.00030
    allow_partial_fills: bool = True
    reject_on_extreme: bool = True
    slippage_cap: float = 0.00100


@dataclass(frozen=True)
class BrokerQuote:
    symbol: str
    raw_bid: float
    raw_ask: float
    bid: float
    ask: float
    spread: float


@dataclass(frozen=True)
class BrokerResult:
    status: str
    reason: str
    broker: str
    quote: BrokerQuote
    routed: RoutedLiquidity | None


class BrokerModel:
    """Simulation-only broker layer. It does not represent Pepperstone's private routing rules."""

    def __init__(self, policy: BrokerPolicy | None = None):
        self.policy = policy or BrokerPolicy()
        self.router = LiquidityRouter()

    def quote(self, raw: Quote, mode: BrokerMode = BrokerMode.NORMAL) -> BrokerQuote:
        markup = self.policy.spread_markup
        if mode == BrokerMode.WIDE_MARKET:
            markup *= 3
        if mode == BrokerMode.EXTREME:
            markup *= 10
        bid = raw.bid - markup / 2
        ask = raw.ask + markup / 2
        return BrokerQuote(raw.symbol, raw.bid, raw.ask, bid, ask, ask - bid)

    def execute(self, signal: Signal, risk: RiskDecision, raw: Quote,
                providers: list[LiquidityProvider], mode: BrokerMode = BrokerMode.NORMAL) -> BrokerResult:
        broker_quote = self.quote(raw, mode)
        if mode == BrokerMode.EXTREME and self.policy.reject_on_extreme:
            return BrokerResult("REJECTED", "extreme-volatility policy", self.policy.name, broker_quote, None)
        if broker_quote.spread > self.policy.max_spread:
            return BrokerResult("REJECTED", "broker spread policy", self.policy.name, broker_quote, None)
        routed = self.router.route(signal, broker_quote_to_quote(broker_quote), risk.units, providers)
        if routed.status == "PARTIAL" and not self.policy.allow_partial_fills:
            return BrokerResult("REJECTED", "partial fills disabled", self.policy.name, broker_quote, routed)
        return BrokerResult(routed.status, "broker execution model", self.policy.name, broker_quote, routed)


def broker_quote_to_quote(q: BrokerQuote) -> Quote:
    return Quote(q.symbol, q.bid, q.ask, "")
