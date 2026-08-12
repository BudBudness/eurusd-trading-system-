"""Canonical immutable dataset manifest helpers."""
from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path


@dataclass(frozen=True)
class Artifact:
    path: str
    sha256: str
    bytes: int


@dataclass(frozen=True)
class DatasetManifest:
    dataset_id: str
    instrument: str
    provider: str
    timezone: str
    base_timeframe: str
    start: str
    end: str
    artifacts: tuple[Artifact, ...]
    schema_version: str = "1"

    def to_dict(self) -> dict:
        value = asdict(self)
        value["artifacts"] = [asdict(item) for item in self.artifacts]
        return value


def utc_iso(value: datetime) -> str:
    if value.tzinfo is None:
        raise ValueError("datetime must be timezone-aware")
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def manifest_sha256(manifest: DatasetManifest) -> str:
    encoded = json.dumps(manifest.to_dict(), sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def write_manifest(path: str | Path, manifest: DatasetManifest) -> Path:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(manifest.to_dict(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return destination
