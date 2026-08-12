from dataclasses import dataclass
from enum import Enum

class TradeState(str, Enum):
    OPEN = "OPEN"; CLOSED = "CLOSED"; CANCELLED = "CANCELLED"

@dataclass(frozen=True)
class Trade:
    trade_id: str
    direction: str
    entry: float
    stop_loss: float | None
    take_profit: float | None
    units: int
    state: TradeState = TradeState.OPEN
    exit_price: float | None = None
    pnl: float = 0.0

class TradeLifecycle:
    def close(self, trade: Trade, exit_price: float) -> Trade:
        if trade.state != TradeState.OPEN: raise ValueError("trade is not open")
        sign = 1 if trade.direction == "LONG" else -1
        pnl = (exit_price - trade.entry) * sign * trade.units
        return Trade(trade.trade_id, trade.direction, trade.entry, trade.stop_loss, trade.take_profit,
                     trade.units, TradeState.CLOSED, exit_price, pnl)

    def check_bar(self, trade: Trade, high: float, low: float) -> Trade:
        if trade.state != TradeState.OPEN: return trade
        if trade.direction == "LONG":
            if trade.stop_loss is not None and low <= trade.stop_loss: return self.close(trade, trade.stop_loss)
            if trade.take_profit is not None and high >= trade.take_profit: return self.close(trade, trade.take_profit)
        else:
            if trade.stop_loss is not None and high >= trade.stop_loss: return self.close(trade, trade.stop_loss)
            if trade.take_profit is not None and low <= trade.take_profit: return self.close(trade, trade.take_profit)
        return trade
