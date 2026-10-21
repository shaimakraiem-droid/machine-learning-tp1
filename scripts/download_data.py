"""Fetch the commit-pinned Telco CSV if absent, then record its source and hash."""

import json
import urllib.request

from churnlab.data import (
    EXPECTED_SHA256,
    RAW_DATA_PATH,
    SOURCE_COMMIT,
    SOURCE_METADATA_PATH,
    SOURCE_REPOSITORY,
    SOURCE_URL,
    sha256_file,
)

if RAW_DATA_PATH.exists():
    print(f"Using existing snapshot: {RAW_DATA_PATH.as_posix()}")
else:
    RAW_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {SOURCE_URL}")
    urllib.request.urlretrieve(SOURCE_URL, RAW_DATA_PATH)

actual_sha256 = sha256_file(RAW_DATA_PATH)
if actual_sha256 != EXPECTED_SHA256:
    raise ValueError(
        f"Source hash mismatch for {RAW_DATA_PATH.as_posix()}: "
        f"expected {EXPECTED_SHA256}, got {actual_sha256}"
    )

metadata = {
    "dataset": "IBM Telco Customer Churn",
    "source_repository": SOURCE_REPOSITORY,
    "source_commit": SOURCE_COMMIT,
    "source_url": SOURCE_URL,
    "local_path": RAW_DATA_PATH.as_posix(),
    "sha256": actual_sha256,
    "size_bytes": RAW_DATA_PATH.stat().st_size,
}
SOURCE_METADATA_PATH.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
print(json.dumps(metadata, indent=2))
