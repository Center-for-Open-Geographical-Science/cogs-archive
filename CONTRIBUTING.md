# Contributing

- Roles
  - **Student/Author** — prepares dataset draft and PR.
  - **Curator** — lab admin(s), approve metadata, publish to Zenodo.
  - **Reviewer** — optional peer reviewer for dataset quality.

- Minimal metadata required (`metadata.yaml`):
  - `dataset_id` — short, kebab_case
  - `title`
  - `description`
  - `creators` (list of `name`, `affiliation`, optional `orcid`)
  - `license` (required; default: `CC-BY-4.0`)
  - `version` (MAJOR.MINOR.PATCH)
  - `keywords` (list)
  - `related_identifiers` (e.g., paper DOI)
  - `sensitive_data` (boolean + description if true)

- PR workflow:
  1. Author branches and adds `datasets/<id>/` with `metadata.yaml` and files (or pointers if files are large).
  2. CI runs `cogs-archive validate`.
  3. Curator reviews PR content and metadata.
  4. If approved:
     - Option A (preferred): Curator merges PR and runs publish (curator-controlled).
     - Option B: Auto-merge with policy; publish occurs via `scripts/publish.sh` which requires curator token.

- Publication policy:
  - Mandatory: dataset must have an explicit license and not contain unanonymized sensitive data.
  - For sensitive datasets, archive only metadata and provide a `data_access` statement (contacts, IRB constraints).

# Versioning & governance model (concise, actionable)

### Package vs dataset versions
- **Repository / package (`cogs-archive`)**: Semantic versioning, standard `MAJOR.MINOR.PATCH`. Release tags on GitHub.
- **Datasets**: Semantic-like `MAJOR.MINOR.PATCH` but interpreted as:
  - MAJOR: incompatible/structural changes to dataset (e.g., different sampling frame)
  - MINOR: additional data or corrected values that do not change main conclusions
  - PATCH: metadata fix, small corrections, or reformatting
- Zenodo concept DOI is for the dataset concept. Each published dataset version gets its own DOI.

### Publication governance
- **Who can publish:** Only curators (or a curator-run GitHub Action) publish to Zenodo. Students open PRs; curators review and publish.
- **Approval criteria:** `validate` must pass, metadata complete, license set, sensitive_data flag resolved.
- **Registry updates:** `data-registry.yaml` is authoritative — append-only for versions. Curator must ratify changes to the registry (PR review).

### Archival policy highlights
- All published versions are immutable.
- When a dataset is removed, the registry retains provenance and the Zenodo DOI remains resolvable (Zenodo keeps records).
- Sensitive data are not archived publicly; provide metadata + access instructions.
