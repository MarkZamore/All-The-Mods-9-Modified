# Reproducing client QA tooling

Production launcher code is release 417, commit
[`585bfc36c7e9b451426e1296214009878c9fe6ef`](https://github.com/MarkZamore/LANMinecraft/commit/585bfc36c7e9b451426e1296214009878c9fe6ef).
The default patch reproduces the protocol-5 harness. The actual protocol-4 QA7
instrumentation and its exact apply/source proof remain separately in `v4/`.

Use a separate clean checkout of the pinned commit with `core.autocrlf=false`
set before checkout. Run `git apply --check --whitespace=nowarn <patch>` followed
by `git apply --whitespace=nowarn <patch>`. This preserves the tested source's
literal CRLF/LF bytes; it does not fix or rewrite whitespace. A complete clean
checkout passed that check and all 15 changed files matched byte for
byte afterward. One unchanged project file is also bound among the sixteen
compilation source files in `verification.json`.

The patch changes only `tools/Atm9OriginalQa`: its console harness, launch-only
agent, tests and documentation. Follow its README for independent fixtures,
file-only production local AI preparation and explicit native `observe`.
Permission to observe is not a readiness claim. The agent checks that Minecraft
is already loaded and fully initialized, then inspects on the client executor.
Three consecutive healthy title/world observations precede actual ModList,
read-only GPU and bounded ResourceManager probes. Loading/error screens grant
no PASS. The probes change no resource, GPU state, framebuffer or quality.

Protocol 5 additionally permits individually requested native `give @s` and
plain-chat checks in a reserved unpublished single-player QA world. No requests
are created or sent automatically. World/UUID, local memory connection, one
server player, queue grammar, byte limits and replay guards are checked before
dispatch. A dispatch-return event alone proves no server effect, AI answer,
voice output or game/backend lifetime. See the patched README for the exact
commands and remaining runtime evidence requirements. No GUI/CUA input,
microphone action or outside-person communication is part of this tooling.

The actual game JDK17 standalone tests cover initialization, health, GPU and
resource guards plus native-request grammar/scope/replay using fake endpoints.
All 13 production QA class files in the agent exactly match that
safety-test compilation; fake/test classes are absent from the JAR. CLI and
process identity tests are separately bound in `verification.json`. Agent
SHA256: `1144efcb66fba27d8fdd897cc18ce03147035f0bc97d2df7077c921eec7a2b1b`. QA harness SHA256: `7dd7997a3536a45a029437a61ef1449d46632866ca9bd67102febc2bf1a1feb5`.

Build production Debug at the pinned commit with `ReleaseNumber=417`, then build
the QA project with `BuildProjectReferences=false`. The verified production
assembly hash and actual SRG method signatures are recorded in the report.
No production source, gameplay JAR, world data or compatibility setting is
patched by this QA source patch. Logs/paths remain private fixture evidence.
No runtime client/world, native chat, AI lifecycle or Steam PASS is claimed by
these standalone preparation tests.

Patch SHA256: `465bc1bf6e8e1bc8ea56b1a44748d7429cc363157168f23c8e89226fa280f7e2`.
