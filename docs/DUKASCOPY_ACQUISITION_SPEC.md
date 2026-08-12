# Dukascopy EUR/USD Acquisition Specification

## Canonical source

Dukascopy historical prices API.

## Canonical base timeframe

M1 bid candles. Tick data remains a separate retained provenance layer when acquired.

## API constraints

The documented historical-price endpoint supports `1min` and `tick` timeframes and caps a single historical-price response at 5000 records. Acquisition therefore uses chunks small enough to remain below the M1 response ceiling.

## Integrity

Every response is preserved byte-for-byte, hashed with SHA-256, and recorded in an acquisition manifest. Existing raw artifacts are never overwritten.

## No fabricated data

A manifest may only be marked as an acquisition after the actual source response has been retrieved. Tests use synthetic fixtures solely to test acquisition mechanics; fixtures are never represented as market data.

## Reference

Dukascopy API documentation: https://www.dukascopy.com/trading-tools/api/documentation/quotes
