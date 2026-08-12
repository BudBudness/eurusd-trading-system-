from .models import Event, WorkUnitStatus
from .policy import TradingPolicy
from .state import StateStore


class TradingWorkflow:
    def __init__(self, state: StateStore, policy: TradingPolicy) -> None:
        self.state = state
        self.policy = policy
        self.policy.validate()

    def start(self, work_unit_id: str) -> None:
        if work_unit_id not in self.state.work_units:
            self.state.create(work_unit_id)
        self.state.transition(work_unit_id, WorkUnitStatus.READY)
        self.state.transition(work_unit_id, WorkUnitStatus.RUNNING)
        self.state.emit(Event("WORKFLOW_STARTED", work_unit_id, actor="workflow"))

    def complete(self, work_unit_id: str) -> None:
        self.state.transition(work_unit_id, WorkUnitStatus.COMPLETED, actor="workflow")
        self.state.emit(Event("WORKFLOW_COMPLETED", work_unit_id, actor="workflow"))
