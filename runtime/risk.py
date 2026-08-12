from dataclasses import dataclass
from .strategy import Signal


@dataclass(frozen=True)
class RiskDecision:
    approved: bool
    reason: str
    units: int = 0


class RiskEngine:
    def __init__(self, max_risk_fraction: float = 0.005, max_spread: float = 0.0003):
        if not 0 < max_risk_fraction <= 0.02:
            raise ValueError("max_risk_fraction must be between 0 and 2%")
        self.max_risk_fraction = max_risk_fraction
        self.max_spread = max_spread

    def approve(self, signal: Signal | None, *, equity: float, stop_distance: float, spread: float) -> RiskDecision:
        if signal is None:
            return RiskDecision(False, "no signal")
        if spread > self.max_spread:
            return RiskDecision(False, "spread exceeds policy")
        if equity <= 0 or stop_distance <= 0:
            return RiskDecision(False, "invalid account or stop distance")
        risk_cash = equity * self.max_risk_fraction
        units = int(risk_cash / stop_distance)
        if units < 1:
            return RiskDecision(False, "minimum position size cannot be satisfied")
        return RiskDecision(True, "risk checks passed", units)
