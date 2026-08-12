from dataclasses import dataclass
from .market_data import Candle
from .market_state import build_market_state
from .strategy import EURUSDStrategy
from .risk import RiskEngine
from .broker_model import BrokerModel, BrokerMode
from .liquidity_model import LiquidityProvider
from .execution import PaperExecutionEngine

@dataclass(frozen=True)
class BacktestResult:
    candles_processed: int
    signals: int
    approved: int
    fills: int
    rejects: int
    total_slippage: float
    total_spread: float

class HistoricalReplay:
    """Deterministic bar replay. Uses supplied historical quotes/candles; no network access."""
    def __init__(self, strategy=None, risk=None, broker=None, executor=None):
        self.strategy = strategy or EURUSDStrategy()
        self.risk = risk or RiskEngine()
        self.broker = broker or BrokerModel()
        self.executor = executor or PaperExecutionEngine()

    def run(self, quotes, candles_by_time, equity=10_000.0, stop_distance=0.001,
            providers=None, mode=BrokerMode.NORMAL):
        providers = providers or [LiquidityProvider("SIM-LP-1", "Historical Replay LP", available_units=10_000_000)]
        signals = approved = fills = rejects = 0
        total_slippage = total_spread = 0.0
        for quote in quotes:
            candles = candles_by_time.get(quote.timestamp)
            if not candles:
                continue
            state = build_market_state(quote, candles)
            signal = self.strategy.evaluate(state)
            if signal is None:
                continue
            signals += 1
            risk = self.risk.approve(signal, equity=equity, stop_distance=stop_distance, spread=state.spread)
            if not risk.approved:
                rejects += 1
                continue
            approved += 1
            broker_result = self.broker.execute(signal, risk, quote, providers, mode)
            if broker_result.status not in {"FILLED", "PARTIAL"}:
                rejects += 1
                continue
            order, fill = self.executor.submit(signal, risk, quote)
            fills += 1
            total_slippage += fill.slippage
            total_spread += fill.spread
        return BacktestResult(len(quotes), signals, approved, fills, rejects, total_slippage, total_spread)
