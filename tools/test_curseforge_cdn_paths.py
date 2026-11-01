"""Official CDN numeric spelling can change; identity and bytes must not."""
import hashlib
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import restore_modified
import verify_modified


class CurseForgeNumericPathTests(unittest.TestCase):
    def row(self, data=b"exact pinned download"):
        return {"path": "mods/example.jar", "fileName": "example.jar", "projectId": 1091339,
                "fileId": 7065024, "sourceUrl": "https://edge.forgecdn.net/files/7065/024/example.jar",
                "sizeBytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}

    def test_official_padded_and_canonical_unpadded_paths_keep_the_same_exact_file_id(self):
        row = self.row()
        for host in ["edge.forgecdn.net", "mediafilez.forgecdn.net", "media.forgecdn.net"]:
            for suffix in ["024", "24"]:
                url = f"https://{host}/files/7065/{suffix}/example.jar"
                with self.subTest(url=url): self.assertEqual(verify_modified.source_url(row, url=url), url)

    def test_wrong_or_noncanonical_numeric_ids_are_rejected(self):
        for prefix in ["7065/025", "7064/024", "7065/0024", "07065/024", "7065/24x", "7065/24.0"]:
            with self.subTest(prefix=prefix), self.assertRaises(ValueError):
                verify_modified.source_url(self.row(), url=f"https://mediafilez.forgecdn.net/files/{prefix}/example.jar")

    def test_official_host_https_exact_filename_and_no_url_decorations_stay_required(self):
        urls = ["http://mediafilez.forgecdn.net/files/7065/24/example.jar",
                "https://mediafilez.forgecdn.net.evil.invalid/files/7065/24/example.jar",
                "https://mediafilez.forgecdn.net/files/7065/24/other.jar",
                "https://mediafilez.forgecdn.net/files/7065/24/example.jar?mirror=1",
                "https://mediafilez.forgecdn.net/files/7065/24/example.jar#fragment",
                "https://user:pass@mediafilez.forgecdn.net/files/7065/24/example.jar"]
        for url in urls:
            with self.subTest(url=url), self.assertRaises(ValueError): verify_modified.source_url(self.row(), url=url)

    def test_cold_download_accepts_official_redirect_and_checks_exact_bytes(self):
        data = b"exact pinned download"
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "locked"
            with patch.object(restore_modified, "urlopen", return_value=Response(data)):
                self.assertTrue(restore_modified.download(self.row(data), target))
            self.assertEqual(target.read_bytes(), data)
            with patch.object(restore_modified, "urlopen") as network:
                self.assertFalse(restore_modified.download(self.row(data), target))
            network.assert_not_called()

    def test_wrong_id_redirect_cannot_replace_an_existing_cache_entry(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "locked"; target.write_bytes(b"preserve existing bytes")
            with patch.object(restore_modified, "urlopen", return_value=Response(b"exact pinned download", "https://mediafilez.forgecdn.net/files/7065/25/example.jar")):
                with self.assertRaises(ValueError): restore_modified.download(self.row(), target)
            self.assertEqual(target.read_bytes(), b"preserve existing bytes")
            self.assertEqual([p.name for p in Path(folder).iterdir()], ["locked"])

    def test_normalized_redirect_does_not_relax_size_or_sha256_guards(self):
        for data in [b"wrong pinned download", b"too long compared to the pinned bytes"]:
            with self.subTest(data=data), tempfile.TemporaryDirectory() as folder:
                target = Path(folder) / "locked"; target.write_bytes(b"preserve existing bytes")
                with patch.object(restore_modified, "urlopen", return_value=Response(data)):
                    with self.assertRaises(ValueError): restore_modified.download(self.row(), target)
                self.assertEqual(target.read_bytes(), b"preserve existing bytes")
                self.assertEqual([p.name for p in Path(folder).iterdir()], ["locked"])


class Response(io.BytesIO):
    def __init__(self, data, url="https://mediafilez.forgecdn.net/files/7065/24/example.jar"):
        super().__init__(data); self.url = url

    def geturl(self):
        return self.url


if __name__ == "__main__": unittest.main()
