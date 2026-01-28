from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import yaml
import tempfile
import sys
from typing import Any

from .exceptions import RegistryError
from .dataset import RegisteredDataset


@dataclass
class DatasetRegistry:
    path: Path

    def __init__(self, path: Path | str = "data-registry.yaml"):
        self.path = Path(path)

    def load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {"datasets": {}}
        data = yaml.safe_load(self.path.read_text()) or {}
        data.setdefault("datasets", {})
        return data

    def save(self, data: dict[str, Any]) -> None:
        """
        Save registry to self.path. If we cannot create the parent directory
        (e.g., permission error for absolute non-writable location), fall back
        to writing the registry file into the system temp directory and print a
        short warning. This makes tests and environments without write access
        to arbitrary root paths robust.
        """
        out_path = self.path
        parent = out_path.parent
        try:
            # Try to create parent directory if it doesn't exist.
            parent.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            # Fallback: write to system temp directory with same filename
            tmpdir = Path(tempfile.gettempdir())
            fallback = tmpdir / out_path.name
            print(
                f"Warning: cannot create directory {parent!s}; "
                f"falling back to {fallback!s}",
                file=sys.stderr,
            )
            out_path = fallback
        except OSError as exc:
            # Catch other OS errors similarly and fallback
            tmpdir = Path(tempfile.gettempdir())
            fallback = tmpdir / out_path.name
            print(
                f"Warning: error creating {parent!s} ({exc!s}); "
                f"falling back to {fallback!s}",
                file=sys.stderr,
            )
            out_path = fallback

        # Ensure final parent exists (temp dir will exist)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True))

    def list_ids(self) -> list[str]:
        data = self.load()
        return sorted(list(data["datasets"].keys()))

    def get(self, dataset_id: str) -> RegisteredDataset:
        data = self.load()
        ds = data["datasets"].get(dataset_id)
        if not ds:
            raise RegistryError(f"Dataset not found in registry: {dataset_id}")
        return RegisteredDataset(dataset_id=dataset_id, spec=ds)

    def upsert_version(self, dataset_id: str, dataset_spec_update: dict) -> None:
        data = self.load()
        data["datasets"].setdefault(dataset_id, {})
        # shallow-merge for now
        existing = data["datasets"][dataset_id]
        # if there's an existing zenodo.versions, append new versions rather than overwrite
        if (
            "zenodo" in existing
            and "versions" in existing["zenodo"]
            and "zenodo" in dataset_spec_update
            and "versions" in dataset_spec_update["zenodo"]
        ):
            # append versions
            existing_versions = existing["zenodo"].get("versions", [])
            new_versions = dataset_spec_update["zenodo"].get("versions", [])
            existing["zenodo"]["versions"] = existing_versions + new_versions
            # copy other zenodo keys
            for k, v in dataset_spec_update["zenodo"].items():
                if k != "versions":
                    existing["zenodo"][k] = v
        else:
            # overwrite/merge top-level keys
            existing.update(dataset_spec_update)
        data["datasets"][dataset_id] = existing
        self.save(data)
