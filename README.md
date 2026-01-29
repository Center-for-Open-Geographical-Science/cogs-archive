# COGS Data Archive (`cogs-archive`)

`cogs-archive` is the official tooling and registry for publishing, managing, and accessing research datasets produced by the **Center for Open Geographical Science (COGS)**.

Datasets are archived on **Zenodo**, assigned **DOIs**, and curated through the **[COGS Zenodo community](https://zenodo.org/communities/cogs/records?q=&l=list&p=1&s=10&sort=newest)** to support **reproducibility, citation, and long-term access**.

---

## What this repository is for

This repository provides:

- A standard workflow for depositing datasets to Zenodo
- A curated publication process with faculty approval
- A registry that maps internal dataset IDs to Zenodo DOIs
- Lightweight Python tooling for programmatic data access

This repository is **not** a data store.  
All actual datasets live on Zenodo.

---

## High-level workflow

1. Students prepare a dataset directory (data + README)
2. The directory is zipped
3. A single command submits the dataset
4. Curators review and approve the submission on Zenodo
5. A DOI is minted and shared

Once published, datasets are:
- Publicly downloadable via Zenodo
- Citable via DOI
- Reproducible via the local registry

---

## Governance model (important)

The **COGS Zenodo community is curated**.

- **Students**
  - Prepare datasets
  - Submit datasets to COGS
  - Do not make datasets public on their own

- **Curators (faculty / designated admins)**
  - Receive automatic notifications of submissions
  - Review metadata, files, and licenses
  - Approve or reject submissions

Nothing becomes public without curator approval.

---

## Repository structure

```
cogs-archive/
├── cogs_archive/          # Python package
├── scripts/               # Student- and curator-facing scripts
├── datasets/              # Dataset directories and ZIPs (not committed)
├── tests/                 # Unit tests
├── data-registry.yaml     # Canonical dataset registry (auto-updated)
├── README.md
├── depositing.md          # Student guide for depositing data
└── pyproject.toml
```

---

## Student workflow (summary)

Students do **not** need to understand Zenodo or Python internals.

1. Prepare a dataset directory containing:
   - Data files (e.g., CSVs)
   - `README.md`
2. Zip the directory
3. Run one command:
   ```bash
   python scripts/publish_qcew.py      --dataset-id <dataset_id>      --version <version>      --zip <path_to_zip>
   ```
4. Wait for curator approval
5. Receive a DOI

Full instructions are in **`depositing.md`**.

---

## Curator workflow (summary)

Curators:

- Hold Zenodo curator privileges for the COGS community
- Receive email notifications when datasets are submitted
- Review submissions via the Zenodo web interface
- Approve or reject submissions
- Optionally publish datasets directly using curator tokens

---

## Installation (development)

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .[test]
```

Run tests:

```bash
pytest
```

---

## Zenodo authentication

Publishing requires a Zenodo **personal access token**.

- Tokens are created in Zenodo → Profile → Applications
- Required scopes:
  - `deposit:read`
  - `deposit:write`
  - `deposit:actions`

Tokens are set via environment variables:

```bash
export ZENODO_ACCESS_TOKEN="your-token"
# sandbox (for testing only)
export ZENODO_BASE_URL="https://sandbox.zenodo.org/api"
```

**Never commit tokens to git.**

---

## Dataset registry

The file `data-registry.yaml` is automatically updated when datasets are published.

It records:
- Dataset IDs
- Zenodo concept DOIs
- Version DOIs
- File checksums

This file is the **authoritative reproducibility index** for the lab and should be committed to the repository.

---

## Accessing published datasets (programmatic)

```python
from cogs_archive.registry import DatasetRegistry

reg = DatasetRegistry("data-registry.yaml")
ds = reg.get("<dataset_id>")

paths = ds.fetch()
```

This:
- Downloads the correct version from Zenodo
- Verifies checksums
- Caches files locally

---

## Versioning policy

Datasets use semantic-style versioning:

- `1.0.0` — first public release
- `1.1.0` — additional data or small corrections
- `2.0.0` — major changes or restructuring

Once published, dataset versions are **immutable**.

---

## What should NOT be committed

- Dataset ZIP files
- Raw or derived research data
- Zenodo tokens or credentials
- `__pycache__`, `.egg-info`, editor backup files

---

## Status

This project is actively used by COGS to support reproducible research and data publication.  
The API may evolve, but dataset DOIs and registry semantics are stable.

---

## License

The software in this repository is licensed under the terms specified in `LICENSE`.

Datasets published using this tooling are licensed individually (e.g. CC-BY, CC-BY-SA), as specified in their Zenodo metadata.
