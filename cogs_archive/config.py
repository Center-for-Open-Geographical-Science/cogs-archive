from dataclasses import dataclass
import os
from pathlib import Path


@dataclass(frozen=True)
class Config:
    zenodo_access_token: str
    zenodo_base_url: str = "https://zenodo.org/api"
    registry_path: Path = Path("data-registry.yaml")
    cache_dir: Path = Path.home() / ".cache" / "labarchive"


def load_config() -> Config:
    token = os.getenv("ZENODO_ACCESS_TOKEN", "").strip()
    base = os.getenv("ZENODO_BASE_URL", "https://zenodo.org/api").strip()
    reg = Path(os.getenv("LABARCHIVE_REGISTRY_PATH", "data-registry.yaml"))
    cache = Path(
        os.getenv("LABARCHIVE_CACHE_DIR", str(Path.home() / ".cache" / "labarchive"))
    )
    return Config(
        zenodo_access_token=token,
        zenodo_base_url=base,
        registry_path=reg,
        cache_dir=cache,
    )
