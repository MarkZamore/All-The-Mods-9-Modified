"""Download and verify every versioned AI mirror asset; never starts a runtime."""
from pathlib import Path
import argparse, concurrent.futures, datetime, hashlib, json, os, subprocess, time
import urllib.request, zipfile


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inventory', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--repo', default='MarkZamore/All-The-Mods-9-Modified')
    args = parser.parse_args()
    expected = json.loads(args.inventory.read_text(encoding='utf-8'))
    tag = expected['tag']; rows = expected['assets']
    assert len(rows) == len({r['name'] for r in rows}) == 13
    output = args.output.resolve(); output.mkdir(parents=True, exist_ok=False)
    prefix = f'https://github.com/{args.repo}/releases/download/{tag}/'

    def release():
        return json.loads(subprocess.check_output(['gh', 'api', f'repos/{args.repo}/releases/tags/{tag}'], text=True, encoding='utf-8'))

    before = release()
    assert before['draft'] is False and before['tag_name'] == tag
    api = {r['name']: r for r in before['assets']}
    assert set(api) == {r['name'] for r in rows}
    for row in rows:
        name = row['name']; assert Path(name).name == name and '/' not in name and '\\' not in name and ':' not in name
        item = api[name]
        assert item['state'] == 'uploaded' and item['size'] == row['sizeBytes'] and item.get('digest') == 'sha256:' + row['sha256']
        assert item['browser_download_url'] == prefix + name

    def fetch(row):
        destination = output / row['name']; partial = destination.with_name(destination.name + '.part')
        for attempt in range(3):
            try:
                h = hashlib.sha256(); size = 0
                request = urllib.request.Request(prefix + row['name'], headers={'User-Agent':'LANMinecraft-ImmutableAiMirrorVerification/1.0','Cache-Control':'no-cache'})
                with urllib.request.urlopen(request, timeout=90) as response, partial.open('wb') as target:
                    while block := response.read(1024 * 1024):
                        size += len(block); assert size <= row['sizeBytes']
                        h.update(block); target.write(block)
                assert size == row['sizeBytes'] and h.hexdigest() == row['sha256'], row['name']
                os.replace(partial, destination)
                return {**row, 'actualPublicDownloadVerified':True}
            except Exception:
                partial.unlink(missing_ok=True)
                if attempt == 2: raise
                time.sleep(attempt + 1)

    verified = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for completed in concurrent.futures.as_completed([pool.submit(fetch, row) for row in rows]):
            verified.append(completed.result()); print(f'Actual AI mirror assets verified: {len(verified)}/13', flush=True)
    index = json.loads((output / 'mirror-index.json').read_text(encoding='utf-8'))
    assert index['releaseTag'] == tag and index['allFiveManifestDescriptorsIncluded'] is True
    indexed = {r['name']: r for r in index['assets']}
    assert set(indexed) == set(api) - {'mirror-index.json','SHA256SUMS.txt'}
    for row in indexed.values():
        actual = api[row['name']]
        assert actual['size'] == row['sizeBytes'] and actual['digest'] == 'sha256:' + row['sha256']
    sums = (output / 'SHA256SUMS.txt').read_text(encoding='utf-8').splitlines()
    assert len(sums) == 12
    for line in sums:
        digest, name = line.split('  ', 1)
        assert name in api and api[name]['digest'] == 'sha256:' + digest and sha(output / name) == digest
    manifest_name = next(r['name'] for r in rows if r['name'].endswith('.manifest.json'))
    manifest_raw = (output / manifest_name).read_bytes(); manifest = json.loads(manifest_raw)
    assert hashlib.sha256(manifest_raw).hexdigest() == index['manifestSha256']
    blobs = [manifest['config'], *manifest['layers']]; assert len(blobs) == 5
    for row in blobs:
        digest = row['digest'].removeprefix('sha256:'); file = output / ('sha256-' + digest)
        assert file.stat().st_size == row['size'] and sha(file) == digest
    runtime_name = next(r['name'] for r in rows if r['name'].startswith('ollama-windows-amd64-'))
    with zipfile.ZipFile(output / runtime_name) as archive:
        assert 'ollama.exe' in archive.namelist()
        for row in index['runtimeArchiveNoticesRetained']:
            raw = archive.read(row['path'])
            assert len(raw) == row['sizeBytes'] and hashlib.sha256(raw).hexdigest() == row['sha256']
    after = release()
    stable = lambda value: sorted((r['id'],r['name'],r['size'],r.get('digest'),r['state']) for r in value['assets'])
    assert before['id'] == after['id'] and stable(before) == stable(after) and after['draft'] is False
    report = {'schemaVersion':1,'status':'PASS','verifiedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'repository':args.repo,'releaseTag':tag,'releaseUrl':after['html_url'],'releaseId':after['id'],
              'githubPlatformImmutableFlag':after.get('immutable',False),
              'versionedContentPinnedPublisherNeverClobbers':True,
              'actualPublicAssetsDownloaded':len(verified),'actualPublicBytesDownloaded':sum(r['sizeBytes'] for r in verified),
              'allApiFullSha256AndSizesVerified':True,'allFiveBlobsAndExactManifestVerified':True,
              'licenseAssetsAndRuntimeEmbeddedNoticesVerified':True,'releaseAssetIdsAndDigestsStableBeforeAfter':True,
              'inventorySha256':sha(args.inventory),'modelManifestSha256':index['manifestSha256'],
              'runtimeAndModelBytesChanged':False,'runtimeOrGameStarted':False,'packRecipePublishedByThisCheck':False,
              'assets':sorted(verified,key=lambda r:r['name'])}
    destination = output / 'public-verification-report.json'
    destination.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='assets'})); print('reportSha256=' + sha(destination))


if __name__ == '__main__': main()
