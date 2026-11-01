# Frozen Russian Verity 6.0.0 fork

This tool implements the user's explicit request to edit the Verity JAR and freeze its version. It is built afresh from the official Verity JE 6.0.0 file, not from any earlier ATM9 Modified implementation. It does not create a second mod, runtime helper, agent or mixin. The original mod ID remains `verity`; the derivative version is `6.0.0-ru.1`. Original author credits and bundled dependencies remain intact.

Official source: [Verity JE file 9300987](https://www.curseforge.com/minecraft/mc-mods/verity-je/files/9300987), 256,881,551 bytes, SHA256 `f76f641f17ea3e3b2e8486596790ae65c27c2b016fae6ed8557c67887816b7d0`. A different input fails before patching.

`translations.json` comes from a new ASM inventory of that exact author file. It changes human text at named class/method/string sites, including exact occurrence ordinals where UI text shares a value with protocol comparisons. Technical IDs, command names, tools, enum names and configuration keys retain their identities. The full Russian XML preserves the author's tag hierarchy, placeholder multiset, tool identifiers and character/gameplay rules, and requires Russian answers.

The original English fallback and the new Russian language file contain the same 21 native resource keys. Four existing enums gain display-only `toString` methods because the verified YACL 3.6.6 formatter uses them; `name`, `valueOf`, ordinals and stored configuration values remain unchanged. The native required-name gate accepts both `Verity` and `Верити` while preserving arbitrary custom names. Native speech normalization also accepts common Russian recognition spellings. The actual generated methods have positive and negative JVM tests.

The author LOCAL speech engine keeps its original Sherpa-onnx 1.13.3 libraries, audio playback, cancellation and spatial effects. Its bundled voice becomes official Russian Piper Denis medium with the matching token table and original Russian-capable eSpeak data. The author NATIVE recognition engine receives official multilingual Whisper **base** int8 and explicit `ru`/`transcribe`; it uses a distinct extraction directory so an old English tiny cache cannot be reused. Pins, source revisions and SHA256 are in `speech-pins.json`. The author microphone capture path is unchanged: only explicit native push-to-talk opens and reads its audio line. Runtime preparation never records a microphone.

`audio.json` records three fresh Russian recordings and their exact bytes. The introduction preserves the meaning of the clearly transcribed author introduction. The two brief box calls are explicitly **contextual adaptations**, not claimed exact transcripts of ambiguous source speech. Their spoken text is `Привет!` and `Кто-нибудь здесь?`. Box0 changes from about 0.522 to 0.600 seconds, box2 from about 0.661 to 1.091 seconds, and the introduction from about 5.590 to 5.586 seconds. The short box1 effect, cinematic soundtrack, other music/effects and all 248 intro frames remain byte-identical. Reviewed frame samples contain the character and the `Verity JE` brand, which is retained. No music, cinematic sequence, effect or mechanic is disabled.

## Rebuild

The offline preparation machine needs Python 3.11+ and JDK 17+. Players download the finished JAR through the normal pack manifest and do not compile anything or install speech tooling.

```powershell
$env:JAVA_HOME = 'C:\Tools\jdk-25.0.2'
python tools/verity_russian.py --input path/to/verity-6.0.0.jar --output artifacts/verity-6.0.0-ru.1.jar
```

The first rebuild downloads the six immutable official voice/model assets. Reuse requires size and SHA256 to match. ASM 9.8 libraries are pinned and distributed with their BSD notice. The patcher is compiled only for preparation and is never placed in the mod. ZIP timestamps/order are fixed; the sidecar report lists every changed entry, old/new hashes and sizes, and the zlib version used for reproducibility.

The ZIP creator field is explicitly the frozen artifact's value `0`, including both nested model ZIPs; it does not inherit the preparation OS. Java executables use the platform's normal suffix. XML and notice line endings are canonicalized to the frozen bytes (LF, except the original ASM notice's CRLF). Full fresh-author rebuilds produced the same SHA256 `45fc05ee600c24e989a5a2c17fab099fa5bd15415ee9d848e73885e8f42b85d8` on Windows Python 3.12.10 / zlib 1.3.1, WSL Linux Python 3.14.4 / zlib 1.3.1, and the official GitHub Actions Ubuntu24 Python 3.12.16 build on WSL with both zlib 1.3.1 and Ubuntu24's official zlib 1.3. JDK25 was used on both platforms. This is local execution proof, not a claim that a remote GitHub workflow has completed. Other compression-library versions still require an exact-hash check.

`VerifyPatch.java` loads generated enum methods with `-Xverify:all`, executes the actual generated name-gate and speech-normalization bytecode, verifies enum serialization identities and checks the instruction structure of all other changed-class gameplay methods. Only the exact native STT-builder method and required-name gate have reviewed non-text changes; no executable class is added.

`VerifySpeech.java` is separate native CPU QA, not a game component. It generates WAV without playback and transcribes supplied clips without opening a microphone or contacting a server. The actual source-model bytes in the built JAR must be used for the final native check. A synthetic Russian Windows SAPI recording provides a recognizer input independent of the Piper voice. Record the actual transcripts; speech recognition is probabilistic and must not be called error-free.

The checked-in Ogg recordings are fixed reproducible build inputs. They were generated with `VerifySpeech`, the pinned Sherpa/Piper voice and the text in `audio.json`, then encoded using Python soundfile 0.13.1 / libsndfile 1.2.2. Re-encoding can change Ogg stream serials, so restoration copies their pinned bytes rather than regenerating them.

The patch report and native tests are separate from full client/new-world acceptance, Ollama inference and the native backend lifecycle. Those checks must run on the final pack revision. Raw local QA output is private evidence and is not a publication payload.
