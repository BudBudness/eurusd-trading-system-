from runtime.execution_model import BrokerExecutionModel, ExecutionConditions, VolatilityMode
from runtime.market_data import MarketDataNormalizer
from runtime.risk import RiskDecision
from runtime.strategy import Signal


def setup():
    n = MarketDataNormalizer()
    q = n.quote("EURUSD", 1.1000, 1.1001)
    signal = Signal("EURUSD", "LONG", "5M", "test")
    risk = RiskDecision(True, "approved", 1000)
    return q, signal, risk


def test_normal_execution():
    q, signal, risk = setup()
    report = BrokerExecutionModel(base_slippage=.00001).execute(signal, risk, q)
    assert report.status == "FILLED"
    assert report.fill_price == report.requested_price + .00001


def test_extreme_volatility_rejects_order():
    q, signal, risk = setup()
    conditions = ExecutionConditions(mode=VolatilityMode.EXTREME, spread_multiplier=5.0,
                                    slippage_multiplier=10.0, reject_orders=True)
    report = BrokerExecutionModel(base_slippage=.00001).execute(signal, risk, q, conditions)
    assert report.status == "REJECTED"
    assert report.fill_price is None
    assert report.spread == q.spread * 5.0


def test_elevated_volatility_models_wider_slippage():
    q, signal, risk = setup()
    conditions = ExecutionConditions(mode=VolatilityMode.ELEVATED, spread_multiplier=2.0,
                                    slippage_multiplier=3.0)
    report = BrokerExecutionModel(base_slippage=.00001).execute(signal, risk, q, conditions)
    assert report.status == "FILLED"
    assert report.spread == q.spread * 2.0
    assert report.slippage == .00003
