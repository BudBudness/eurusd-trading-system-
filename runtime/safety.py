from dataclasses import dataclass

@dataclass
class SafetyController:
    enabled: bool = True
    kill_switch: bool = False
    max_daily_loss: float = 0.02

    def can_trade(self, daily_pnl: float, equity: float) -> bool:
        if not self.enabled or self.kill_switch or equity <= 0: return False
        return daily_pnl > -(equity * self.max_daily_loss)

    def halt(self): self.kill_switch = True
    def resume(self): self.kill_switch = False
