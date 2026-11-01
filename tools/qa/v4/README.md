# Reproducing the final client QA harness

Production launcher code is release 417, commit
[`585bfc36c7e9b451426e1296214009878c9fe6ef`](https://github.com/MarkZamore/LANMinecraft/commit/585bfc36c7e9b451426e1296214009878c9fe6ef).
Use a separate clean checkout of that exact commit. For byte-identical Windows
working files set `core.autocrlf=true` before checkout, then run
`git apply --check <path-to-launcher-417-qa.patch>` and
`git apply <path-to-launcher-417-qa.patch>`. The twelve affected files were verified
byte for byte after applying to a complete clean checkout of that commit.

The patch changes only `tools/Atm9OriginalQa`: its console harness, launch-only
agent, build/test scripts and documentation. Follow the patched README for
independent fixtures, production instance/file-only local AI preparation and
the explicit native `observe` permission. Observation permission is not a
readiness claim. The v4 agent checks an already loaded Minecraft class using
the actual JDK17 initialized-state query, observes on its native executor and
requires three consecutive healthy title or joined-world samples before
recording the actual ModList. Loading/error screens grant no PASS. Legacy
visual `ready` remains supported. A running v2 JVM cannot be upgraded in place.

Run `Test-AgentSafety.ps1` on the complete game JDK17 before using the agent.
The recorded standalone validation covers cold, in-progress, successful and
failed class initialization and the native health/deadline gates. It never
attaches to or starts a game. All 5 agent class files exactly
match the safety-test compilation. Fake GL/resource fixtures verify health
guards, absent-context handling, the exact GPU query list and the 1 MiB resource
limit. All synthetic screen/GL/resource classes are absent from that JAR.
Agent SHA256: `8b71e68ab1ed398d338020da41c8611578d927ba1c9cd1bf1ce444a9ece31c42`.

After native health the read-only GPU probe records the actual current context,
texture limit and driver strings, without changing GPU state. A fresh v4 launch
can additionally request one `--resource-probe namespace:path`; it records the
actual selected resource source pack, byte length and SHA256 at healthy title
and world stages. Neither probe asserts visual quality or suppresses errors.

Build production Debug code at the pinned commit with `ReleaseNumber=417`, then
build the QA tool with `BuildProjectReferences=false`. This avoids an older
assembly stamp being carried over into a new fixture. The verified production
assembly is bound in `verification.json`; no production source is patched.

The existing explicit `--mixin-export` diagnostic also enables the native
`mixin.dumpTargetOnFailure` option. No transformer, gameplay mod, replacement
class, model/quality change or production launcher behavior is added. Process
guards prefer matching terminal evidence and verify Java identity/start time;
they never control or terminate a PID. All
logs, native target dumps and local paths remain private fixture evidence.
This tooling is outside the managed game payload. Tool/test success does not
establish a full client, world, AI lifecycle or Steam runtime PASS.

Patch SHA256: `17873957dc9a7a2bd49a6c8a6a54e52dde9b061427a2dddec92efd0a841a9562`. Full sanitized file/source/JDK bindings and
clean-checkout apply proof are in `verification.json`.
