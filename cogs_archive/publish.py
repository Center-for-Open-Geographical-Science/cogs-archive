from pathlib import Path
from typing import List

from .config import load_config
from .zenodo import ZenodoClient
from .registry import DatasetRegistry
from .exceptions import ZenodoError


def publish(
    dataset_id: str,
    files: List[Path],
    metadata: dict,
    version: str,
    registry_path: Path | None = None,
) -> dict:
    """
    Publish a dataset release to Zenodo and update the lab registry.

    `metadata` should be Zenodo deposition metadata shaped like Zenodo's "metadata" dict:
    e.g. title, upload_type="dataset", creators, description, license, keywords, etc.
    """
    cfg = load_config()
    if not cfg.zenodo_access_token:
        raise RuntimeError("ZENODO_ACCESS_TOKEN (or ZENODO_SANDBOX_TOKEN) is not set")

    client = ZenodoClient(
        access_token=cfg.zenodo_access_token, base_url=cfg.zenodo_base_url
    )
    reg = DatasetRegistry(path=registry_path or cfg.registry_path)

    # create a new deposition (draft)
    dep = client.create_deposition()
    dep_id = dep["id"]

    # ensure required Zenodo fields are present and enforce COGS community
    md = dict(metadata)
    md.setdefault("upload_type", "dataset")
    md.setdefault("communities", [{"identifier": "cogs"}])

    # Strict enforcement (uncomment to enforce)
    if md.get("communities") != [{"identifier": "cogs"}]:
        raise ValueError(
            "All datasets must be published to the Zenodo community 'COGS'."
        )

    # push metadata to deposition
    client.update_metadata(dep_id, md)

    # upload files
    uploaded = []
    for fp in files:
        uploaded.append(client.upload_file(dep_id, fp))

    # publish deposition
    published = client.publish(dep_id)

    # Pull identifiers from publish response (Zenodo may use "id" or "record_id")
    conceptrecid = published.get("conceptrecid")
    conceptdoi = published.get("conceptdoi")
    recid = published.get("record_id") or published.get("id")
    doi = published.get("doi")

    # File info: use local filenames as the source of truth.
    # Zenodo's publish response may not reliably include "filename" immediately.
    files_entry = []
    local_names = [fp.name for fp in files]
    for local_name, f in zip(local_names, published.get("files", [])):
        links = f.get("links", {}) or {}
        files_entry.append(
            {
                "name": local_name,
                "checksum": f.get("checksum"),
                "size": f.get("filesize") or f.get("size"),
                "download_url": links.get("download") or links.get("self"),
            }
        )

    # update registry entry (append version)
    update = {
        "zenodo": {
            "conceptrecid": conceptrecid,
            "conceptdoi": conceptdoi,
            "versions": [
                {
                    "version": version,
                    "recid": recid,
                    "doi": doi,
                    "published": published.get("created"),
                    "files": files_entry,
                }
            ],
        },
        # store descriptive fields locally
        "title": md.get("title"),
        "description": md.get("description"),
        "creators": md.get("creators"),
        "keywords": md.get("keywords"),
        "license": md.get("license"),
    }

    reg.upsert_version(dataset_id, update)

    return {
        "dataset_id": dataset_id,
        "doi": doi,
        "conceptdoi": conceptdoi,
        "recid": recid,
    }
