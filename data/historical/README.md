# Historical EUR/USD data

Place licensed EUR/USD historical datasets here locally. Raw market data is intentionally not committed by the project foundation.

Required CSV schema:

```text
timestamp,bid,ask,open_4h,high_4h,low_4h,close_4h,open_1h,high_1h,low_1h,close_1h,open_15m,high_15m,low_15m,close_15m,open_5m,high_5m,low_5m,close_5m
```

The loader validates EUR/USD-only data, sorted unique timestamps, valid bid/ask values, and OHLC structure.
