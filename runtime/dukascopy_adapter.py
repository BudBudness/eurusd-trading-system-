from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DukascopyConfig:
    """Configuration for the canonical Dukascopy data boundary.

    Network acquisition is intentionally kept separate from the runtime
    execution engine. Raw source artifacts must be preserved before parsing.
    """

    symbol: str = "EURUSD"
    timezone: str = "UTC"
    raw_root: Path = Path("data/historical/dukascopy/EURUSD/raw")


class DukascopyAdapter:
    """Provider boundary for Dukascopy EUR/USD market data.

    This adapter owns provider identity and local raw-data conventions. It
    does not place broker orders. Historical acquisition is performed by the
    dedicated acquisition pipeline so that raw artifacts remain immutable.
    """

    PROVIDER = "dukascopy"
    SUPPORTED_SYMBOLS = {"EURUSD"}
    BASE_TIMEFRAMES = {"TICK", "M1"}
    DERIVED_TIMEFRAMES = {"M5", "M15", "H1", "H4"}

    def __init__(self, config: DukascopyConfig | None = None):
        self.config = config or DukascopyConfig()
        if self.config.symbol not in self.SUPPORTED_SYMBOLS:
            raise ValueError("only EURUSD is supported")
        if self.config.timezone != "UTC":
            raise ValueError("canonical market-data timezone must be UTC")

    def raw_path(self, timeframe: str) -> Path:
        tf = timeframe.upper()
        if tf not in self.BASE_TIMEFRAMES:
            raise ValueError(f"raw Dukascopy timeframe must be TICK or M1: {timeframe}")
        path = self.config.raw_root / tf
        path.mkdir(parents=True, exist_ok=True)
        return path

    def source_metadata(self) -> dict[str, str]:
        return {
            "provider": self.PROVIDER,
            "symbol": self.config.symbol,
            "timezone": self.config.timezone,
            "canonical_base": "M1",
            "tick_retained": "true",
        }
