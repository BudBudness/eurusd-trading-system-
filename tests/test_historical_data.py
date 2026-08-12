import tempfile
from pathlib import Path
from runtime.historical_data import HistoricalCSVLoader, validate_dataset

CSV = """timestamp,bid,ask,open_4h,high_4h,low_4h,close_4h,open_1h,high_1h,low_1h,close_1h,open_15m,high_15m,low_15m,close_15m,open_5m,high_5m,low_5m,close_5m
2026-08-12T10:00:00Z,1.1000,1.1001,1.100,1.101,1.099,1.100,1.101,1.102,1.100,1.101,1.102,1.103,1.101,1.102,1.103,1.104,1.102,1.103
2026-08-12T10:05:00Z,1.1001,1.1002,1.100,1.101,1.099,1.100,1.101,1.102,1.100,1.101,1.102,1.103,1.101,1.102,1.103,1.104,1.102,1.103
"""

def test_load_and_validate_csv():
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "eurusd.csv"
        p.write_text(CSV)
        dataset = HistoricalCSVLoader().load(p)
        validate_dataset(dataset)
        assert len(dataset.quotes) == 2
        assert set(dataset.candles_by_time) == {"2026-08-12T10:00:00Z", "2026-08-12T10:05:00Z"}
        assert len(dataset.candles_by_time["2026-08-12T10:00:00Z"]) == 4
