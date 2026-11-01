"""Delivery gates for a complete model mirror; no game or runtime is started."""
import base64
import contextlib
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest

import generate_manifest


class AiMirrorFeatureTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.pack = Path(self.temp.name)
        (self.pack / 'launcher').mkdir()
        (self.pack / 'library').mkdir()
        self.manifest = {'config': {'digest': 'sha256:' + 'a' * 64, 'size': 1},
                         'layers': [{'digest': 'sha256:' + 'b' * 64, 'size': 2}]}
        raw = json.dumps(self.manifest).encode()
        self.recipe = {'model': {'manifestBase64': base64.b64encode(raw).decode(),
                                 'manifestSha256': hashlib.sha256(raw).hexdigest()}}
        self.descriptor = {'recipeFile': 'launcher/recipe.json'}
        self.write('launcher/launch-context.json', {})
        self.write('library/content.json', {'visibleModIds': []})

    def write(self, path, value):
        target = self.pack / path
        target.write_text(json.dumps(value), encoding='utf-8')
        return target

    def install(self):
        path = self.write('launcher/recipe.json', self.recipe)
        self.descriptor['recipeSha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
        self.write('launcher/local-ai.json', self.descriptor)

    def mirrored(self):
        self.recipe['model']['blobUrls'] = {c * 64: 'https://example.org/sha256-' + c * 64 for c in ('a', 'b')}

    def rejected(self):
        self.install()
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            generate_manifest.required_launcher_features(self.pack)

    def test_legacy_recipe_preserves_existing_four_features(self):
        self.install()
        self.assertEqual(generate_manifest.required_launcher_features(self.pack),
                         ['local-ai-native-v1', 'local-ai-recipe-v1', 'launch-context-v1', 'curated-mod-list-v1'])

    def test_complete_mirror_requires_new_feature_and_keeps_existing_four(self):
        self.mirrored(); self.install()
        self.assertEqual(generate_manifest.required_launcher_features(self.pack),
                         ['local-ai-native-v1', 'local-ai-recipe-v1', 'local-ai-blob-urls-v1',
                          'launch-context-v1', 'curated-mod-list-v1'])

    def test_no_ai_descriptor_does_not_require_ai_features(self):
        self.assertEqual(generate_manifest.required_launcher_features(self.pack),
                         ['launch-context-v1', 'curated-mod-list-v1'])

    def test_partial_extra_empty_and_prefixed_maps_are_rejected(self):
        for urls in ({}, None, {'a' * 64: 'https://example.org/a'},
                     {c * 64: 'https://example.org/' + c for c in ('a', 'b', 'c')},
                     {'sha256:' + c * 64: 'https://example.org/' + c for c in ('a', 'b')}):
            with self.subTest(urls=urls):
                self.recipe['model']['blobUrls'] = urls
                self.rejected()

    def test_map_rejects_http_credentials_and_fragment(self):
        for url in ('http://example.org/blob', 'https://user:secret@example.org/blob', 'https://example.org/blob#part'):
            with self.subTest(url=url):
                self.mirrored(); self.recipe['model']['blobUrls']['a' * 64] = url
                self.rejected()

    def test_manifest_hash_and_descriptor_hash_are_both_bound(self):
        self.mirrored(); self.recipe['model']['manifestSha256'] = '0' * 64
        self.rejected()
        self.install()
        self.write('launcher/recipe.json', {})
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            generate_manifest.required_launcher_features(self.pack)

    def test_recipe_traversal_is_rejected(self):
        for relative in ('../recipe.json', '/recipe.json', 'launcher\\recipe.json', 'C:/recipe.json'):
            with self.subTest(relative=relative):
                self.descriptor['recipeFile'] = relative
                self.rejected()


if __name__ == '__main__':
    unittest.main()
