from runtime.liquidity_model import LiquidityProvider, LiquidityRouter, LiquidityTier
from runtime.market_data import MarketDataNormalizer
from runtime.strategy import Signal


def setup():
    q = MarketDataNormalizer().quote("EURUSD", 1.1000, 1.1001)
    return q, Signal("EURUSD", "LONG", "5M", "test")


def test_routes_to_available_provider():
    q, signal = setup()
    provider = LiquidityProvider("LP1", "Simulated LP", LiquidityTier.NORMAL, 5000, .00001)
    result = LiquidityRouter().route(signal, q, 1000, [provider])
    assert result.status == "FILLED"
    assert result.provider_id == "LP1"
    assert result.filled_units == 1000
    assert result.fill_price == 1.10011


def test_finite_liquidity_produces_partial_fill():
    q, signal = setup()
    provider = LiquidityProvider("LP1", "Thin LP", LiquidityTier.THIN, 500, 0)
    result = LiquidityRouter().route(signal, q, 1000, [provider])
    assert result.status == "PARTIAL"
    assert result.filled_units == 500


def test_disconnected_provider_produces_no_liquidity():
    q, signal = setup()
    provider = LiquidityProvider("LP1", "Disconnected LP", LiquidityTier.DISCONNECTED, 1_000_000)
    result = LiquidityRouter().route(signal, q, 1000, [provider])
    assert result.status == "NO_LIQUIDITY"
    assert result.fill_price is None
