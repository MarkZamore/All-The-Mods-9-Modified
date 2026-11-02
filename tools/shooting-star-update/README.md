# Shooting Star 1.5.1 / Rimulib 1.2.1 source update

The Shooting Star phase replaces two NEW files: requested Shooting Star Demo 1.4.4 → 1.5.1-demo and its NEW dependency Rimulib 1.1.2 → 1.2.1. That phase retains the Minecraft 1.20.1 / Forge 47.4.0 platform and BASE membership/pins. The later separately audited official ModernFix BASE replacement is recorded in tools/qa/modernfix-525-static.json; do not interpret this two-file phase as the complete current candidate. Vocaloid, Addition and SS-21 Quasar remain excluded. Official project links stay attached to their existing IDs in `library/mod-pages.json`.

Exact old/new rows, dependency ranges and limits are recorded in `tools/qa/shooting-star-151-static.json`. The old Rimulib retirement triple is added to `tools/legacy-files.json`; the old Shooting Star triple was already present. This authorizes cleanup only when old size and SHA256 match, not deletion by filename alone.

`audit_rimulib_api.py` reproduces the pinned mc1201 constant-pool reference check without starting Minecraft. Supply the four exact inputs from the documented old/new source locks:

```text
python tools/shooting-star-update/audit_rimulib_api.py --old-library /path/to/rimulib-1.1.2-forge.jar --new-library mods/rimulib-1.2.1-forge.jar --type95 mods/type-95-1.0.2.jar --shooting-star mods/the-shooting-star-demo-1.5.1-forge.jar --output /path/to/new-api-proof.json
```

The tool rejects different input hashes. Parsed output must equal `tools/qa/shooting-star-151-rimulib-api.json`: 120 Type95 member references / 49 library classes and 134 Shooting Star references / 58 classes, with no missing members/classes, changed staticness, reduced public visibility or changed class kind. This checks symbol compatibility only. It does not execute Mixins, opaque bootstrap targets, menus, world operations or every ability.

The new Gravitia capability and Rimulib world-shape classes include direct chunk-section/palette paths. The native singleplayer clone helper excludes published integrated servers; that is not a claim that other ability paths preserve a Steam/LAN world. The user forbids a custom Safety/framework, so none is introduced, and FTB claim/caster protection is not asserted. See the dedicated entry in `tools/approved-jar-update-safety.json`.

Native ModList, key registration, registry comparison, startup log comparison and the separate network investigation remain publication gates. A translated Gravitia key name is not proof of a registered binding. The old 557-ID inventory and 638-name stock table retain their old JAR hashes until actual candidate captures replace them through the normal inventory/key workflow. The runtime preset is held unchanged during that capture. Historical full-native and delivery-only receipts remain bound to their measured parent cohorts.
