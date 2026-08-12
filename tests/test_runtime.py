import pytest

from runtime.models import WorkUnitStatus
from runtime.policy import TradingPolicy
from runtime.skills import Skill, SkillRegistry
from runtime.state import StateStore
from runtime.workflow import TradingWorkflow


def test_workflow_completes():
    state = StateStore()
    workflow = TradingWorkflow(state, TradingPolicy())
    workflow.start("WU-EURUSD-001")
    assert state.work_units["WU-EURUSD-001"] == WorkUnitStatus.RUNNING
    workflow.complete("WU-EURUSD-001")
    assert state.work_units["WU-EURUSD-001"] == WorkUnitStatus.COMPLETED


def test_invalid_transition_is_rejected():
    state = StateStore()
    state.create("WU-EURUSD-002")
    with pytest.raises(ValueError):
        state.transition("WU-EURUSD-002", WorkUnitStatus.COMPLETED)


def test_skill_registry_executes_reusable_capability():
    registry = SkillRegistry()
    registry.register(Skill("identity", "1.0.0", lambda p: {"value": p["value"]}))
    assert registry.run("identity", {"value": "EURUSD"}) == {"value": "EURUSD"}


def test_live_execution_is_disabled_by_default():
    assert TradingPolicy().live_execution_enabled is False
