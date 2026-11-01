# Bounded Connection exception diagnostics

Minecraft 1.20.1 / Forge 47.4.0 emits the caught exception stack in `Connection.exceptionCaught` at DEBUG. The ordinary bounded INFO configuration does not retain it. The configuration now retains only the four exact Throwable-bearing messages from that method, while keeping INFO/WARN/ERROR and rejecting other Connection DEBUG output, including packet traces.

This is a diagnostic change. It does not fix or identify the cause of a multiplayer disconnect and does not alter network traffic, identity, game mechanics or mods.

The fixture uses real Log4j 2.19.0 API/core JARs. Compile `ConnectionLogProbe.java` with those two JARs on the classpath, then run it in an empty temporary directory with `-Dlog4j.configurationFile=<absolute path to connection-throwable-filter.probe.xml>`. The result file `probe-filter.log` must contain four `ArrayIndexOutOfBoundsException` stacks, EXPECTED_INFO, EXPECTED_WARN and EXPECTED_ERROR (including its stack). It must not contain UNWANTED_PACKET_TRACE or UNWANTED_OTHER_DEBUG. The fixture uses a standard pattern so custom Minecraft formatting plugins are outside its scope.

The native bytecode proof is tied to the exact Forge client JAR SHA256 in `connection-throwable-filter-proof.json`. `javap -p -c` shows the four DEBUG `(String, Throwable)` calls in `exceptionCaught`, and the static initializer obtains the logger through `LogUtils.getLogger`. Recheck these sites if changing the Minecraft or Forge JAR.