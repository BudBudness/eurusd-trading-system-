# EUR/USD Dukascopy Dataset Acquisition Runbook

## Purpose

Acquire real Dukascopy EUR/USD historical data without modifying the source artifacts, then normalize and validate it before any backtest is permitted.

## Required order

1. Define an explicit UTC start/end range.
2. Plan deterministic chunks.
3. Download each chunk from Dukascopy.
4. Refuse to overwrite an existing raw artifact.
5. SHA-256 every raw artifact.
6. Parse into the repository canonical schema.
7. Validate UTC ordering, duplicates, OHLC invariants, and expected market gaps.
8. Derive M5/M15/H1/H4 from canonical M1 only.
9. Hash every normalized/derived artifact.
10. Write the immutable dataset manifest.
11. Run the dataset gate.
12. Unlock backtesting only after the gate passes.

## Provenance rule

Raw Dukascopy files are evidence. They must never be rewritten in place. A normalization or parser correction creates a new normalized artifact/version while retaining the original raw acquisition.

## Backtest rule

A dataset without a complete manifest and passing validation report is not a backtestable dataset.
