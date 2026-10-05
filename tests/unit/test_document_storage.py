from pathlib import Path

import pytest

from cairnsearch.documents.storage import DocumentStorage


def test_storage_rejects_path_escape(tmp_path: Path):
    storage = DocumentStorage(tmp_path)
    with pytest.raises(ValueError):
        storage.put("../outside.txt", b"secret")


def test_storage_roundtrip_and_hash(tmp_path: Path):
    storage = DocumentStorage(tmp_path)
    key = storage.put("org/doc/v1.bin", b"hello")
    assert storage.read(key) == b"hello"
    assert storage.sha256(b"hello") == "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
