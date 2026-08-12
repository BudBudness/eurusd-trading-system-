from runtime.broker_model import BrokerMode, BrokerModel, BrokerPolicy
from runtime.liquidity_model import LiquidityProvider
from runtime.market_data import MarketDataNormalizer
from runtime.risk import RiskDecision
from runtime.strategy import Signal


def setup():
    q = MarketDataNormalizer().quote("EURUSD", 1.1000, 1.1001)
    signal = Signal("EURUSD", "LONG", "5M", "test")
    risk = RiskDecision(True, "approved", 1000)
    lp = LiquidityProvider("LP1", "Simulated LP", available_units=10000)
    return q, signal, risk, [lp]


def test_normal_broker_execution():
    q, signal, risk, providers = setup()
    result = BrokerModel().execute(signal, risk, q, providers)
    assert result.status == "FILLED"
    assert result.quote.symbol == "EURUSD"


def test_extreme_market_is_rejected():
    q, signal, risk, providers = setup()
    result = BrokerModel().execute(signal, risk, q, providers, BrokerMode.EXTREME)
    assert result.status == "REJECTED"
    assert "extreme" in result.reason


def test_partial_fill_policy():
    q, signal, risk, _ = setup()
    providers = [LiquidityProvider("LP1", "Thin LP", available_units=100)]
    result = BrokerModel(BrokerPolicy(allow_partial_fills=True)).execute(signal, risk, q, providers)
    assert result.status == "PARTIAL"
    assert result.routed.filled_units == 100
