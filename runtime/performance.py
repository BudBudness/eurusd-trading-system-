from dataclasses import dataclass
from math import sqrt

@dataclass(frozen=True)
class PerformanceReport:
    trades: int
    wins: int
    losses: int
    net_pnl: float
    gross_profit: float
    gross_loss: float
    win_rate: float
    expectancy: float
    profit_factor: float
    max_drawdown: float
    sharpe: float
    sortino: float

def analyze(pnls: list[float], periods_per_year: int = 252) -> PerformanceReport:
    if not pnls:
        return PerformanceReport(0,0,0,0,0,0,0,0,0,0,0,0)
    wins = [p for p in pnls if p > 0]; losses = [p for p in pnls if p < 0]
    equity = peak = 0.0; max_dd = 0.0
    for p in pnls:
        equity += p; peak = max(peak, equity); max_dd = max(max_dd, peak-equity)
    mean = sum(pnls)/len(pnls)
    variance = sum((p-mean)**2 for p in pnls)/len(pnls)
    downside = [min(0,p) for p in pnls]
    down_var = sum(x*x for x in downside)/len(pnls)
    std = sqrt(variance)
    down_std = sqrt(down_var)
    return PerformanceReport(len(pnls),len(wins),len(losses),sum(pnls),sum(wins),abs(sum(losses)),
        len(wins)/len(pnls),mean,(sum(wins)/abs(sum(losses)) if losses else float('inf')),
        max_dd,(mean/std*sqrt(periods_per_year) if std else 0),(mean/down_std*sqrt(periods_per_year) if down_std else 0))
