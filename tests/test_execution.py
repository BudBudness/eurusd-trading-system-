from runtime.execution import PaperExecutionEngine
from runtime.market_data import MarketDataNormalizer
from runtime.market_state import build_market_state
from runtime.strategy import EURUSDStrategy
from runtime.risk import RiskEngine


def setup_trade():
    n = MarketDataNormalizer()
    q = n.quote("EURUSD", 1.1000, 1.1001, "2026-08-12T10:00:00Z")
    prices = {"4H": 1.1000, "1H": 1.1010, "15M": 1.1020, "5M": 1.1030}
    candles = [n.candle("EURUSD", tf, open=p, high=p+.001, low=p-.001, close=p, timestamp="2026-08-12T10:00:00Z") for tf, p in prices.items()]
    state = build_market_state(q, candles)
    signal = EURUSDStrategy().evaluate(state)
    risk = RiskEngine().approve(signal, equity=10000, stop_distance=.001, spread=state.spread)
    return q, signal, risk


def test_paper_execution_records_slippage_and_spread():
    q, signal, risk = setup_trade()
    order, fill = PaperExecutionEngine(slippage=.00002, latency_ms=75).submit(signal, risk, q)
    assert order.order_id.startswith("PAPER-EURUSD-")
    assert fill.units == risk.units
    assert fill.spread == q.spread
    assert fill.slippage == .00002
    assert fill.latency_ms == 75


def test_rejected_risk_cannot_execute():
    q, signal, _ = setup_trade()
    from runtime.risk import RiskDecision
    rejected = RiskDecision(False, "blocked")
    try:
        PaperExecutionEngine().submit(signal, rejected, q)
    except ValueError as exc:
        assert "rejected" in str(exc)
    else:
        raise AssertionError("rejected trade was executed")
