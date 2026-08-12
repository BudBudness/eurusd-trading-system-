from dataclasses import dataclass

@dataclass(frozen=True)
class CTraderConfig:
    environment: str = "demo"
    symbol: str = "EURUSD"

class CTraderAdapter:
    """Boundary only. Network/API execution is intentionally not implemented."""
    def __init__(self, config=None): self.config = config or CTraderConfig()
    def connect(self):
        if self.config.environment != "demo": raise RuntimeError("only demo environment is permitted")
        return False
    def submit(self, *args, **kwargs):
        raise RuntimeError("cTrader network execution is not implemented; use paper execution")
