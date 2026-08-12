from runtime.backtest import HistoricalReplay
from runtime.analytics import summarize
from runtime.market_data import MarketDataNormalizer


def test_historical_replay_to_analytics():
    n = MarketDataNormalizer()
    timestamps = [f"2026-08-12T10:0{i}:00Z" for i in range(2)]
    quotes = []
    candles_by_time = {}
    for ts in timestamps:
        q = n.quote("EURUSD", 1.1000, 1.1001, ts)
        quotes.append(q)
        prices = {"4H": 1.1000, "1H": 1.1010, "15M": 1.1020, "5M": 1.1030}
        candles_by_time[ts] = [n.candle("EURUSD", tf, open=p, high=p+.001, low=p-.001, close=p, timestamp=ts) for tf, p in prices.items()]
    result = HistoricalReplay().run(quotes, candles_by_time)
    report = summarize(result)
    assert result.candles_processed == 2
    assert result.signals == 2
    assert result.fills == 2
    assert report.fill_rate == 1.0
