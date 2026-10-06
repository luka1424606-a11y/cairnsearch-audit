"""Content-addressed storage boundary for immutable legal source snapshots."""

from __future__ import annotations

import hashlib
from pathlib import Path


class FileSnapshotStore:
    def __init__(self, root: str):
        self._root = Path(root).resolve()

    def _path(self, storage_key: str) -> Path:
        candidate = (self._root / storage_key).resolve()
        if candidate != self._root and self._root not in candidate.parents:
            raise ValueError("invalid snapshot storage key")
        return candidate

    def put_if_absent(self, storage_key: str, content: bytes) -> bool:
        path = self._path(storage_key)
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            return False
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_bytes(content)
        tmp.replace(path)
        return True

    def delete_if_exists(self, storage_key: str) -> None:
        path = self._path(storage_key)
        if path.exists():
            path.unlink()

    def sha256(self, storage_key: str) -> str:
        return hashlib.sha256(self._path(storage_key).read_bytes()).hexdigest()
