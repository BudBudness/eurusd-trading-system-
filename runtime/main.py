from .pipeline import MarketSnapshot, run_paper_cycle
from .policy import TradingPolicy
from .state import StateStore
from .workflow import TradingWorkflow


def main() -> None:
    policy = TradingPolicy()
    policy.validate()
    state = StateStore()
    workflow = TradingWorkflow(state, policy)
    workflow.start("WU-EURUSD-001")

    result = run_paper_cycle(
        state,
        policy,
        MarketSnapshot(symbol="EURUSD", bid=1.16000, ask=1.16010, volatility="normal"),
    )

    workflow.complete("WU-EURUSD-001")
    print({"state": state.work_units["WU-EURUSD-001"].value, "result": result["status"]})
    for event in state.events:
        print(event.type, event.work_unit_id)


if __name__ == "__main__":
    main()
