"""Storage boundary for document bytes.

The domain stores only an opaque storage key. Filesystem/object-store access is
kept outside the authorization and document metadata layer.
"""

from __future__ import annotations

from pathlib import Path
import hashlib


class DocumentStorage:
    def __init__(self, root: Path):
        self._root = root.resolve()

    def put(self, storage_key: str, content: bytes) -> str:
        target = (self._root / storage_key).resolve()
        if self._root not in target.parents:
            raise ValueError("storage key escapes storage root")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
        return storage_key

    def read(self, storage_key: str) -> bytes:
        target = (self._root / storage_key).resolve()
        if self._root not in target.parents:
            raise ValueError("storage key escapes storage root")
        return target.read_bytes()

    @staticmethod
    def sha256(content: bytes) -> str:
        return hashlib.sha256(content).hexdigest()
