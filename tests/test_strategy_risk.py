from runtime.market_data import MarketDataNormalizer
from runtime.market_state import build_market_state
from runtime.strategy import EURUSDStrategy
from runtime.risk import RiskEngine


def state():
    n = MarketDataNormalizer()
    q = n.quote("EURUSD", 1.1000, 1.1001, "2026-08-12T10:00:00Z")
    prices = {"4H": 1.1000, "1H": 1.1010, "15M": 1.1020, "5M": 1.1030}
    candles = [n.candle("EURUSD", tf, open=p, high=p+.001, low=p-.001, close=p, timestamp="2026-08-12T10:00:00Z") for tf, p in prices.items()]
    return build_market_state(q, candles)


def test_strategy_detects_bullish_alignment():
    signal = EURUSDStrategy().evaluate(state())
    assert signal is not None
    assert signal.direction == "LONG"


def test_risk_approves_valid_signal():
    s = state()
    signal = EURUSDStrategy().evaluate(s)
    decision = RiskEngine().approve(signal, equity=10000, stop_distance=0.0010, spread=s.spread)
    assert decision.approved is True
    assert decision.units > 0


def test_risk_rejects_wide_spread():
    s = state()
    signal = EURUSDStrategy().evaluate(s)
    decision = RiskEngine(max_spread=0.00005).approve(signal, equity=10000, stop_distance=0.001, spread=s.spread)
    assert decision.approved is False
