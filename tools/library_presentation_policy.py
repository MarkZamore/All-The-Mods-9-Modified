"""Verify a pack-owned comparison of displayed mods; never set UI counts."""
from pathlib import Path
import json


def verify_presentation(document, policy):
    rows = {row['id']: row for row in document['mods']}
    all_ids = {key for key, row in rows.items() if not row['isLibrary']}
    visible_list = document.get('visibleModIds', [])
    visible = set(visible_list)
    base_list = policy['baselineReference']['baseContentIds']
    base = set(base_list)
    if len(base) != len(base_list) or len(visible) != len(visible_list):
        raise ValueError('Duplicate comparison or visible mod IDs')
    if document.get('modCountScope') != 'all':
        raise ValueError('Comparison presentation requires all count scope')
    if not base <= all_ids or base & visible or all_ids - base != visible:
        raise ValueError('Full minus base must equal exactly the visible additions')
    if visible != set(policy['expectedAddedVisibleModIds']):
        raise ValueError('Visible additions differ from reviewed policy')
    for key in policy['normalStandaloneModIds']:
        if key not in all_ids:
            raise ValueError('Standalone mod was classified as a library: ' + key)
    for key in policy['helperLibraryIds']:
        if key not in rows or not rows[key]['isLibrary'] or key in visible:
            raise ValueError('API must remain outside the displayed mod count: ' + key)
    for key in policy['originalSharedContentExcludedFromAdded']:
        if key not in base or key in visible:
            raise ValueError('Shared original mod must not repeat in additions: ' + key)
    return {'base': len(base), 'added': len(visible), 'total': len(all_ids)}


def verify_if_declared(pack, document):
    policy = Path(pack) / 'tools/library-presentation-policy.json'
    if policy.is_file():
        return verify_presentation(document, json.loads(policy.read_text(encoding='utf-8-sig')))
    return None
