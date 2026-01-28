from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import hashlib
import requests

from .exceptions import ChecksumError


@dataclass(frozen=True)
class Cache:
    cache_dir: Path

    def path_for(self, dataset_id: str, filename: str, version: str) -> Path:
        safe = dataset_id.replace(":", "_").replace("/", "_")
        p = self.cache_dir / safe / version
        p.mkdir(parents=True, exist_ok=True)
        return p / filename

    def verify_checksum(self, file_path: Path, checksum: str) -> None:
        # checksum expected like "md5:<hex>" (Zenodo commonly uses md5)
        algo, hex_expected = checksum.split(":", 1)
        h = hashlib.new(algo)
        with file_path.open("rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                h.update(chunk)
        if h.hexdigest() != hex_expected:
            raise ChecksumError(
                f"Checksum mismatch for {file_path.name}: expected {checksum}, got {algo}:{h.hexdigest()}"
            )

    def download(self, url: str, dest: Path) -> None:
        with requests.get(url, stream=True, timeout=120) as r:
            r.raise_for_status()
            with dest.open("wb") as f:
                for chunk in r.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        f.write(chunk)
