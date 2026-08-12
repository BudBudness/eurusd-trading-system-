# EUR/USD Trading System — Dukascopy Migration Report

## 1. Decision

Replace Pepperstone/cTrader as the canonical market-data provider with Dukascopy.

Dukascopy is the sole canonical source for EUR/USD historical market data in v1.

## 2. Baseline

- Historical normalization/integrity: CI #45 PASS.
- Execution arithmetic/slippage correction: CI #46 PASS.
- Verified execution correction commit: `8d0de2ff5826d557f21cfc7ef736b0fed51756f7`.
- Backtest remains locked until the real dataset passes its integrity gate.

## 3. Target architecture

```text
Dukascopy tick + M1
        |
        v
raw immutable artifacts
        |
        v
UTC normalization
        |
        v
M1 canonical dataset
        |
        +--> M5
        +--> M15
        +--> H1
        +--> H4
        |
        v
validation + SHA-256
        |
        v
immutable manifest
        |
        v
backtest gate
```

## 4. Provider migration

### Remove

- Pepperstone-specific configuration.
- cTrader market-data dependency.
- cTrader historical-data assumptions.
- cTrader-specific symbol/time semantics.

### Replace

- `runtime/dukascopy_adapter.py` is the provider boundary.
- `data/historical/dukascopy/` is the canonical historical-data namespace.
- Raw TICK and M1 are retained as provenance/base feeds.

## 5. Canonical dataset

Instrument: `EURUSD`

Timezone: `UTC`

Base bar timeframe: `M1`

Derived timeframes: `M5`, `M15`, `H1`, `H4`

Tick data is retained separately for execution/microstructure provenance.

## 6. Integrity requirements

Every acquisition must record:

- source/provider
- instrument
- timeframe
- acquisition timestamp
- first timestamp
- last timestamp
- row count
- duplicate count
- ordering errors
- invalid OHLC count
- invalid price count
- unexpected gaps
- raw SHA-256
- normalized SHA-256
- normalizer version
- resampler version
- schema version

## 7. OHLC invariants

For every canonical bar:

```text
high >= max(open, close)
low  <= min(open, close)
high >= low
open  > 0
high  > 0
low   > 0
close > 0
```

## 8. Resampling policy

M1 is the only canonical bar layer.

For each derived timeframe:

```text
open  = first M1 open
high  = maximum M1 high
low   = minimum M1 low
close = last M1 close
volume = sum M1 volume
```

The transformation must be deterministic and timezone-aware.

## 9. Immutability

Raw files must never be modified after acquisition.

A changed source or transformation creates a new dataset version rather than mutating an existing dataset.

## 10. Backtest gate

The backtest is unlocked only when all of these pass:

- source validation
- raw integrity
- UTC normalization
- ordering
- duplicate audit
- OHLC validation
- gap audit
- deterministic resampling
- SHA-256 generation
- manifest generation
- immutability verification

## 11. Execution preservation

The provider migration must not alter the execution arithmetic already verified by CI #46, including deterministic slippage handling and normalized simulated fill prices.

## 12. Live execution boundary

Dukascopy historical data and a Dukascopy execution/account interface are separate concerns. Historical-data migration does not authorize live execution. Live trading remains disabled until an explicit production gate is implemented and passed.

## 13. Acquisition record

To be completed when the real dataset is acquired:

```yaml
dataset_id:
provider: Dukascopy
instrument: EURUSD
base_timeframe: M1
start_timestamp:
end_timestamp:
raw_sha256:
normalized_sha256:
manifest_sha256:
row_count:
duplicate_count:
ordering_errors:
invalid_ohlc:
unexpected_gaps:
validation: PENDING
```

## 14. Status

| Gate | Status |
|---|---|
| CI #45 historical integrity | PASS |
| CI #46 execution correction | PASS |
| Dukascopy provider boundary | IMPLEMENTED |
| Dukascopy dataset namespace | IMPLEMENTED |
| Validation primitives | IMPLEMENTED |
| Deterministic resampling | IMPLEMENTED |
| Real EUR/USD acquisition | PENDING |
| Dataset manifest | PENDING |
| Immutable dataset gate | PENDING |
| Backtest | LOCKED |
