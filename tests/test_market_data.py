from runtime.market_data import MarketDataNormalizer
from runtime.market_state import build_market_state


def test_quote_and_candles_normalize():
    n = MarketDataNormalizer()
    q = n.quote("EURUSD", 1.1000, 1.1001, "2026-08-12T10:00:00Z")
    candles = [
        n.candle("EURUSD", tf, open=1.1, high=1.102, low=1.099, close=1.101, timestamp="2026-08-12T10:00:00Z")
        for tf in ("4H", "1H", "15M", "5M")
    ]
    state = build_market_state(q, candles)
    assert state.mid == 1.10005
    assert state.spread == 0.0001
    assert state.close("5M") == 1.101


def test_rejects_non_eurusd():
    n = MarketDataNormalizer()
    try:
        n.quote("GBPUSD", 1.3, 1.3001)
    except ValueError as exc:
        assert "EURUSD" in str(exc)
    else:
        raise AssertionError("non-EURUSD quote was accepted")
