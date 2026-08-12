from dataclasses import dataclass, asdict
import json
from .historical_data import HistoricalDataset
from .replay import ReplayEngine
from .strategy import EURUSDStrategy
from .risk import RiskEngine
from .broker_model import BrokerModel, BrokerMode
from .liquidity_model import LiquidityProvider
from .execution import PaperExecutionEngine

@dataclass(frozen=True)
class TradeRecord:
    timestamp: str
    direction: str
    units: int
    requested_price: float
    fill_price: float
    slippage: float
    spread: float
    execution_status: str

@dataclass(frozen=True)
class BacktestReport:
    frames: int
    signals: int
    approved: int
    rejected: int
    fills: int
    total_slippage: float
    average_slippage: float
    average_spread: float
    trades: tuple[TradeRecord, ...]

class EndToEndBacktest:
    def __init__(self, strategy=None, risk=None, broker=None, executor=None):
        self.strategy = strategy or EURUSDStrategy()
        self.risk = risk or RiskEngine()
        self.broker = broker or BrokerModel()
        self.executor = executor or PaperExecutionEngine()

    def run(self, dataset: HistoricalDataset, equity=10_000.0, stop_distance=0.001,
            providers=None, mode=BrokerMode.NORMAL) -> BacktestReport:
        providers = providers or [LiquidityProvider("SIM-LP-1", "Historical Replay LP", available_units=10_000_000)]
        frames = signals = approved = rejected = fills = 0
        total_slippage = total_spread = 0.0
        trades = []
        for frame in ReplayEngine().frames(dataset):
            frames += 1
            from .market_state import build_market_state
            state = build_market_state(frame.quote, frame.candles)
            signal = self.strategy.evaluate(state)
            if signal is None:
                continue
            signals += 1
            decision = self.risk.approve(signal, equity=equity, stop_distance=stop_distance, spread=state.spread)
            if not decision.approved:
                rejected += 1
                continue
            approved += 1
            broker_result = self.broker.execute(signal, decision, frame.quote, providers, mode)
            if broker_result.status not in {"FILLED", "PARTIAL"}:
                rejected += 1
                continue
            order, fill = self.executor.submit(signal, decision, frame.quote)
            fills += 1
            total_slippage += fill.slippage
            total_spread += fill.spread
            trades.append(TradeRecord(frame.timestamp, signal.direction, fill.units,
                                      order.requested_price, fill.fill_price, fill.slippage,
                                      fill.spread, broker_result.status))
        return BacktestReport(frames, signals, approved, rejected, fills, total_slippage,
                              total_slippage / fills if fills else 0.0,
                              total_spread / fills if fills else 0.0, tuple(trades))

def report_json(report: BacktestReport) -> str:
    return json.dumps(asdict(report), indent=2)
