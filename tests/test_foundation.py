from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]


def test_work_unit_exists():
    manifest = ROOT / "work_units/WU-EURUSD-001/manifest.yaml"
    assert manifest.exists()
    assert "WU-EURUSD-001" in manifest.read_text()


def test_eurusd_only_policy():
    policy = ROOT / "control/policies/trading.yaml"
    text = policy.read_text()
    assert "instrument: EURUSD" in text
    assert "live_trading_enabled: false" in text


def test_schema_files_are_valid_json():
    for path in (ROOT / "control/schemas").glob("*.json"):
        json.loads(path.read_text())


def test_workflow_exists():
    workflow = ROOT / "control/workflows/trading.yaml"
    assert workflow.exists()
    assert "ORDER_SUBMITTED" in workflow.read_text()
