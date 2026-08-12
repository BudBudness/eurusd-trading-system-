from dataclasses import dataclass
from typing import Any

from .models import Event
from .policy import TradingPolicy
from .state import StateStore


@dataclass(frozen=True)
class MarketSnapshot:
    symbol: str
    bid: float
    ask: float
    volatility: str = "normal"

    @property
    def spread(self) -> float:
        return round(self.ask - self.bid, 10)


@dataclass(frozen=True)
class TradeProposal:
    symbol: str
    side: str
    entry: float
    stop: float
    target: float
    risk_pct: float


class PaperExecution:
    """Deterministic paper executor. Never sends broker orders."""

    def execute(self, proposal: TradeProposal, policy: TradingPolicy) -> dict[str, Any]:
        if policy.live_execution_enabled:
            raise RuntimeError("paper executor cannot be used when live execution is enabled")
        return {
            "mode": "paper",
            "symbol": proposal.symbol,
            "side": proposal.side,
            "requested_entry": proposal.entry,
            "simulated_fill": proposal.entry,
            "slippage": 0.0,
            "status": "filled",
        }


def run_paper_cycle(state: StateStore, policy: TradingPolicy, snapshot: MarketSnapshot) -> dict[str, Any]:
    if snapshot.symbol != policy.instrument:
        raise ValueError("only EURUSD is supported")
    if snapshot.volatility == "extreme":
        state.emit(Event("ENTRY_HALTED", "WU-EURUSD-001", actor="risk", payload={"reason": "extreme_volatility"}))
        return {"status": "halted", "reason": "extreme_volatility"}

    entry = (snapshot.bid + snapshot.ask) / 2
    proposal = TradeProposal(
        symbol="EURUSD",
        side="BUY",
        entry=entry,
        stop=entry - 0.0010,
        target=entry + 0.0020,
        risk_pct=policy.max_trade_risk_pct,
    )
    state.emit(Event("SIGNAL_CREATED", "WU-EURUSD-001", task_id="T002", actor="strategy",
                     payload={"side": proposal.side, "entry": proposal.entry}))
    state.emit(Event("RISK_APPROVED", "WU-EURUSD-001", task_id="T003", actor="risk",
                     payload={"risk_pct": proposal.risk_pct}))
    fill = PaperExecution().execute(proposal, policy)
    state.emit(Event("PAPER_FILL_RECEIVED", "WU-EURUSD-001", task_id="T004", actor="execution", payload=fill))
    return {"status": "filled", "proposal": proposal, "fill": fill}
