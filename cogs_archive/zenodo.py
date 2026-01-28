from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import requests

from .exceptions import ZenodoError


@dataclass(frozen=True)
class ZenodoClient:
    access_token: str
    base_url: str = "https://zenodo.org/api"
    timeout_s: int = 60

    def _headers(self) -> dict:
        return {"Accept": "application/json"}

    def _params(self) -> dict:
        return {"access_token": self.access_token}

    def create_deposition(self) -> dict:
        url = f"{self.base_url}/deposit/depositions"
        r = requests.post(
            url,
            params=self._params(),
            json={},
            headers=self._headers(),
            timeout=self.timeout_s,
        )
        if not r.ok:
            raise ZenodoError(f"Create deposition failed: {r.status_code} {r.text}")
        return r.json()

    def update_metadata(self, deposition_id: int, metadata: dict) -> dict:
        url = f"{self.base_url}/deposit/depositions/{deposition_id}"
        payload = {"metadata": metadata}
        r = requests.put(
            url,
            params=self._params(),
            json=payload,
            headers=self._headers(),
            timeout=self.timeout_s,
        )
        if not r.ok:
            raise ZenodoError(f"Update metadata failed: {r.status_code} {r.text}")
        return r.json()

    def upload_file(self, deposition_id: int, file_path: Path) -> dict:
        # Zenodo deposit API supports multipart upload to the deposition "bucket"
        dep = self.get_deposition(deposition_id)
        bucket_url = dep["links"]["bucket"]

        with file_path.open("rb") as f:
            url = f"{bucket_url}/{file_path.name}"
            r = requests.put(
                url,
                params=self._params(),
                data=f,
                headers=self._headers(),
                timeout=self.timeout_s,
            )
        if not r.ok:
            raise ZenodoError(f"Upload failed: {r.status_code} {r.text}")
        return r.json()

    def publish(self, deposition_id: int) -> dict:
        url = f"{self.base_url}/deposit/depositions/{deposition_id}/actions/publish"
        r = requests.post(
            url, params=self._params(), headers=self._headers(), timeout=self.timeout_s
        )
        if not r.ok:
            raise ZenodoError(f"Publish failed: {r.status_code} {r.text}")
        return r.json()

    def get_deposition(self, deposition_id: int) -> dict:
        url = f"{self.base_url}/deposit/depositions/{deposition_id}"
        r = requests.get(
            url, params=self._params(), headers=self._headers(), timeout=self.timeout_s
        )
        if not r.ok:
            raise ZenodoError(f"Get deposition failed: {r.status_code} {r.text}")
        return r.json()

    def get_record(self, recid: int) -> dict:
        # published record endpoint
        url = f"{self.base_url}/records/{recid}"
        r = requests.get(url, headers=self._headers(), timeout=self.timeout_s)
        if not r.ok:
            raise ZenodoError(f"Get record failed: {r.status_code} {r.text}")
        return r.json()
