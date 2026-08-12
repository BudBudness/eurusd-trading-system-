# Dukascopy EUR/USD Historical Data

This directory is the canonical landing zone for real Dukascopy EUR/USD historical acquisitions.

- `raw/` contains immutable source artifacts.
- `normalized/` contains deterministic repository-schema artifacts.
- `manifests/` contains provenance and SHA-256 manifests.
- `validation/` contains dataset-gate reports.

Do not commit large raw market-data files unless the repository's storage policy explicitly permits them. Store the acquisition artifact externally when required, but commit its manifest, hash, date range, schema version, and validation result.

Synthetic or fabricated market data must never be represented as a real Dukascopy acquisition.
