"""Storage boundary for document bytes."""

from __future__ import annotations

import hashlib
from pathlib import Path


class DocumentStorage:
    def __init__(self, root: Path):
        self._root = root.resolve()

    def _target(self, storage_key: str) -> Path:
        target = (self._root / storage_key).resolve()
        if self._root == target or self._root not in target.parents:
            raise ValueError("storage key escapes storage root")
        return target

    def put(self, storage_key: str, content: bytes) -> str:
        target = self._target(storage_key)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
        return storage_key

    def delete(self, storage_key: str) -> None:
        target = self._target(storage_key)
        if target.exists():
            target.unlink()

    def read(self, storage_key: str) -> bytes:
        return self._target(storage_key).read_bytes()

    @staticmethod
    def sha256(content: bytes) -> str:
        return hashlib.sha256(content).hexdigest()
