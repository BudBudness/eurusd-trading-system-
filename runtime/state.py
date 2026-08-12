from dataclasses import dataclass, field
from .models import Event, WorkUnitStatus


_ALLOWED = {
    WorkUnitStatus.CREATED: {WorkUnitStatus.READY, WorkUnitStatus.CANCELLED},
    WorkUnitStatus.READY: {WorkUnitStatus.RUNNING, WorkUnitStatus.BLOCKED, WorkUnitStatus.CANCELLED},
    WorkUnitStatus.RUNNING: {WorkUnitStatus.WAITING, WorkUnitStatus.COMPLETED, WorkUnitStatus.FAILED, WorkUnitStatus.BLOCKED},
    WorkUnitStatus.WAITING: {WorkUnitStatus.RUNNING, WorkUnitStatus.FAILED, WorkUnitStatus.CANCELLED},
    WorkUnitStatus.BLOCKED: {WorkUnitStatus.READY, WorkUnitStatus.CANCELLED},
    WorkUnitStatus.FAILED: {WorkUnitStatus.READY, WorkUnitStatus.CANCELLED},
    WorkUnitStatus.COMPLETED: set(),
    WorkUnitStatus.CANCELLED: set(),
}


@dataclass
class StateStore:
    work_units: dict[str, WorkUnitStatus] = field(default_factory=dict)
    events: list[Event] = field(default_factory=list)

    def create(self, work_unit_id: str) -> None:
        if work_unit_id in self.work_units:
            raise ValueError(f"work unit already exists: {work_unit_id}")
        self.work_units[work_unit_id] = WorkUnitStatus.CREATED
        self.emit(Event("WORK_UNIT_CREATED", work_unit_id))

    def transition(self, work_unit_id: str, target: WorkUnitStatus, actor: str = "runtime") -> None:
        current = self.work_units[work_unit_id]
        if target not in _ALLOWED[current]:
            raise ValueError(f"invalid transition: {current.value} -> {target.value}")
        self.work_units[work_unit_id] = target
        self.emit(Event("STATE_CHANGED", work_unit_id, actor=actor,
                        payload={"from": current.value, "to": target.value}))

    def emit(self, event: Event) -> None:
        self.events.append(event)
