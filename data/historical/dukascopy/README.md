# Dukascopy Historical EUR/USD Data

Dukascopy is the canonical market-data provider for this system.

## Layout

```text
data/historical/dukascopy/EURUSD/
├── raw/
│   ├── TICK/
│   └── M1/
├── normalized/
│   ├── M1/
│   ├── M5/
│   ├── M15/
│   ├── H1/
│   └── H4/
├── manifests/
└── validation/
```

## Rules

1. Raw source artifacts are immutable.
2. Never overwrite an acquired raw file.
3. Preserve source metadata and acquisition timestamps.
4. Compute SHA-256 for every raw and normalized artifact.
5. Canonical timestamps are UTC.
6. M1 is the canonical bar layer.
7. M5, M15, H1 and H4 are deterministic derivatives of M1.
8. Do not commit large raw datasets to Git; store them in controlled dataset storage and commit manifests/provenance.
9. A backtest cannot consume a dataset until its validation manifest is PASS.
