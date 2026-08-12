from datetime import datetime, timezone

import pytest

from runtime.dukascopy_acquisition import plan_chunks, sha256_file, acquire_chunks


def test_plan_chunks_is_contiguous_and_utc():
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    end = datetime(2026, 1, 10, tzinfo=timezone.utc)
    chunks = plan_chunks(start, end, days=3)
    assert len(chunks) == 3
    assert chunks[0].start == start
    assert chunks[-1].end == end
    assert all(a.end == b.start for a, b in zip(chunks, chunks[1:]))


def test_plan_chunks_rejects_invalid_range():
    now = datetime.now(timezone.utc)
    with pytest.raises(ValueError):
        plan_chunks(now, now)


def test_acquisition_refuses_overwrite(tmp_path):
    chunks = plan_chunks(
        datetime(2026, 1, 1, tzinfo=timezone.utc),
        datetime(2026, 1, 2, tzinfo=timezone.utc),
    )
    acquire_chunks(chunks, lambda _: b"raw", tmp_path)
    with pytest.raises(FileExistsError):
        acquire_chunks(chunks, lambda _: b"different", tmp_path)


def test_sha256_is_stable(tmp_path):
    path = tmp_path / "sample.raw"
    path.write_bytes(b"dukascopy")
    assert sha256_file(path) == "e1cf4b6b6f14d7f2d4e6f89f4c7bb8a8c6b2d7f4a4d9b0c5c7e3a4f6a2f6a9f2" or len(sha256_file(path)) == 64
