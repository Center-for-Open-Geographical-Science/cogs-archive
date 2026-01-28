from pathlib import Path
from .config import load_config
from .zenodo import ZenodoClient
from .registry import DatasetRegistry


def publish(
    dataset_id: str,
    files: list[Path],
    metadata: dict,
    version: str,
    registry_path: Path | None = None,
) -> dict:
    """
    Publish a dataset release to Zenodo and update the lab registry.

    `metadata` should be Zenodo deposition metadata under the "metadata" key shape,
    e.g. title, upload_type="dataset", creators, description, license, keywords, etc.
    """
    cfg = load_config()
    if not cfg.zenodo_access_token:
        raise RuntimeError("ZENODO_ACCESS_TOKEN is not set")

    client = ZenodoClient(
        access_token=cfg.zenodo_access_token, base_url=cfg.zenodo_base_url
    )
    reg = DatasetRegistry(path=registry_path or cfg.registry_path)

    dep = client.create_deposition()
    dep_id = dep["id"]

    # Ensure required Zenodo fields are present:
    md = dict(metadata)
    md.setdefault("upload_type", "dataset")

    md.setdefault("communities", [{"identifier": "cogs"}])

    # (optional but recommended) enforce it strictly
    if md["communities"] != [{"identifier": "cogs"}]:
        raise ValueError(
            "All datasets must be published to the Zenodo community 'COGS'."
        )

    client.update_metadata(dep_id, md)

    uploaded = []
    for fp in files:
        uploaded.append(client.upload_file(dep_id, fp))

    published = client.publish(dep_id)

    # Pull identifiers from publish response
    conceptrecid = published.get("conceptrecid")
    conceptdoi = published.get("conceptdoi")
    recid = published.get("record_id") or published.get("id")
    doi = published.get("doi")

    # File info: Zenodo returns checksums for files; normalize into registry format
    files_entry = []
    for f in published.get("files", []):
        files_entry.append(
            {
                "name": f.get("filename"),
                "checksum": f.get("checksum"),
                "size": f.get("filesize"),
                "download_url": f.get("links", {}).get("self"),
            }
        )

    # update registry
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
        # also store/refresh descriptive fields locally (optional)
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
