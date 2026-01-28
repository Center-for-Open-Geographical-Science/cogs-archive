# tests/test_publish_unit.py
from pathlib import Path
import builtins
import io
import pytest
from unittest.mock import MagicMock, patch

import cogs_archive.publish as publish_module  # or the module where your publish() function lives


@pytest.fixture
def fake_files(tmp_path):
    p = tmp_path / "dummy.txt"
    p.write_text("hello")
    return [p]


def test_publish_inserts_cogs_community_and_calls_update_metadata(fake_files):
    # minimal metadata from a student
    input_md = {
        "title": "Test dataset",
        "creators": [{"name": "Student, Test"}],
        "license": "CC-BY-4.0",
    }

    # Patch load_config to provide a fake token & registry path
    fake_cfg = MagicMock()
    fake_cfg.zenodo_access_token = "fake-token"
    fake_cfg.zenodo_base_url = "https://sandbox.zenodo.org/api"
    fake_cfg.registry_path = Path("/nonexistent/data-registry.yaml")

    # Patch ZenodoClient so we don't do HTTP
    fake_client = MagicMock()
    # create_deposition should return a deposition with an id
    fake_client.create_deposition.return_value = {"id": 1234}
    # update_metadata returns an updated deposition JSON
    fake_client.update_metadata.return_value = {"id": 1234, "metadata": {}}
    # upload_file returns a file dict
    fake_client.upload_file.return_value = {"filename": "dummy.txt"}
    # publish returns a published record dict with expected keys
    fake_client.publish.return_value = {
        "id": 9999,
        "doi": "10.5281/zenodo.9999",
        "conceptdoi": "10.5281/zenodo.8888",
        "files": [
            {
                "filename": "dummy.txt",
                "checksum": "md5:abcd",
                "filesize": 5,
                "links": {"self": "https://fake"},
            }
        ],
        "created": "2026-01-28T00:00:00Z",
    }

    with patch("cogs_archive.publish.load_config", return_value=fake_cfg):
        with patch(
            "cogs_archive.publish.ZenodoClient", return_value=fake_client
        ) as mock_client_cls:
            # Call publish
            res = publish_module.publish(
                dataset_id="test_ds",
                files=fake_files,
                metadata=input_md,
                version="0.1.0",
                registry_path=None,
            )

    # Check update_metadata was called with communities added
    # The first call to update_metadata should have been with dep_id and metadata
    assert fake_client.update_metadata.called, "update_metadata() was not called"
    call_args = fake_client.update_metadata.call_args[0]  # (dep_id, md)
    assert call_args[0] == 1234
    sent_md = call_args[1]
    assert "communities" in sent_md, "communities not set in metadata"
    assert sent_md["communities"] == [{"identifier": "cogs"}]

    # Confirm publish returned a DOI etc.
    assert res["doi"] == "10.5281/zenodo.9999"
    assert res["conceptdoi"] == "10.5281/zenodo.8888"
