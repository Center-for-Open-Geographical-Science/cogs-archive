from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path

from .cache import Cache
from .config import load_config
from .exceptions import RegistryError


@dataclass(frozen=True)
class RegisteredDataset:
    dataset_id: str
    spec: dict

    def latest(self) -> dict:
        z = self.spec.get("zenodo", {})
        versions = z.get("versions", [])
        if not versions:
            raise RegistryError(f"No versions registered for {self.dataset_id}")
        # assume versions are appended in chronological order; could sort by published date
        return versions[-1]

    @property
    def doi(self) -> str:
        return self.latest().get("doi", "")

    @property
    def conceptdoi(self) -> str:
        return self.spec.get("zenodo", {}).get("conceptdoi", "")

    def citation(self, style: str = "text") -> str:
        # minimal; you can extend to CSL JSON / bibtex
        title = self.spec.get("title", self.dataset_id)
        creators = self.spec.get("creators", [])
        author = creators[0]["name"] if creators else "Unknown"
        version = self.latest().get("version", "")
        doi = self.doi
        if style == "text":
            return f"{author} et al. ({version}). {title}. Zenodo. DOI:{doi}"
        if style == "bibtex":
            key = self.dataset_id.replace("-", "_")
            return (
                f"@dataset{{{key},\n"
                f"  title = {{{title}}},\n"
                f"  author = {{{' and '.join([c['name'] for c in creators])}}},\n"
                f"  year = {{{self.latest().get('published','')[:4]}}},\n"
                f"  version = {{{version}}},\n"
                f"  doi = {{{doi}}}\n"
                f"}}"
            )
        raise ValueError(f"Unknown style: {style}")

    def fetch(
        self, version: str | None = None, cache: Cache | None = None
    ) -> list[Path]:
        cfg = load_config()
        cache = cache or Cache(cfg.cache_dir)

        z = self.spec.get("zenodo", {})
        versions = z.get("versions", [])
        if not versions:
            raise RegistryError(f"No versions registered for {self.dataset_id}")

        v = None
        if version is None:
            v = versions[-1]
        else:
            for cand in versions:
                if cand.get("version") == version:
                    v = cand
                    break
        if v is None:
            raise RegistryError(f"Version {version} not found for {self.dataset_id}")

        out = []
        for f in v.get("files", []):
            name = f["name"]
            checksum = f.get("checksum")
            url = f.get("download_url") or f.get("links", {}).get("self")
            if not url:
                # registry can store download URL; otherwise you can resolve via records API
                raise RegistryError(
                    f"Missing download URL for file {name} in {self.dataset_id}"
                )

            dest = cache.path_for(self.dataset_id, name, v.get("version", "unknown"))
            if not dest.exists():
                cache.download(url, dest)
            if checksum:
                cache.verify_checksum(dest, checksum)
            out.append(dest)

        return out
