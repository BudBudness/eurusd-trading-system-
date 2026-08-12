from runtime.pipeline import MarketSnapshot, run_paper_cycle
from runtime.policy import TradingPolicy
from runtime.state import StateStore


def test_normal_market_produces_paper_fill():
    state = StateStore()
    policy = TradingPolicy()
    result = run_paper_cycle(state, policy, MarketSnapshot("EURUSD", 1.1600, 1.1601))
    assert result["status"] == "filled"
    assert result["fill"]["mode"] == "paper"
    assert result["fill"]["status"] == "filled"


def test_extreme_volatility_halts_new_entry():
    state = StateStore()
    policy = TradingPolicy()
    result = run_paper_cycle(state, policy, MarketSnapshot("EURUSD", 1.1600, 1.1601, "extreme"))
    assert result == {"status": "halted", "reason": "extreme_volatility"}
    assert state.events[-1].type == "ENTRY_HALTED"


def test_non_eurusd_is_rejected():
    state = StateStore()
    policy = TradingPolicy()
    try:
        run_paper_cycle(state, policy, MarketSnapshot("GBPUSD", 1.34, 1.3401))
    except ValueError as exc:
        assert str(exc) == "only EURUSD is supported"
    else:
        raise AssertionError("non-EURUSD symbol was accepted")
