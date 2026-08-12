# EUR/USD Trading System

A standalone, folder-over-agents trading and execution research system for **EUR/USD only**, with **Dukascopy as the canonical market-data provider**.

## Architecture

```text
CONTROL
  policies / schemas / workflows / state machines
       ↓
WORK UNITS
       ↓
TASKS
       ↓
SKILLS
       ↓
AGENTS
       ↓
CONNECTORS
       ↓
DUKASCOPY DATA
       ↓
NORMALIZATION / VALIDATION
       ↓
IMMUTABLE DATASET
       ↓
EXECUTION / BACKTEST
       ↓
STATE + EVENTS + EVIDENCE
       ↓
AUDIT + OBSERVABILITY
```

### Principles

- **Folders hold persistent state and evidence.**
- **Work units are bounded operational objectives.**
- **Tasks are discrete pieces of work.**
- **Skills are reusable capabilities.**
- **Agents are replaceable workers, not system owners.**
- **Policies constrain agents and workflows.**
- **Schemas define contracts.**
- **Dukascopy is the canonical EUR/USD market-data source.**
- **Raw market data is immutable and hashed.**
- **M1 is the canonical bar layer.**
- **M5/M15/H1/H4 are deterministic derivatives of M1.**
- **Real trading is disabled until the runtime is validated and explicitly authorized.**
- **No credentials or secrets belong in Git.**
- **EUR/USD is the only supported trading instrument in v1.**

## Current scope

1. Dukascopy tick and M1 historical-data acquisition.
2. UTC normalization and source provenance.
3. M1 → M5 → M15 → H1 → H4 deterministic resampling.
4. Historical-data integrity validation and SHA-256 manifests.
5. 4H → 1H → 15M → 5M analysis pipeline.
6. Strategy signal proposals.
7. Pre-trade risk validation.
8. Paper/demo execution first.
9. Execution telemetry: spread, slippage, latency, fills and rejects.
10. Post-trade analytics and expectancy.

## Data architecture

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

See `docs/DUKASCOPY_MIGRATION_REPORT.md` for the migration and reproducibility contract.

## Safety boundary

This repository is initially a research, simulation and demo-execution system. A passing CI build does **not** authorize a live order. Live execution requires an explicit, separately controlled production gate.

## Development

Python is the initial runtime language. Run tests with:

```bash
python -m pytest
```
