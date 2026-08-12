from datetime import datetime, timezone

from runtime.dataset_manifest import Artifact, DatasetManifest, manifest_sha256, utc_iso


def test_manifest_is_deterministic():
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    end = datetime(2026, 1, 2, tzinfo=timezone.utc)
    manifest = DatasetManifest(
        dataset_id="EURUSD-DUKASCOPY-TEST",
        instrument="EURUSD",
        provider="Dukascopy",
        timezone="UTC",
        base_timeframe="M1",
        start=utc_iso(start),
        end=utc_iso(end),
        artifacts=(Artifact("raw/a", "abc", 3),),
    )
    assert utc_iso(start) == "2026-01-01T00:00:00Z"
    assert manifest_sha256(manifest) == manifest_sha256(manifest)
    assert len(manifest_sha256(manifest)) == 64
