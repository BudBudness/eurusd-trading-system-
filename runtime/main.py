from .policy import TradingPolicy
from .state import StateStore
from .workflow import TradingWorkflow


def main() -> None:
    policy = TradingPolicy()
    state = StateStore()
    workflow = TradingWorkflow(state, policy)
    workflow.start("WU-EURUSD-001")
    workflow.complete("WU-EURUSD-001")
    print(state.work_units["WU-EURUSD-001"].value)
    for event in state.events:
        print(event.type, event.work_unit_id)


if __name__ == "__main__":
    main()
