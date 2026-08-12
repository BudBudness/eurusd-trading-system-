from pathlib import Path
import tempfile
import pytest
from runtime.historical_data import HistoricalCSVLoader, normalize_timestamp


CSV = """timestamp,bid,ask,open_4h,high_4h,low_4h,close_4h,open_1h,high_1h,low_1h,close_1h,open_15m,high_15m,low_15m,close_15m,open_5m,high_5m,low_5m,close_5m
2026-08-12T10:00:00+03:00,1.1000,1.1001,1.100,1.101,1.099,1.100,1.101,1.102,1.100,1.101,1.102,1.103,1.101,1.102,1.103,1.104,1.102,1.103
2026-08-12T10:05:00+03:00,1.1001,1.1002,1.100,1.101,1.099,1.100,1.101,1.102,1.100,1.101,1.102,1.103,1.101,1.102,1.103,1.104,1.102,1.103
"""


def test_loader_normalizes_timezone_and_builds_manifest():
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "eurusd.csv"
        p.write_text(CSV, encoding="utf-8")
        dataset = HistoricalCSVLoader().load(p)
        manifest = HistoricalCSVLoader.manifest(p, dataset)
        assert dataset.quotes[0].timestamp == "2026-08-12T07:00:00Z"
        assert manifest.rows == 2
        assert len(manifest.sha256) == 64


def test_timestamp_requires_timezone():
    with pytest.raises(ValueError, match="timezone"):
        normalize_timestamp("2026-08-12T10:00:00")


def test_loader_rejects_missing_columns():
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "bad.csv"
        p.write_text("timestamp,bid,ask\n2026-08-12T10:00:00Z,1.1,1.2\n", encoding="utf-8")
        with pytest.raises(ValueError, match="missing columns"):
            HistoricalCSVLoader().load(p)
