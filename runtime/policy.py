from dataclasses import dataclass


@dataclass(frozen=True)
class TradingPolicy:
    instrument: str = "EURUSD"
    broker: str = "Pepperstone"
    platform: str = "cTrader"
    max_trade_risk_pct: float = 0.50
    max_daily_loss_pct: float = 2.0
    live_execution_enabled: bool = False

    def validate(self) -> None:
        if self.instrument != "EURUSD":
            raise ValueError("v1 supports EURUSD only")
        if self.max_trade_risk_pct <= 0 or self.max_trade_risk_pct > 1:
            raise ValueError("max_trade_risk_pct must be >0 and <=1")
        if self.max_daily_loss_pct <= 0:
            raise ValueError("max_daily_loss_pct must be positive")
