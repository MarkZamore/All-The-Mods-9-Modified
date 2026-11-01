# Pinned local AI delivery

The pack mirrors Ollama 0.40.12 and the exact existing Qwen3:1.7b model in a separate, versioned [GitHub release](https://github.com/MarkZamore/All-The-Mods-9-Modified/releases/tag/ai-ollama-v0.40.12-qwen3-1.7b-8f68893c). The release contains the unchanged Windows runtime archive, all five model manifest descriptors, the exact manifest, licenses, attribution and SHA256 inventory. Large binaries are release assets, not Git or LFS files.

`launcher/ollama-recipe.json` binds the same runtime SHA256/size and embedded model manifest as the parent delivery. Its runtime URL and complete `model.blobUrls` map now use that release. The registry address remains the local Ollama manifest namespace; a launcher supporting `local-ai-blob-urls-v1` downloads every model blob from the declared map. There is no registry fallback for a partial map. The pack manifest requires this new feature in addition to its four existing features, so an older launcher cannot silently interpret the new delivery recipe.

This is a delivery update. All 532 content JARs, model weights, template, parameters, license layer, runtime executable archive, AI settings, control preset, translations and native abilities retain their exact bytes. No new world-writing route or permission behavior is introduced, so no Safety code/profile change is required. The separately documented Connection logger change records selected native exception stacks; it does not fix a multiplayer failure.

The historical full native receipt in `tools/qa/native-source-acceptance.json` remains bound to parent lock `0096874596826ede2b8250dc04f70c8db58b8d886d61d958cf69870e34537285`. It is not a repeated game run of the new recipe or logger. The delivery amendment records the three changed runtime files and their independent checks.

Ollama's own code uses the [MIT license](https://github.com/ollama/ollama/blob/v0.40.12/LICENSE). The unchanged archive retains its embedded third-party notices and terms; those components are not all described as MIT. Qwen Team / Alibaba Cloud publish [Qwen3-1.7B under Apache 2.0](https://huggingface.co/Qwen/Qwen3-1.7B/blob/main/LICENSE). Both the exact pinned model license layer and a separately named upstream license snapshot are supplied. `ATTRIBUTION-AND-LICENSES.md` on the release identifies the sources without substituting a different license blob into the model.

The release is versioned and SHA-pinned. GitHub's platform `immutable` flag is false; our publisher does not overwrite these assets. Repository-wide immutable-release settings are not enabled because the pack's separate `pack-latest` release deliberately rolls forward.

To independently download and hash every public asset without starting Ollama or Minecraft:

```text
python tools/ai-mirror/verify_public.py --inventory tools/ai-mirror/release-inventory.json --output /path/to/new-private-output
```

The verifier downloads all 13 assets, checks the complete API digests and sizes, manifest descriptors, archive notices and checksum inventory, then verifies the release asset IDs/digests again. Its report distinguishes actual public byte downloads from API-only verification. Store the downloaded binaries and run reports outside source control.
