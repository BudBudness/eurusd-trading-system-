# EUR/USD Trading System

A standalone, folder-over-agents trading and execution research system for **EUR/USD only**, designed around Pepperstone + cTrader.

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
EXECUTION / DATA
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
- **Real trading is disabled until the runtime is validated.**
- **No credentials or secrets belong in Git.**
- **EUR/USD is the only supported trading instrument in v1.**

## Current scope

1. Market-state ingestion and normalization.
2. 4H → 1H → 15M → 5M analysis pipeline.
3. Strategy signal proposals.
4. Pre-trade risk validation.
5. Paper/demo execution first.
6. Execution telemetry: spread, slippage, latency, fills and rejects.
7. Post-trade analytics and expectancy.

## Safety boundary

This repository is initially a research, simulation and demo-execution system. A passing CI build does **not** authorize a live order. Live execution requires an explicit, separately controlled production gate.

## Work-unit example

`work_units/WU-EURUSD-001/` is the reference work unit. It demonstrates the complete lifecycle without requiring live broker credentials.

## Development

Python is the initial runtime language. Run tests with:

```bash
python -m pytest
```

See `docs/architecture/` for the design and `docs/operations/` for runtime rules.
