"""Verify a three-file delivery delta against the previously downloaded public pack."""
from pathlib import Path
import argparse
import base64
import copy
import datetime
import hashlib
import json
import sys
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import generate_manifest

PARENT_REVISION = '5d1f1db1062207431b2c698aed580de1c7cfbd87'
PARENT_MANIFEST = '626ca4e2a96f41bdffcb55e3c4921eb6b9764a7528717c709c9aee81b09599b6'
PARENT_LOCK = '0096874596826ede2b8250dc04f70c8db58b8d886d61d958cf69870e34537285'
PARENT_PUBLIC_PROOF = '03da778e8194f891a922579305dccbd079f2503ac290a56c707b7502ae20c937'
PARENT_NATIVE_RECEIPT = '21daa63e9ed6367cb333a3aa82ff4c5a9436b94d0234e9f658938c98dadc4414'
CHANGED = {'config/log4j2.xml', 'launcher/local-ai.json', 'launcher/ollama-recipe.json'}


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def verify(pack, parent_downloads, parent_lock, parent_public_proof, ai_proof):
    manifest_path = parent_downloads / 'pack-manifest.json'
    assert sha(manifest_path) == PARENT_MANIFEST
    parent = load(manifest_path)
    assert parent['revision'] == PARENT_REVISION and len(parent['files']) == 1915
    assert sha(parent_lock) == PARENT_LOCK and sha(parent_public_proof) == PARENT_PUBLIC_PROOF
    assert load(parent_public_proof)['status'] == 'PASS'
    assert sha(pack / 'tools/qa/native-source-acceptance.json') == PARENT_NATIVE_RECEIPT
    before = {row['path']: row for row in parent['files']}
    shipped = {'portable-pack.json'}
    for root in generate_manifest.SCAN_ROOTS:
        shipped.update(generate_manifest.walk_root(pack, root))
    portable = load(pack / 'portable-pack.json')
    if portable.get('clientJar'):
        shipped.add(portable['clientJar'])
    assert shipped == set(before)
    after = {name: {'path': name, 'sizeBytes': (pack / name).stat().st_size,
                    'sha256': sha(pack / name)} for name in shipped}
    changed = {name for name in shipped if after[name] != before[name]}
    assert changed == CHANGED, changed
    jars = [name for name in shipped if name.startswith('mods/') and name.endswith('.jar')]
    assert len(jars) == 532 and all(before[name] == after[name] for name in jars)

    def old_bytes(relative):
        asset, = [asset for asset in parent['assets'] if relative in asset['covers']]
        path = parent_downloads / asset['name']
        assert path.stat().st_size == asset['sizeBytes'] and sha(path) == asset['sha256']
        with zipfile.ZipFile(path) as archive:
            raw = archive.read(relative)
        assert len(raw) == before[relative]['sizeBytes']
        assert hashlib.sha256(raw).hexdigest() == before[relative]['sha256']
        return raw

    old_recipe = json.loads(old_bytes('launcher/ollama-recipe.json'))
    new_recipe = load(pack / 'launcher/ollama-recipe.json')
    reduced_recipe = copy.deepcopy(new_recipe)
    reduced_recipe['runtime']['archiveUrl'] = old_recipe['runtime']['archiveUrl']
    urls = reduced_recipe['model'].pop('blobUrls')
    assert reduced_recipe == old_recipe
    old_descriptor = json.loads(old_bytes('launcher/local-ai.json'))
    descriptor = load(pack / 'launcher/local-ai.json')
    reduced_descriptor = dict(descriptor, recipeSha256=old_descriptor['recipeSha256'])
    assert reduced_descriptor == old_descriptor
    assert descriptor['recipeSha256'] == after['launcher/ollama-recipe.json']['sha256']
    old_lock = load(parent_lock); new_lock = load(pack / 'tools/modified-lock.json')
    reduced_lock = copy.deepcopy(new_lock)
    old_support = {row['path']: row for row in old_lock['supportFiles']}
    reduced_lock['supportFiles'] = [old_support[row['path']] if row['path'] in CHANGED else row
                                    for row in reduced_lock['supportFiles']]
    assert reduced_lock == old_lock and len(new_lock['supportFiles']) == 18
    for row in new_lock['supportFiles']:
        if row['path'] in CHANGED:
            assert row['sha256'] == after[row['path']]['sha256'] and row['sizeBytes'] == after[row['path']]['sizeBytes']
    native_filter = load(pack / 'tools/qa/connection-throwable-filter-proof.json')
    assert native_filter['status'] == 'PASS' and all(native_filter['syntheticAssertions'].values())
    assert native_filter['sourceConfigSha256'] == before['config/log4j2.xml']['sha256']
    assert native_filter['candidateConfigSha256'] == after['config/log4j2.xml']['sha256']
    assert native_filter['mechanicsChanged'] is False and native_filter['networkErrorFixed'] is False
    actual_ai = load(ai_proof)
    assert actual_ai['status'] == 'PASS' and actual_ai['actualPublicAssetsDownloaded'] == 13
    assert actual_ai['allFiveBlobsAndExactManifestVerified'] is True
    assert actual_ai['runtimeOrGameStarted'] is False and actual_ai['runtimeAndModelBytesChanged'] is False
    ai_assets = {row['name']: row for row in actual_ai['assets']}
    release_prefix = ('https://github.com/' + actual_ai['repository'] + '/releases/download/'
                      + actual_ai['releaseTag'] + '/')
    runtime = new_recipe['runtime']
    runtime_asset = ai_assets[runtime['archiveUrl'].rsplit('/', 1)[1]]
    assert runtime['archiveUrl'] == release_prefix + runtime_asset['name']
    assert runtime_asset['sha256'] == runtime['sha256'] and runtime_asset['sizeBytes'] == runtime['sizeBytes']
    raw_manifest = base64.b64decode(new_recipe['model']['manifestBase64'], validate=True)
    model_manifest = json.loads(raw_manifest)
    assert hashlib.sha256(raw_manifest).hexdigest() == actual_ai['modelManifestSha256']
    descriptors = [model_manifest['config'], *model_manifest['layers']]
    assert len(descriptors) == len(urls) == 5
    for row in descriptors:
        digest = row['digest'][7:]
        asset = ai_assets[urls[digest].rsplit('/', 1)[1]]
        assert urls[digest] == release_prefix + asset['name']
        assert asset['sha256'] == digest and asset['sizeBytes'] == row['size']
        assert asset['actualPublicDownloadVerified'] is True
    features = generate_manifest.required_launcher_features(pack)
    assert features == ['local-ai-native-v1', 'local-ai-recipe-v1', 'local-ai-blob-urls-v1',
                        'launch-context-v1', 'curated-mod-list-v1']
    return {'schemaVersion': 1, 'status': 'PASS', 'kind': 'delivery-and-bounded-logging-amendment',
            'verifiedAtUtc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'parentSourceRevision': PARENT_REVISION, 'parentSourceLockSha256': PARENT_LOCK,
            'parentPublicManifestSha256': PARENT_MANIFEST, 'parentFullPublicProofSha256': PARENT_PUBLIC_PROOF,
            'historicalNativeReceiptSha256': PARENT_NATIVE_RECEIPT,
            'currentSourceLockSha256': sha(pack / 'tools/modified-lock.json'),
            'runtimeFiles': len(shipped), 'unchangedRuntimeFiles': len(shipped) - len(changed),
            'changedRuntimeFiles': [{'before': before[name], 'after': after[name]} for name in sorted(changed)],
            'unchangedContentJars': len(jars), 'supportFiles': 18,
            'runtimeArchiveAndModelBytesUnchanged': True, 'allFiveBlobUrlsPublicBytesVerified': True,
            'aiMirrorPublicProofSha256': sha(ai_proof),
            'aiMirrorInventorySha256': sha(pack / 'tools/ai-mirror/release-inventory.json'),
            'nativeLoggingFilterProofSha256': sha(pack / 'tools/qa/connection-throwable-filter-proof.json'),
            'requiredLauncherFeatures': features,
            'safetyReview': 'All532 content JARs/native abilities and AI payload bytes are unchanged. Only declarative download URLs and an exact native caught-Throwable logger filter change; no new world-writing or permission route is introduced.',
            'newGameRunClaimed': False, 'networkFailureFixed': False,
            'limits': ['Historical native/gameplay receipt remains bound to its parent009 lock.',
                       'New GitHub pack publication and catalog synchronization require separate public-delivery checks.',
                       'The Connection filter adds diagnostic stacks only; no disconnect cause or gameplay fix is established.']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pack', type=Path, required=True)
    parser.add_argument('--parent-downloads', type=Path, required=True)
    parser.add_argument('--parent-lock', type=Path, required=True)
    parser.add_argument('--parent-public-proof', type=Path, required=True)
    parser.add_argument('--ai-public-proof', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = verify(args.pack, args.parent_downloads, args.parent_lock, args.parent_public_proof, args.ai_public_proof)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({key: value for key, value in result.items() if key not in ('changedRuntimeFiles', 'limits')}))
    print('reportSha256=' + sha(args.output))


if __name__ == '__main__':
    main()
