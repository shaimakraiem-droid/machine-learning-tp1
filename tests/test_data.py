import hashlib

import churnlab
from churnlab.data import RAW_DATA_PATH, SOURCE_COMMIT, SOURCE_URL, sha256_file


def test_package_version():
    assert churnlab.__version__ == "0.1.0"


def test_sha256_file_matches_hashlib(tmp_path):
    sample = tmp_path / "sample.csv"
    sample.write_bytes(b"customerID,Churn\n0001-AAAAA,No\n")
    assert sha256_file(sample) == hashlib.sha256(sample.read_bytes()).hexdigest()


def test_source_url_is_pinned_to_a_commit():
    assert SOURCE_COMMIT in SOURCE_URL
    assert RAW_DATA_PATH.as_posix() == "data/raw/telco.csv"
