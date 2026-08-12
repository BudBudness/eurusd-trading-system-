"""Deterministic Dukascopy historical EUR/USD acquisition primitives.

This module intentionally does not silently normalize or mutate downloaded data.
It provides chunk planning, SHA-256 hashing, and immutable acquisition manifests.
Network transport is injected so production downloads and tests remain separate.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
from typing import Callable, Iterable


UTC = timezone.utc


@dataclass(frozen=True)
class AcquisitionChunk:
    start: datetime
    end: datetime

    def __post_init__(self) -> None:
        if self.start.tzinfo is None or self.end.tzinfo is None:
            raise ValueError("chunk timestamps must be timezone-aware")
        if self.start.astimezone(UTC) >= self.end.astimezone(UTC):
            raise ValueError("chunk start must precede chunk end")

    def as_dict(self) -> dict[str, str]:
        return {
            "start": self.start.astimezone(UTC).isoformat().replace("+00:00", "Z"),
            "end": self.end.astimezone(UTC).isoformat().replace("+00:00", "Z"),
        }


def plan_chunks(start: datetime, end: datetime, *, days: int = 7) -> list[AcquisitionChunk]:
    """Create deterministic, contiguous UTC chunks."""
    if start.tzinfo is None or end.tzinfo is None:
        raise ValueError("start/end must be timezone-aware")
    if days <= 0:
        raise ValueError("days must be positive")
    start, end = start.astimezone(UTC), end.astimezone(UTC)
    if start >= end:
        raise ValueError("start must precede end")
    result: list[AcquisitionChunk] = []
    cursor = start
    step = timedelta(days=days)
    while cursor < end:
        nxt = min(cursor + step, end)
        result.append(AcquisitionChunk(cursor, nxt))
        cursor = nxt
    return result


def sha256_file(path: str | Path, *, block_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(block_size), b""):
            digest.update(block)
    return digest.hexdigest()


def write_manifest(path: str | Path, *, instrument: str, source: str,
                   timeframe: str, start: datetime, end: datetime,
                   artifacts: Iterable[dict[str, object]],
                   acquisition_version: str = "1") -> Path:
    """Write a canonical JSON manifest with stable key ordering."""
    payload = {
        "schema_version": "1",
        "dataset": {
            "instrument": instrument,
            "provider": source,
            "timeframe": timeframe,
            "start": start.astimezone(UTC).isoformat().replace("+00:00", "Z"),
            "end": end.astimezone(UTC).isoformat().replace("+00:00", "Z"),
        },
        "acquisition_version": acquisition_version,
        "artifacts": list(artifacts),
    }
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return destination


def acquire_chunks(
    chunks: Iterable[AcquisitionChunk],
    fetch: Callable[[AcquisitionChunk], bytes],
    output_dir: str | Path,
    *,
    prefix: str = "EURUSD_M1",
) -> list[dict[str, object]]:
    """Persist fetched chunks without modification and return manifest records."""
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, object]] = []
    for index, chunk in enumerate(chunks):
        data = fetch(chunk)
        filename = f"{prefix}_{index:05d}.raw"
        destination = root / filename
        if destination.exists():
            raise FileExistsError(f"refusing to overwrite immutable raw artifact: {destination}")
        destination.write_bytes(data)
        records.append({
            "path": str(destination),
            "sha256": sha256_file(destination),
            "bytes": len(data),
            "chunk": chunk.as_dict(),
        })
    return records
