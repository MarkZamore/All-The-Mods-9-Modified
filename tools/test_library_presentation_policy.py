import unittest
from library_presentation_policy import verify_presentation


class ComparisonPolicyTests(unittest.TestCase):
    def setUp(self):
        self.doc = {'modCountScope': 'all', 'visibleModIds': ['addon', 'chat'], 'mods': [
            {'id': 'base', 'isLibrary': False}, {'id': 'shared', 'isLibrary': False},
            {'id': 'addon', 'isLibrary': False}, {'id': 'chat', 'isLibrary': False},
            {'id': 'api', 'isLibrary': True}]}
        self.policy = {'baselineReference': {'baseContentIds': ['base', 'shared']},
                       'expectedAddedVisibleModIds': ['addon', 'chat'], 'normalStandaloneModIds': ['chat'],
                       'helperLibraryIds': ['api'], 'originalSharedContentExcludedFromAdded': ['shared']}

    def test_exact_difference_counts_addons_and_excludes_api(self):
        self.assertEqual({'base': 2, 'added': 2, 'total': 4}, verify_presentation(self.doc, self.policy))

    def test_new_hidden_mod_requires_review_instead_of_silent_count_drift(self):
        self.doc['mods'].append({'id': 'unexpected', 'isLibrary': False})
        with self.assertRaisesRegex(ValueError, 'Full minus base'):
            verify_presentation(self.doc, self.policy)

    def test_library_role_regression_is_rejected(self):
        self.doc['mods'][-1]['isLibrary'] = False
        with self.assertRaises(ValueError):
            verify_presentation(self.doc, self.policy)

    def test_shared_mod_cannot_be_counted_as_an_addition(self):
        self.doc['visibleModIds'].append('shared')
        with self.assertRaisesRegex(ValueError, 'Full minus base'):
            verify_presentation(self.doc, self.policy)

    def test_absent_base_id_is_rejected(self):
        self.doc['mods'] = [row for row in self.doc['mods'] if row['id'] != 'base']
        with self.assertRaises(ValueError):
            verify_presentation(self.doc, self.policy)
