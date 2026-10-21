"""Source definition and fingerprinting for the raw Telco snapshot."""

import hashlib
from pathlib import Path

SOURCE_REPOSITORY = "https://github.com/IBM/telco-customer-churn-on-icp4d"
SOURCE_COMMIT = "1fd6fd70906479be1712e64cfc0ea89f58466629"
SOURCE_URL = (
    "https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d/"
    f"{SOURCE_COMMIT}/data/Telco-Customer-Churn.csv"
)
EXPECTED_SHA256 = (
    "16320c9c1ec72448db59aa0a26a0b95401046bef5d02fd3aeb906448e3055e91"
)

RAW_DATA_PATH = Path("data/raw/telco.csv")
SOURCE_METADATA_PATH = Path("data/raw/telco.source.json")


def sha256_file(path: Path) -> str:
    """Return the SHA-256 hex digest of the file's bytes."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 16), b""):
            digest.update(chunk)
    return digest.hexdigest()
