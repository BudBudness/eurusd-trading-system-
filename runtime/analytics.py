from dataclasses import dataclass

@dataclass(frozen=True)
class AnalyticsReport:
    signals: int
    approved: int
    fills: int
    rejects: int
    fill_rate: float
    average_slippage: float
    average_spread: float

def summarize(result) -> AnalyticsReport:
    fill_rate = result.fills / result.signals if result.signals else 0.0
    avg_slippage = result.total_slippage / result.fills if result.fills else 0.0
    avg_spread = result.total_spread / result.fills if result.fills else 0.0
    return AnalyticsReport(result.signals, result.approved, result.fills, result.rejects,
                           fill_rate, avg_slippage, avg_spread)
