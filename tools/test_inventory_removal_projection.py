"""Source projections may subtract known removals, never impersonate a fresh capture."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import pack_library


class InventoryRemovalProjectionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.pack = Path(self.tmp.name)
        self.parent = {"schemaVersion": 1, "minecraftVersion": "1.20.1",
                       "sourceJars": {"mods/a.jar": "a"*64, "mods/b.jar": "b"*64},
                       "mods": [{"id": "a", "version": "1"}, {"id": "b", "version": "1"}],
                       "evidenceUtc": "historical", "observationSha256": "c"*64}
        raw = (json.dumps(self.parent) + "\n").encode()
        (self.pack / "parent.json").write_bytes(raw)
        self.current = {**self.parent, "sourceJars": {"mods/a.jar": "a"*64},
                        "mods": [self.parent["mods"][0]],
                        "derivation": {"kind": "exact-removal-projection",
                            "parentInventory": {"path": "parent.json", "sha256": hashlib.sha256(raw).hexdigest()},
                            "removedSourceJars": {"mods/b.jar": "b"*64}, "removedModIds": ["b"],
                            "freshNativeObservationClaimed": False}}

    def test_exact_removal_retains_historical_evidence_without_new_capture(self):
        self.assertEqual("exact-removal-projection", pack_library.inventory_evidence_kind(self.pack, self.current))
        self.assertEqual("historical", self.current["evidenceUtc"])
        self.assertEqual("native-observation", pack_library.inventory_evidence_kind(self.pack, self.parent))

    def test_retained_jar_change_is_rejected(self):
        self.current["sourceJars"]["mods/a.jar"] = "d"*64
        with self.assertRaises(ValueError): pack_library.inventory_evidence_kind(self.pack, self.current)

    def test_extra_mod_subtraction_is_rejected(self):
        self.current["mods"] = []
        with self.assertRaises(ValueError): pack_library.inventory_evidence_kind(self.pack, self.current)

    def test_parent_hash_and_path_are_guarded(self):
        bad = copy.deepcopy(self.current)
        bad["derivation"]["parentInventory"]["sha256"] = "0"*64
        with self.assertRaises(ValueError): pack_library.inventory_evidence_kind(self.pack, bad)
        self.current["derivation"]["parentInventory"]["path"] = "../parent.json"
        with self.assertRaises(ValueError): pack_library.inventory_evidence_kind(self.pack, self.current)

    def test_fresh_observation_claim_or_changed_evidence_is_rejected(self):
        self.current["derivation"]["freshNativeObservationClaimed"] = True
        with self.assertRaises(ValueError): pack_library.inventory_evidence_kind(self.pack, self.current)
        self.current["derivation"]["freshNativeObservationClaimed"] = False
        self.current["evidenceUtc"] = "new-unobserved-time"
        with self.assertRaises(ValueError): pack_library.inventory_evidence_kind(self.pack, self.current)

    def test_a_projected_parent_cannot_impersonate_the_last_actual_capture(self):
        parent = {**self.parent, "derivation": {"kind": "exact-removal-projection"}}
        raw = (json.dumps(parent) + "\n").encode()
        (self.pack / "parent.json").write_bytes(raw)
        self.current["derivation"]["parentInventory"]["sha256"] = hashlib.sha256(raw).hexdigest()
        with self.assertRaises(ValueError): pack_library.inventory_evidence_kind(self.pack, self.current)
