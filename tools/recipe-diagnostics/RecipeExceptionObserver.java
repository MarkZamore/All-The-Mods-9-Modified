import com.sun.jdi.*;
import com.sun.jdi.connect.*;
import com.sun.jdi.event.*;
import com.sun.jdi.request.*;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.nio.file.attribute.BasicFileAttributes;
import java.security.MessageDigest;
import java.time.Instant;
import java.util.*;
import java.util.concurrent.*;
import java.util.jar.*;
import javax.tools.ToolProvider;

/** Local JDI observation only. No target method invocation, agent load, class mutation or heap dump. */
public final class RecipeExceptionObserver {
    static final String CALLER = "com.smashingmods.alchemylib.api.item.IngredientStack";
    static final String SERIALIZER = "com.smashingmods.alchemistry.common.recipe.dissolver.DissolverRecipeSerializer";
    static final String LIB_SHA = "1bf4d28c70fb671c5b2ca72bfd12f74594db6319f67be7b50bb7bce5d11c4466";
    static final String CHEM_SHA = "fe993f8e0586a9c65209c230de21225991d9e91c5482a262ce80b3eab2eb02e1";
    static final String STEAM_CLASS = "link.e4steam.steam.SteamConnectionBridge";
    static final String STEAM_JAR = "e4steam-forge-mc1.18.2-1.20.2-v0.3.4-lanmc-native-ui.1.jar";
    static final String STEAM_SHA = "68ba6bdce76868e2cb43359a13416dfa1b011c628c13b6c4266b653c765b5c40";
    static final String HEADER = "[RecipeExceptionObserver v7] ";
    static final int MAX_BYTES = 256 * 1024;
    static final int MAX_EVENTS = 8;
    static final int MAX_TERMINALS = 24;
    static final int MAX_KEEPALIVES = 32;
    record Config(long pid, long parentPid, Path game, Path output, String librarySha, String chemistrySha, int maxEvents, String steamSha, int maxTerminals, int maxKeepAlives) {
        Config(long pid, long parentPid, Path game, Path output, String librarySha, String chemistrySha, int maxEvents) {
            this(pid, parentPid, game, output, librarySha, chemistrySha, maxEvents, STEAM_SHA, MAX_TERMINALS, MAX_KEEPALIVES);
        }
        Config(long pid, long parentPid, Path game, Path output, String librarySha, String chemistrySha, int maxEvents, String steamSha) {
            this(pid, parentPid, game, output, librarySha, chemistrySha, maxEvents, steamSha, MAX_TERMINALS, MAX_KEEPALIVES);
        }
    }
    record Candidate(long pid, Path game) { }
    record Site(String className, String methodName, String signature) { }
    static final List<Site> TERMINALS = List.of(
        new Site(STEAM_CLASS, "close", "(Z)V"), new Site(STEAM_CLASS, "beginGracefulClose", "()V"),
        new Site("net.minecraft.network.Connection", "channelInactive", "(Lio/netty/channel/ChannelHandlerContext;)V"),
        new Site("net.minecraft.network.Connection", "exceptionCaught", "(Lio/netty/channel/ChannelHandlerContext;Ljava/lang/Throwable;)V"),
        new Site("net.minecraft.network.Connection", "m_129507_", "(Lnet/minecraft/network/chat/Component;)V"),
        new Site("net.minecraft.client.multiplayer.ClientPacketListener", "m_7231_", "(Lnet/minecraft/network/protocol/game/ClientboundKeepAlivePacket;)V"),
        new Site("net.minecraft.server.network.ServerGamePacketListenerImpl", "m_5683_", "(Lnet/minecraft/network/protocol/game/ServerboundKeepAlivePacket;)V"),
        new Site("net.minecraft.server.network.ServerGamePacketListenerImpl", "m_9942_", "(Lnet/minecraft/network/chat/Component;)V"));
    static boolean keepAliveSite(Site site) { return site.methodName.equals("m_7231_") || site.methodName.equals("m_5683_"); }

    public static void main(String[] args) throws Exception {
        if (args.length >= 1 && args[0].equals("--self-test")) {
            if (args.length != 3) throw new IllegalArgumentException("--self-test ARTIFACT_DIRECTORY FULL_JDK17_JAVA");
            selfTest(Path.of(args[1]), Path.of(args[2])); return;
        }
        if (args.length >= 1 && args[0].equals("--discover")) {
            Map<String, String> discoveredOptions = options(Arrays.copyOfRange(args, 1, args.length));
            if (!discoveredOptions.keySet().equals(Set.of("--minecraft-root")))
                throw new IllegalArgumentException("--discover accepts only --minecraft-root DIRECTORY");
            Candidate target = discover(Path.of(required(discoveredOptions, "--minecraft-root")), LIB_SHA, CHEM_SHA);
            observe(new Config(target.pid, target.pid, target.game, target.game.resolve("logs/debug.log"), LIB_SHA, CHEM_SHA, MAX_EVENTS),
                () -> System.out.println("OBSERVER_READY: Diagnostics ready; repeat the connection now."));
            return;
        }
        Map<String, String> options = options(args);
        if (!options.keySet().stream().allMatch(key -> Set.of("--pid", "--parent-pid", "--game").contains(key)))
            throw new IllegalArgumentException("Only --pid, --parent-pid and --game are accepted");
        long pid = Long.parseLong(required(options, "--pid"));
        Path game = Path.of(required(options, "--game")).toAbsolutePath().normalize();
        observe(new Config(pid, Long.parseLong(options.getOrDefault("--parent-pid", String.valueOf(pid))), game,
            game.resolve("logs/debug.log"), LIB_SHA, CHEM_SHA, MAX_EVENTS), () -> System.out.println("OBSERVER_READY pid=" + pid));
    }

    static Candidate discover(Path minecraftRoot, String librarySha, String chemistrySha) throws Exception {
        return discover(minecraftRoot, librarySha, chemistrySha, STEAM_SHA);
    }
    static Candidate discover(Path minecraftRoot, String librarySha, String chemistrySha, String steamSha) throws Exception {
        Path root = safe(minecraftRoot);
        if (!Files.isDirectory(root.resolve("Launcher/JavaRuntimes")) || !Files.isDirectory(root.resolve("Personal/Instances")))
            throw new SecurityException("Expected portable Minecraft root with Launcher/JavaRuntimes and Personal/Instances");
        Path instances = safe(root.resolve("Personal/Instances"));
        String ownUser = ProcessHandle.current().info().user().orElseThrow(() -> new SecurityException("Cannot verify observer owner"));
        var candidates = new ArrayList<Candidate>();
        List<ProcessHandle> javaProcesses;
        try (var processes = ProcessHandle.allProcesses()) {
            javaProcesses = processes.filter(process -> process.pid() != ProcessHandle.current().pid() && process.isAlive())
                .filter(process -> process.info().user().map(ownUser::equalsIgnoreCase).orElse(false))
                .filter(process -> process.info().command().map(command -> Set.of("java", "javaw", "java.exe", "javaw.exe")
                    .contains(Path.of(command).getFileName().toString().toLowerCase(Locale.ROOT))).orElse(false))
                .limit(65).toList();
        }
        if (javaProcesses.size() > 64) throw new IllegalStateException("More than 64 Java processes are running; close unnecessary Java processes first.");
        for (ProcessHandle process : javaProcesses) {
            long pid = process.pid();
            Path game;
            com.sun.tools.attach.VirtualMachine attached = null;
            try {
                attached = com.sun.tools.attach.VirtualMachine.attach(String.valueOf(pid));
                Properties properties = attached.getSystemProperties();
                if (!"true".equals(properties.getProperty("lanminecraft.diagnostics.recipeIds"))) continue;
                game = safe(Path.of(properties.getProperty("user.dir", "")));
                if (game.equals(instances) || !game.startsWith(instances)) continue;
                String arguments = attached.getAgentProperties().getProperty("sun.jvm.args", "");
                if (!arguments.contains("-agentlib:jdwp=") || !arguments.contains("address=127.0.0.1:") || !arguments.contains("server=y") || !arguments.contains("suspend=n")) continue;
            } catch (Exception unavailable) { continue; }
            finally { if (attached != null) try { attached.detach(); } catch (IOException ignored) { } }
            try {
                validate(new Config(pid, pid, game, game.resolve("logs/debug.log"), librarySha, chemistrySha, MAX_EVENTS, steamSha));
                candidates.add(new Candidate(pid, game));
            } catch (Exception incompatible) { /* An unvalidated JVM is never selected. */ }
        }
        return selectOne(candidates);
    }

    static Candidate selectOne(List<Candidate> candidates) {
        if (candidates.isEmpty()) throw new IllegalStateException("Start the updated game through the launcher first, then run this helper again. No matching diagnostic game was found.");
        if (candidates.size() != 1) throw new IllegalStateException("More than one matching game is running. Close the extra game and run this helper again.");
        return candidates.get(0);
    }

    static void observe(Config config, Runnable ready) throws Exception {
        validate(config);
        VirtualMachine vm = null;
        int captured = 0;
        int terminalCaptured = 0;
        int keepAliveCaptured = 0;
        OutputBudget budget = new OutputBudget();
        try {
            AttachingConnector connector = Bootstrap.virtualMachineManager().attachingConnectors().stream()
                .filter(value -> value.name().equals("com.sun.jdi.ProcessAttach")).findFirst()
                .orElseThrow(() -> new IllegalStateException("Full JDK jdk.jdi ProcessAttach connector is required"));
            Map<String, Connector.Argument> arguments = connector.defaultArguments();
            arguments.get("pid").setValue(String.valueOf(config.pid));
            if (arguments.containsKey("timeout")) arguments.get("timeout").setValue("5000");
            vm = connector.attach(arguments);
            EventRequestManager manager = vm.eventRequestManager();
            List<ReferenceType> exceptions = vm.classesByName("java.lang.ArrayIndexOutOfBoundsException");
            if (exceptions.isEmpty()) {
                ClassPrepareRequest prepare = manager.createClassPrepareRequest();
                prepare.addClassFilter("java.lang.ArrayIndexOutOfBoundsException");
                prepare.setSuspendPolicy(EventRequest.SUSPEND_EVENT_THREAD); prepare.enable();
            } else exceptionRequest(manager, exceptions.get(0));
            var hookStates = new ArrayList<Map<String, Object>>();
            var terminalClasses = new LinkedHashSet<String>(); for (Site site : TERMINALS) terminalClasses.add(site.className);
            for (String className : terminalClasses) {
                List<ReferenceType> loaded = vm.classesByName(className);
                if (loaded.isEmpty()) {
                    ClassPrepareRequest prepare = manager.createClassPrepareRequest(); prepare.addClassFilter(className);
                    prepare.setSuspendPolicy(EventRequest.SUSPEND_EVENT_THREAD); prepare.enable();
                    hookStates.add(Map.of("class", className, "state", "waiting_for_class"));
                } else for (ReferenceType type : loaded) hookStates.add(terminalRequests(manager, type));
            }
            append(config, budget, HEADER + json(Map.of("kind", "observer_ready", "utc", Instant.now().toString(),
                "pid", config.pid, "callerFilter", CALLER, "maxEvents", config.maxEvents,
                "targetMethodsInvoked", false, "classMutation", false, "terminalHooks", hookStates, "maxTerminalEvents", config.maxTerminals, "maxKeepAliveEvents", config.maxKeepAlives)) + "\n");
            ready.run();
            while ((captured < config.maxEvents || terminalCaptured < config.maxTerminals || keepAliveCaptured < config.maxKeepAlives) && alive(config.pid) && alive(config.parentPid)) {
                EventSet eventSet;
                try { eventSet = vm.eventQueue().remove(1000); }
                catch (VMDisconnectedException disconnected) { break; }
                if (eventSet == null) continue;
                var snapshots = new ArrayList<Map<String, Object>>();
                boolean disconnected = false;
                try {
                    for (Event event : eventSet) {
                        if (event instanceof ClassPrepareEvent prepared && prepared.referenceType().name().equals("java.lang.ArrayIndexOutOfBoundsException")) {
                            exceptionRequest(manager, prepared.referenceType()); prepared.request().disable();
                        } else if (event instanceof ClassPrepareEvent prepared && terminalClasses.contains(prepared.referenceType().name())) {
                            var state = new LinkedHashMap<String, Object>(terminalRequests(manager, prepared.referenceType()));
                            state.put("kind", "terminal_hooks_ready"); state.put("utc", Instant.now().toString()); state.put("pid", config.pid);
                            snapshots.add(state); prepared.request().disable();
                        } else if (event instanceof BreakpointEvent terminal && terminal.request().getProperty("terminalSite") instanceof Site site && keepAliveSite(site) && keepAliveCaptured < config.maxKeepAlives) {
                            try { snapshots.add(keepAliveSnapshot(terminal, site, config.pid)); keepAliveCaptured++; }
                            catch (Throwable failure) { snapshots.add(Map.of("kind", "keepalive_snapshot_failure", "utc", Instant.now().toString(), "error", failure.getClass().getName())); keepAliveCaptured++; }
                        } else if (event instanceof BreakpointEvent terminal && terminalCaptured < config.maxTerminals && terminal.request().getProperty("terminalSite") instanceof Site site && !keepAliveSite(site)) {
                            try { snapshots.add(terminalSnapshot(terminal, site, config.pid)); terminalCaptured++; }
                            catch (Throwable failure) { snapshots.add(Map.of("kind", "terminal_snapshot_failure", "utc", Instant.now().toString(), "error", failure.getClass().getName())); terminalCaptured++; }
                        } else if (event instanceof ExceptionEvent exception && captured < config.maxEvents && isTarget(exception)) {
                            try { Map<String, Object> capturedSnapshot = snapshot(exception); if (capturedSnapshot != null) { snapshots.add(capturedSnapshot); captured++; } }
                            catch (Throwable failure) { snapshots.add(Map.of("kind", "observer_snapshot_failure", "utc", Instant.now().toString(), "error", failure.getClass().getName())); captured++; }

                        } else if (event instanceof VMDisconnectEvent || event instanceof VMDeathEvent) disconnected = true;
                    }
                } finally {
                    // No file/console I/O occurs until every event in this set has been resumed.
                    try { eventSet.resume(); } catch (VMDisconnectedException ignored) { }
                }
                for (Map<String, Object> snapshot : snapshots) append(config, budget, HEADER + json(snapshot) + "\n");
                for (BreakpointRequest request : manager.breakpointRequests()) if (request.getProperty("terminalSite") instanceof Site site &&
                    ((keepAliveSite(site) && keepAliveCaptured >= config.maxKeepAlives) || (!keepAliveSite(site) && terminalCaptured >= config.maxTerminals))) request.disable();
                if (captured >= config.maxEvents) for (ExceptionRequest request : manager.exceptionRequests()) request.disable();
                if (disconnected) break;
            }
        } finally {
            if (vm != null) {
                try { for (ExceptionRequest request : vm.eventRequestManager().exceptionRequests()) request.disable(); }
                catch (VMDisconnectedException ignored) { }
                try { for (BreakpointRequest request : vm.eventRequestManager().breakpointRequests()) request.disable(); }
                catch (VMDisconnectedException ignored) { }
                try { for (ClassPrepareRequest request : vm.eventRequestManager().classPrepareRequests()) request.disable(); }
                catch (VMDisconnectedException ignored) { }
                try { vm.dispose(); } catch (VMDisconnectedException ignored) { }
            }
        }
    }

    static void exceptionRequest(EventRequestManager manager, ReferenceType type) {
        ExceptionRequest request = manager.createExceptionRequest(type, true, true);
        request.addClassFilter(CALLER); request.setSuspendPolicy(EventRequest.SUSPEND_EVENT_THREAD); request.enable();
    }

    static Map<String, Object> terminalRequests(EventRequestManager manager, ReferenceType type) {
        var methods = new ArrayList<String>();
        for (Site site : TERMINALS) {
            if (!type.name().equals(site.className)) continue;
            List<Method> matching = type.methodsByName(site.methodName, site.signature);
            if (matching.size() != 1) throw new IllegalStateException("Terminal profile mismatch: " + site.className + "." + site.methodName);
            Location entry = matching.get(0).locationOfCodeIndex(0);
            if (entry == null) throw new IllegalStateException("Terminal entry unavailable: " + site.methodName);
            BreakpointRequest request = manager.createBreakpointRequest(entry); request.putProperty("terminalSite", site);
            request.setSuspendPolicy(EventRequest.SUSPEND_EVENT_THREAD); request.enable();
            methods.add(site.methodName + site.signature);
        }
        return Map.of("class", type.name(), "state", "installed", "methods", methods);
    }

    static Map<String, Object> terminalSnapshot(BreakpointEvent event, Site site, long pid) throws Exception {
        var output = new LinkedHashMap<String, Object>(); output.put("kind", "connection_terminal");
        output.put("utc", Instant.now().toString()); output.put("pid", pid); output.put("thread", shortText(event.thread().name(), 120));
        output.put("class", site.className); output.put("method", site.methodName); output.put("signature", site.signature);
        List<StackFrame> frames = event.thread().frames(0, Math.min(36, event.thread().frameCount()));
        StackFrame top = frames.get(0); var arguments = new ArrayList<Object>();
        for (Value value : top.getArgumentValues()) arguments.add(allowedValue(value)); output.put("arguments", arguments);
        ObjectReference receiver = top.thisObject();
        if (receiver != null) output.put("receiverId", receiver.uniqueID());
        if (receiver != null && site.className.equals(STEAM_CLASS)) {
            output.put("bridge", fields(receiver, List.of("hostSide", "connectionId", "started", "closed", "outboundFinQueued", "outboundFinSubmitted", "inboundFinQueued", "inboundFinished", "outboundDataObserved", "inboundDataObserved", "peerReady", "addonNegotiationReady", "preNegotiationBytes", "outboundWait", "gracefulCloseDeadlineMillis", "outboundNotBeforeMillis", "outboundDataFallbackMillis", "dedicatedSessionGeneration")));
            Field diagnosticFlag = receiver.referenceType().fieldByName("NETWORK_DIAGNOSTICS");
            boolean countersEnabled = diagnosticFlag != null && receiver.referenceType().getValue(diagnosticFlag) instanceof BooleanValue value && value.value();
            output.put("bridgeCountersEnabled", countersEnabled);
            if (countersEnabled) output.put("bridgeCounters", fields(receiver, List.of("tcpReadBytes", "steamSentBytes", "steamReceivedBytes", "tcpWrittenBytes", "localQueueRetries")));
            Value runtime = readField(receiver, "runtime");
            if (runtime instanceof ObjectReference object) {
                output.put("runtime", fields(object, List.of("status", "failureCause", "permanentlyShutdown", "activityCount", "retryOutboundNotBeforeMillis", "retryOutboundDeadlineMillis")));
                Value generation = readField(object, "generation");
                if (generation instanceof ObjectReference value) output.put("runtimeGeneration", fields(value, List.of("stopRequested", "id")));
            }
        } else if (receiver != null && site.className.equals("net.minecraft.network.Connection")) {
            output.put("connection", fields(receiver, List.of("f_129471_", "f_290021_", "f_129479_", "f_129473_", "f_129468_")));
            Value listener = readField(receiver, "f_129470_"); output.put("packetListener", allowedValue(listener));
        } else if (receiver != null && site.className.equals("net.minecraft.server.network.ServerGamePacketListenerImpl")) {
            output.put("serverKeepAlive", serverKeepAliveFields(receiver));
        }
        var stack = new ArrayList<Map<String, Object>>();
        for (StackFrame frame : frames) {
            Location location = frame.location();
            stack.add(Map.of("class", shortText(location.declaringType().name(), 220), "method", shortText(location.method().name(), 100), "line", location.lineNumber(), "codeIndex", location.codeIndex()));
            if (location.declaringType().name().equals(STEAM_CLASS) && location.method().signature().equals("()V") &&
                ((location.method().name().equals("readLoop") && location.codeIndex() >= 112 && location.codeIndex() <= 159) ||
                 (location.method().name().equals("writeLoop") && location.codeIndex() >= 123 && location.codeIndex() <= 170))) {
                try {
                    LocalVariable variable = frame.visibleVariableByName("exception");
                    if (variable != null && variable.typeName().equals("java.io.IOException") && frame.getValue(variable) instanceof ObjectReference exception)
                        output.put("localIoException", allowedValue(exception));
                } catch (AbsentInformationException unavailable) { output.put("localIoException", "debug_local_information_unavailable"); }
            }
            if (location.declaringType().name().equals("link.e4steam.steam.SteamRuntime") && location.method().name().equals("drainOutbound") &&
                location.method().signature().equals("(Ljava/nio/ByteBuffer;J)V") && location.codeIndex() == 1248) {
                try {
                    LocalVariable failure = frame.visibleVariableByName("failure"), result = frame.visibleVariableByName("result");
                    if (failure != null && frame.getValue(failure) instanceof ObjectReference value) output.put("nativeSendFailure", allowedValue(value));
                    if (result != null && frame.getValue(result) instanceof IntegerValue value) output.put("nativeSendResult", value.value());
                } catch (AbsentInformationException unavailable) { output.put("nativeSendFailure", "debug_local_information_unavailable"); }
            }
        }
        output.put("stack", stack); output.put("targetMethodsInvoked", false); output.put("classMutation", false); return output;
    }

    static Map<String, Object> keepAliveSnapshot(BreakpointEvent event, Site site, long pid) throws Exception {
        var output = new LinkedHashMap<String, Object>(); output.put("kind", "keepalive"); output.put("utc", Instant.now().toString()); output.put("pid", pid);
        output.put("thread", shortText(event.thread().name(), 120)); output.put("class", site.className); output.put("method", site.methodName);
        StackFrame top = event.thread().frame(0); List<Value> arguments = top.getArgumentValues();
        if (!arguments.isEmpty() && arguments.get(0) instanceof ObjectReference packet) {
            String field = site.methodName.equals("m_7231_") ? "f_132209_" : "f_134092_";
            output.put("packetClass", packet.referenceType().name()); output.put("challengeId", allowedValue(readField(packet, field)));
        }
        ObjectReference receiver = top.thisObject();
        if (receiver != null) output.put("receiverId", receiver.uniqueID());
        if (site.methodName.equals("m_7231_")) {
            output.put("direction", "client_received_request");
            var polling = new LinkedHashMap<String, Object>();
            List<ReferenceType> renderTypes = event.virtualMachine().classesByName("com.mojang.blaze3d.systems.RenderSystem");
            if (renderTypes.size() == 1) for (String name : List.of("pollingEvents", "pollEventsWaitStart")) {
                Field field = renderTypes.get(0).fieldByName(name); polling.put(name, field == null ? null : allowedValue(renderTypes.get(0).getValue(field)));
            }
            output.put("renderSystemPolling", polling);
        } else {
            output.put("direction", "server_received_reply"); if (receiver != null) output.put("serverKeepAlive", serverKeepAliveFields(receiver));
        }
        output.put("targetMethodsInvoked", false); output.put("classMutation", false); return output;
    }

    static Map<String, Object> serverKeepAliveFields(ObjectReference listener) {
        var output = new LinkedHashMap<String, Object>(); output.put("pending", allowedValue(readField(listener, "f_9748_")));
        output.put("lastKeepAliveMillis", allowedValue(readField(listener, "f_9747_"))); output.put("challengeId", allowedValue(readField(listener, "f_9749_")));
        Value player = readField(listener, "f_9743_"); if (player instanceof ObjectReference value) output.put("playerLatencyMillis", allowedValue(readField(value, "f_8943_")));
        Value connection = readField(listener, "f_9742_"); if (connection instanceof ObjectReference value) output.put("connectionReceiverId", value.uniqueID());
        return output;
    }

    static Map<String, Object> fields(ObjectReference object, List<String> names) {
        var result = new LinkedHashMap<String, Object>();
        for (String name : names) result.put(name, allowedValue(readField(object, name))); return result;
    }
    static Object allowedValue(Value value) {
        if (value == null) return null;
        if (value instanceof BooleanValue primitive) return primitive.value();
        if (value instanceof ByteValue primitive) return primitive.value();
        if (value instanceof ShortValue primitive) return primitive.value();
        if (value instanceof IntegerValue primitive) return primitive.value();
        if (value instanceof LongValue primitive) return primitive.value();
        if (value instanceof FloatValue primitive) return Float.isFinite(primitive.value()) ? primitive.value() : "nonfinite";
        if (value instanceof DoubleValue primitive) return Double.isFinite(primitive.value()) ? primitive.value() : "nonfinite";
        if (value instanceof CharValue primitive) return String.valueOf(primitive.value());
        if (value instanceof StringReference string) return shortText(string.value(), 512);
        if (value instanceof ObjectReference object) {
            String className = object.referenceType().name();
            if (className.equals("java.util.concurrent.atomic.AtomicBoolean")) { Value primitive = readField(object, "value"); return primitive instanceof IntegerValue integer ? integer.value() != 0 : null; }
            if (className.equals("java.util.concurrent.atomic.AtomicLong")) return allowedValue(readField(object, "value"));
            if (className.equals("net.minecraft.network.chat.MutableComponent")) {
                var component = new LinkedHashMap<String, Object>(); component.put("class", className);
                Value contents = readField(object, "f_237194_");
                if (contents instanceof ObjectReference content) {
                    String contentClass = content.referenceType().name(); component.put("contentsClass", contentClass);
                    if (contentClass.equals("net.minecraft.network.chat.contents.TranslatableContents")) {
                        component.put("key", stringField(content, "f_237497_")); component.put("fallback", stringField(content, "f_263792_"));
                    } else if (contentClass.equals("net.minecraft.network.chat.contents.LiteralContents")) component.put("text", stringField(content, "f_237368_"));
                }
                return component;
            }
            if (object.referenceType() instanceof ClassType type) {
                for (ClassType current = type; current != null; current = current.superclass()) {
                    if (current.name().equals("java.lang.Throwable")) {
                        var exception = new LinkedHashMap<String, Object>(); exception.put("class", className); exception.put("message", stringField(object, "detailMessage"));
                        Value cause = readField(object, "cause");
                        if (cause instanceof ObjectReference causeObject && causeObject.uniqueID() != object.uniqueID()) {
                            exception.put("causeClass", causeObject.referenceType().name()); exception.put("causeMessage", stringField(causeObject, "detailMessage"));
                        }
                        return exception;
                    }
                    if (current.name().equals("java.lang.Enum")) return Map.of("class", className, "name", Objects.toString(stringField(object, "name"), ""));
                }
            }
            return Map.of("class", shortText(className, 220));
        }
        return value.type().name();
    }

    static boolean isTarget(ExceptionEvent event) {
        return event.exception().referenceType().name().equals("java.lang.ArrayIndexOutOfBoundsException") &&
            event.location().declaringType().name().equals(CALLER) && event.location().method().name().equals("<init>") &&
            event.location().method().signature().startsWith("(Lnet/minecraft/world/item/crafting/Ingredient;");
    }

    static Map<String, Object> snapshot(ExceptionEvent event) throws Exception {
        var output = new LinkedHashMap<String, Object>();
        output.put("kind", "alchemylib_recipe_exception"); output.put("utc", Instant.now().toString());
        output.put("exception", event.exception().referenceType().name());
        output.put("message", stringField(event.exception(), "detailMessage"));
        output.put("caught", event.catchLocation() != null); output.put("thread", shortText(event.thread().name(), 120));
        List<StackFrame> frames = event.thread().frames(0, Math.min(48, event.thread().frameCount()));
        if (frames.stream().noneMatch(frame -> frame.location().declaringType().name().equals(SERIALIZER) && frame.location().method().name().equals("fromNetwork"))) return null;
        var stack = new ArrayList<Map<String, Object>>();
        for (StackFrame frame : frames) {
            Location location = frame.location();
            stack.add(Map.of("class", shortText(location.declaringType().name(), 220), "method", shortText(location.method().name(), 100), "line", location.lineNumber()));
            if (location.declaringType().name().equals(CALLER) && location.method().name().equals("<init>")) {
                List<Value> args = frame.getArgumentValues();
                if (!args.isEmpty() && args.get(0) instanceof ObjectReference ingredient && ingredient.referenceType().allFields().stream().anyMatch(f -> f.name().equals("f_43902_"))) {
                    Value values = readField(ingredient, "f_43902_");
                    output.put("ingredientClass", ingredient.referenceType().name());
                    output.put("ingredientValuesLength", values instanceof ArrayReference array ? array.length() : null);
                    if (args.size() > 1 && args.get(1) instanceof IntegerValue count) output.put("ingredientCount", count.value());
                }
            }
            if (location.declaringType().name().equals(SERIALIZER) && location.method().name().equals("fromNetwork")) {
                List<Value> args = frame.getArgumentValues();
                if (!args.isEmpty() && args.get(0) instanceof ObjectReference id && id.referenceType().name().equals("net.minecraft.resources.ResourceLocation")) {
                    String namespace = stringField(id, "f_135804_"); String path = stringField(id, "f_135805_");
                    output.put("recipeNamespace", namespace); output.put("recipePath", path);
                    output.put("recipeId", namespace == null || path == null ? null : namespace + ":" + path);
                }
                if (args.size() > 1 && args.get(1) instanceof ObjectReference buffer) output.put("bufferPositions", bufferPositions(buffer));
            }
        }
        output.put("stack", stack); output.put("targetMethodsInvoked", false);
        return output;
    }

    static List<Map<String, Object>> bufferPositions(ObjectReference source) {
        var rows = new ArrayList<Map<String, Object>>(); var seen = new HashSet<Long>();
        for (int depth = 0; depth < 5 && source != null && seen.add(source.uniqueID()); depth++) {
            var row = new LinkedHashMap<String, Object>(); row.put("class", shortText(source.referenceType().name(), 180));
            Value reader = readField(source, "readerIndex"), writer = readField(source, "writerIndex");
            if (reader instanceof IntegerValue integer) row.put("readerIndex", integer.value());
            if (writer instanceof IntegerValue integer) row.put("writerIndex", integer.value());
            rows.add(row); ObjectReference next = null;
            for (String field : List.of("f_130049_", "f_130048_", "source", "buf", "buffer")) {
                Value child = readField(source, field); if (child instanceof ObjectReference object && !(child instanceof StringReference)) { next = object; break; }
            }
            source = next;
        }
        return rows;
    }

    static Value readField(ObjectReference object, String name) {
        for (Field field : object.referenceType().allFields()) if (!field.isStatic() && field.name().equals(name)) return object.getValue(field);
        return null;
    }
    static String stringField(ObjectReference object, String field) { Value value = readField(object, field); return value instanceof StringReference text ? shortText(text.value(), 512) : null; }
    static String shortText(String value, int maximum) { return value.length() <= maximum ? value : value.substring(0, maximum); }
    static boolean alive(long pid) { return ProcessHandle.of(pid).map(ProcessHandle::isAlive).orElse(false); }

    static void validate(Config config) throws Exception {
        if (config.pid == ProcessHandle.current().pid() || !alive(config.pid) || !alive(config.parentPid)) throw new SecurityException("Target/parent process is absent or self");
        String targetUser = ProcessHandle.of(config.pid).orElseThrow().info().user().orElseThrow(() -> new SecurityException("Cannot verify target owner"));
        String ownUser = ProcessHandle.current().info().user().orElseThrow(() -> new SecurityException("Cannot verify observer owner"));
        if (!targetUser.equalsIgnoreCase(ownUser)) throw new SecurityException("Different target owner");
        Path game = safe(config.game);
        if (!config.output.toAbsolutePath().normalize().equals(game.resolve("logs/debug.log"))) throw new SecurityException("Output must be the existing game logs/debug.log");
        safe(game.resolve("logs"));
        verifyHash(game.resolve("mods/alchemylib-1.20.1-1.0.30.jar"), config.librarySha);
        verifyHash(game.resolve("mods/alchemistry-1.20.1-2.3.4.jar"), config.chemistrySha);
        try (var entries = Files.list(game.resolve("mods"))) {
            List<Path> steam = entries.filter(path -> path.getFileName().toString().toLowerCase(Locale.ROOT).startsWith("e4steam") && path.toString().endsWith(".jar")).toList();
            if (steam.size() > 1) throw new SecurityException("Ambiguous e4steam JARs");
            if (steam.size() == 1) {
                if (!steam.get(0).getFileName().toString().equals(STEAM_JAR)) throw new SecurityException("Unprofiled e4steam JAR name");
                verifyHash(steam.get(0), config.steamSha);
            }
        }
        com.sun.tools.attach.VirtualMachine local = com.sun.tools.attach.VirtualMachine.attach(String.valueOf(config.pid));
        try {
            Properties properties = local.getSystemProperties();
            if (!safe(Path.of(properties.getProperty("user.dir", ""))).equals(game)) throw new SecurityException("Target user.dir does not equal expected game root");
            String arguments = local.getAgentProperties().getProperty("sun.jvm.args", "");
            if (!arguments.contains("-agentlib:jdwp=") || !arguments.contains("address=127.0.0.1:") || !arguments.contains("server=y") || !arguments.contains("suspend=n"))
                throw new SecurityException("Expected loopback-only non-suspending standard JDWP flag is absent");
        } finally { local.detach(); }
    }

    static Path safe(Path path) throws Exception {
        Path normalized = path.toAbsolutePath().normalize();
        for (Path part = normalized; part != null; part = part.getParent()) {
            BasicFileAttributes attributes = Files.readAttributes(part, BasicFileAttributes.class, LinkOption.NOFOLLOW_LINKS);
            if (attributes.isSymbolicLink() || attributes.isOther()) throw new SecurityException("Reparse/special paths forbidden");
            if (!part.toRealPath().toString().equalsIgnoreCase(part.toString())) throw new SecurityException("Aliased/reparse path forbidden");
        }
        return normalized;
    }
    static void verifyHash(Path path, String expected) throws Exception {
        safe(path); MessageDigest digest = MessageDigest.getInstance("SHA-256");
        try (InputStream input = Files.newInputStream(path)) { byte[] buffer = new byte[131072]; int length; while ((length = input.read(buffer)) != -1) digest.update(buffer, 0, length); }
        if (!HexFormat.of().formatHex(digest.digest()).equals(expected)) throw new SecurityException("Native JAR SHA differs: " + path.getFileName());
    }
    static final class OutputBudget { int emittedBytes; }
    static void append(Config config, OutputBudget budget, String line) throws Exception {
        safe(config.output.getParent()); if (Files.exists(config.output, LinkOption.NOFOLLOW_LINKS)) safe(config.output);
        byte[] bytes = line.getBytes(StandardCharsets.UTF_8);
        if ((long) budget.emittedBytes + bytes.length > MAX_BYTES) throw new IOException("Observer reached256KiB bound");
        Files.write(config.output, bytes, StandardOpenOption.CREATE, StandardOpenOption.APPEND);
        budget.emittedBytes += bytes.length;
    }
    static Map<String, String> options(String[] args) { if (args.length % 2 != 0) throw new IllegalArgumentException("Expected option/value pairs"); var values = new HashMap<String, String>(); for (int i=0;i<args.length;i+=2) if (values.putIfAbsent(args[i],args[i+1])!=null) throw new IllegalArgumentException("Duplicate option"); return values; }
    static String required(Map<String,String> values,String name) { String result=values.get(name); if(result==null||result.isBlank()) throw new IllegalArgumentException("Missing "+name); return result; }
    static String json(Object value) { if(value==null)return"null"; if(value instanceof Number||value instanceof Boolean)return value.toString(); if(value instanceof Map<?,?> map){var result=new StringJoiner(",","{","}");for(var row:map.entrySet())result.add(json(String.valueOf(row.getKey()))+":"+json(row.getValue()));return result.toString();}if(value instanceof Iterable<?> items){var result=new StringJoiner(",","[","]");for(Object item:items)result.add(json(item));return result.toString();}StringBuilder result=new StringBuilder("\"");for(char c:value.toString().toCharArray())switch(c){case'"'->result.append("\\\"");case'\\'->result.append("\\\\");case'\n'->result.append("\\n");case'\r'->result.append("\\r");case'\t'->result.append("\\t");default->{if(c<32)result.append(String.format("\\u%04x",(int)c));else result.append(c);}}return result.append('"').toString();}

    static void selfTest(Path directory, Path java) throws Exception {
        Path root = directory.toAbsolutePath().normalize(); boolean artifact=false; for(Path part:root)artifact|=part.toString().equalsIgnoreCase("artifacts");
        if(!artifact||Files.exists(root))throw new SecurityException("Fresh artifact-only self-test directory required");
        Path minecraft=root.resolve("Minecraft"),game=minecraft.resolve("Personal/Instances/Fixture"),sources=root.resolve("src"),classes=root.resolve("classes");Files.createDirectories(minecraft.resolve("Launcher/JavaRuntimes"));Files.createDirectories(game.resolve("logs"));Files.createDirectories(game.resolve("mods"));Files.createDirectories(classes);
        var files=new LinkedHashMap<String,String>();
        files.put("net/minecraft/resources/ResourceLocation.java","package net.minecraft.resources; public class ResourceLocation { public final String f_135804_,f_135805_; public ResourceLocation(String a,String b){f_135804_=a;f_135805_=b;} }");
        files.put("net/minecraft/world/item/crafting/Ingredient.java","package net.minecraft.world.item.crafting; public class Ingredient { public final Object[] f_43902_; public Ingredient(Object[] a){f_43902_=a;} }");
        files.put("net/minecraft/network/FriendlyByteBuf.java","package net.minecraft.network; public class FriendlyByteBuf { private final Storage f_130049_=new Storage(); public static class Storage { public int readerIndex=9,writerIndex=17; } }");
        files.put("com/smashingmods/alchemylib/api/item/IngredientStack.java","package com.smashingmods.alchemylib.api.item; import net.minecraft.world.item.crafting.Ingredient; public class IngredientStack { public IngredientStack(Ingredient ingredient,int count){ if(count==999)throw new IllegalStateException(\"unrelated\"); Object first=ingredient.f_43902_[0]; } }");
        files.put("com/smashingmods/alchemistry/common/recipe/dissolver/DissolverRecipeSerializer.java","package com.smashingmods.alchemistry.common.recipe.dissolver; import net.minecraft.resources.ResourceLocation; import net.minecraft.network.FriendlyByteBuf; import net.minecraft.world.item.crafting.Ingredient; import com.smashingmods.alchemylib.api.item.IngredientStack; public class DissolverRecipeSerializer { public void fromNetwork(ResourceLocation id,FriendlyByteBuf buf){ new IngredientStack(new Ingredient(new Object[0]),2); } }");
        files.put("ProbeMain.java","import java.nio.file.*; import com.smashingmods.alchemistry.common.recipe.dissolver.DissolverRecipeSerializer; import net.minecraft.resources.ResourceLocation; import net.minecraft.network.FriendlyByteBuf; public class ProbeMain { public static void main(String[] args)throws Exception { Path root=Path.of(args[0]); Class.forName(\"java.lang.ArrayIndexOutOfBoundsException\"); Files.writeString(root.resolve(\"boot.flag\"),\"ok\"); while(!Files.exists(root.resolve(\"start.flag\")))Thread.sleep(10); try {int a=(new int[0])[0];}catch(ArrayIndexOutOfBoundsException expected){} try {new com.smashingmods.alchemylib.api.item.IngredientStack(new net.minecraft.world.item.crafting.Ingredient(new Object[]{\"ok\"}),999);}catch(IllegalStateException expected){} try {new com.smashingmods.alchemylib.api.item.IngredientStack(new net.minecraft.world.item.crafting.Ingredient(new Object[0]),2);}catch(ArrayIndexOutOfBoundsException expected){} try {new DissolverRecipeSerializer().fromNetwork(new ResourceLocation(\"qa\",\"caught_recipe\"),new FriendlyByteBuf());}catch(ArrayIndexOutOfBoundsException expected){} Thread worker=new Thread(()->new DissolverRecipeSerializer().fromNetwork(new ResourceLocation(\"qa\",\"uncaught_recipe\"),new FriendlyByteBuf()),\"uncaught-selftest\");worker.start();worker.join(); Files.writeString(root.resolve(\"continued.flag\"),\"continued\");while(!Files.exists(root.resolve(\"stop.flag\")))Thread.sleep(10); } }");
        files.put("io/netty/channel/ChannelHandlerContext.java", "package io.netty.channel; public interface ChannelHandlerContext {} ");
        files.put("net/minecraft/network/chat/Component.java", "package net.minecraft.network.chat; public interface Component {} ");
        files.put("net/minecraft/network/chat/ComponentContents.java", "package net.minecraft.network.chat; public interface ComponentContents {} ");
        files.put("net/minecraft/network/chat/MutableComponent.java", "package net.minecraft.network.chat; public class MutableComponent implements Component { private final ComponentContents f_237194_; public MutableComponent(ComponentContents contents){f_237194_=contents;} }");
        files.put("net/minecraft/network/chat/contents/TranslatableContents.java", "package net.minecraft.network.chat.contents; public class TranslatableContents implements net.minecraft.network.chat.ComponentContents { private final String f_237497_; private final String f_263792_=null; public TranslatableContents(String key){f_237497_=key;} }");
        files.put("net/minecraft/network/protocol/game/ClientboundKeepAlivePacket.java", "package net.minecraft.network.protocol.game; public class ClientboundKeepAlivePacket { private final long f_132209_; public ClientboundKeepAlivePacket(long id){f_132209_=id;} }");
        files.put("net/minecraft/network/protocol/game/ServerboundKeepAlivePacket.java", "package net.minecraft.network.protocol.game; public class ServerboundKeepAlivePacket { private final long f_134092_; public ServerboundKeepAlivePacket(long id){f_134092_=id;} }");
        files.put("com/mojang/blaze3d/systems/RenderSystem.java", "package com.mojang.blaze3d.systems; public class RenderSystem { private static final java.util.concurrent.atomic.AtomicBoolean pollingEvents=new java.util.concurrent.atomic.AtomicBoolean(false); private static final java.util.concurrent.atomic.AtomicLong pollEventsWaitStart=new java.util.concurrent.atomic.AtomicLong(12345); public static void load(){} }");
        files.put("net/minecraft/client/multiplayer/ClientPacketListener.java", "package net.minecraft.client.multiplayer; public class ClientPacketListener { public boolean continued; public void m_7231_(net.minecraft.network.protocol.game.ClientboundKeepAlivePacket packet){continued=true;} }");
        files.put("net/minecraft/server/level/ServerPlayer.java", "package net.minecraft.server.level; public class ServerPlayer { public int f_8943_=12; }");
        files.put("net/minecraft/server/network/ServerGamePacketListenerImpl.java", "package net.minecraft.server.network; public class ServerGamePacketListenerImpl { private boolean f_9748_=true; private long f_9747_=112233,f_9749_=704815; public boolean continued; public void m_5683_(net.minecraft.network.protocol.game.ServerboundKeepAlivePacket packet){f_9748_=false;continued=true;} public void m_9942_(net.minecraft.network.chat.Component reason){continued=true;} public void tick(){f_9748_=true;f_9747_=998877;m_9942_(new net.minecraft.network.chat.MutableComponent(new net.minecraft.network.chat.contents.TranslatableContents(\"disconnect.timeout\")));} }");
        files.put("net/minecraft/server/network/ServerGamePacketListenerImpl.java", files.get("net/minecraft/server/network/ServerGamePacketListenerImpl.java").replace("private boolean f_9748_=true;", "private net.minecraft.server.level.ServerPlayer f_9743_=new net.minecraft.server.level.ServerPlayer(); private boolean f_9748_=true;"));
        files.put("ProbeKeepAlive.java", "public class ProbeKeepAlive { public static void run(){com.mojang.blaze3d.systems.RenderSystem.load();net.minecraft.client.multiplayer.ClientPacketListener client=new net.minecraft.client.multiplayer.ClientPacketListener();client.m_7231_(new net.minecraft.network.protocol.game.ClientboundKeepAlivePacket(704815));if(!client.continued)throw new AssertionError();net.minecraft.server.network.ServerGamePacketListenerImpl server=new net.minecraft.server.network.ServerGamePacketListenerImpl();server.m_5683_(new net.minecraft.network.protocol.game.ServerboundKeepAlivePacket(704815));if(!server.continued)throw new AssertionError();server.tick();} }");
        files.put("net/minecraft/network/Connection.java", "package net.minecraft.network; public class Connection { private Object f_129470_=new Listener(); private Object f_129471_,f_290021_,f_129468_; private boolean f_129479_,f_129473_; public static class Listener {} public void channelInactive(io.netty.channel.ChannelHandlerContext c){} public void exceptionCaught(io.netty.channel.ChannelHandlerContext c,Throwable t){f_129479_=true;} public void m_129507_(net.minecraft.network.chat.Component c){f_129471_=c;} }");
        files.put("link/e4steam/steam/SteamRuntime.java", "package link.e4steam.steam; public class SteamRuntime { public enum State { RUNNING } private State status=State.RUNNING; private Throwable failureCause; private boolean permanentlyShutdown; private int activityCount=1; }");
        files.put("link/e4steam/steam/SteamConnectionBridge.java", "package link.e4steam.steam; import java.util.concurrent.atomic.*; public class SteamConnectionBridge { public static final boolean NETWORK_DIAGNOSTICS=true; private final SteamRuntime runtime=new SteamRuntime(); private final int connectionId; private final boolean hostSide; private final AtomicBoolean started=new AtomicBoolean(true),closed=new AtomicBoolean(),outboundFinQueued=new AtomicBoolean(),peerReady=new AtomicBoolean(true); private final AtomicLong tcpReadBytes=new AtomicLong(41); private String outboundWait=\"selftest\"; private int mode; public SteamConnectionBridge(int id,boolean host){connectionId=id;hostSide=host;} public void localEof(){mode=0;readLoop();} public void localIo(){mode=1;readLoop();} private void readLoop(){if(mode==0){beginGracefulClose();return;}try{throw new java.io.IOException(\"qa_bridge_local_io\");}catch(java.io.IOException exception){close(false);}} public void acceptRemoteFin(){beginGracefulClose();} private void beginGracefulClose(){outboundFinQueued.set(true);} public void close(boolean reset){closed.set(true);} }");
        files.put("ProbeClose.java", "public class ProbeClose { public static void run(){new link.e4steam.steam.SteamConnectionBridge(7,true).localEof();new link.e4steam.steam.SteamConnectionBridge(8,true).localIo();new link.e4steam.steam.SteamConnectionBridge(9,false).acceptRemoteFin();net.minecraft.network.Connection connection=new net.minecraft.network.Connection();connection.exceptionCaught(null,new java.io.IOException(\"qa_native_local_io\"));connection.m_129507_(new net.minecraft.network.chat.MutableComponent(new net.minecraft.network.chat.contents.TranslatableContents(\"disconnect.timeout\")));new net.minecraft.network.Connection().channelInactive(null);} }");
        files.put("ProbeMain.java", files.get("ProbeMain.java").replace("Files.writeString(root.resolve(\"continued.flag\"),\"continued\");", "ProbeClose.run(); ProbeKeepAlive.run(); Files.writeString(root.resolve(\"continued.flag\"),\"continued\");"));
        var compilerArgs=new ArrayList<String>(List.of("--release","17","-g","-d",classes.toString()));
        for(var row:files.entrySet()){Path file=sources.resolve(row.getKey());Files.createDirectories(file.getParent());Files.writeString(file,row.getValue());compilerArgs.add(file.toString());}
        int compiled=ToolProvider.getSystemJavaCompiler().run(null,null,null,compilerArgs.toArray(String[]::new));if(compiled!=0)throw new IllegalStateException("Self-test compilation failed");
        for(String name:List.of("alchemylib-1.20.1-1.0.30.jar","alchemistry-1.20.1-2.3.4.jar",STEAM_JAR)){try(JarOutputStream zip=new JarOutputStream(Files.newOutputStream(game.resolve("mods").resolve(name)))){zip.putNextEntry(new JarEntry("selftest.marker"));zip.write(name.getBytes(StandardCharsets.UTF_8));zip.closeEntry();}}
        String lib=HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(Files.readAllBytes(game.resolve("mods/alchemylib-1.20.1-1.0.30.jar"))));
        String chem=HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(Files.readAllBytes(game.resolve("mods/alchemistry-1.20.1-2.3.4.jar"))));
        String steam=HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(Files.readAllBytes(game.resolve("mods").resolve(STEAM_JAR))));
        Path childTemp = root.resolve("separate-game-temp"); Files.createDirectories(childTemp);
        if (childTemp.equals(Path.of(System.getProperty("java.io.tmpdir")).toAbsolutePath().normalize())) throw new AssertionError("Self-test temp directories must differ");
        ProcessBuilder childBuilder=new ProcessBuilder(java.toAbsolutePath().toString(),"-Djava.io.tmpdir="+childTemp,"-Dlanminecraft.diagnostics.recipeIds=true","-agentlib:jdwp=transport=dt_socket,address=127.0.0.1:0,server=y,suspend=n","-cp",classes.toString(),"ProbeMain",root.toString()).directory(game.toFile()).redirectOutput(root.resolve("debuggee.out.log").toFile()).redirectError(root.resolve("debuggee.err.log").toFile());
        childBuilder.environment().put("TEMP",childTemp.toString()); childBuilder.environment().put("TMP",childTemp.toString());
        Process child=childBuilder.start();
        byte[] existingLog = new byte[300 * 1024]; Arrays.fill(existingLog, (byte)'P'); Files.write(game.resolve("logs/debug.log"), existingLog);
        CompletableFuture<Void> observing=new CompletableFuture<>();
        try {
            waitFor(root.resolve("boot.flag"),child,10000);
            Candidate selected = discover(minecraft, lib, chem, steam);
            if (selected.pid != child.pid() || !selected.game.equals(game)) throw new AssertionError("Discovery selected wrong game");
            try { selectOne(List.of()); throw new AssertionError("Empty selection accepted"); } catch (IllegalStateException expected) { }
            try { selectOne(List.of(selected, selected)); throw new AssertionError("Ambiguous selection accepted"); } catch (IllegalStateException expected) { }
            Thread observer=new Thread(()->{try{observe(new Config(child.pid(),child.pid(),game,game.resolve("logs/debug.log"),lib,chem,2,steam,7,2),()->{try{Files.writeString(root.resolve("start.flag"),"start");}catch(Exception failure){throw new RuntimeException(failure);}});observing.complete(null);}catch(Throwable failure){observing.completeExceptionally(failure);}},"self-test-observer");observer.start();
            observing.get(20,TimeUnit.SECONDS);waitFor(root.resolve("continued.flag"),child,5000);
            String captured=Files.readString(game.resolve("logs/debug.log"));
            byte[] resultingLog=Files.readAllBytes(game.resolve("logs/debug.log")); if(!Arrays.equals(existingLog,Arrays.copyOf(resultingLog,existingLog.length)))throw new AssertionError("Existing log prefix changed");
            if(!captured.contains("qa:caught_recipe")||!captured.contains("qa:uncaught_recipe")||!captured.contains("\"ingredientValuesLength\":0")||!captured.contains("\"caught\":false")||!captured.contains("\"caught\":true")||captured.contains("IllegalStateException")||!captured.contains("\"readerIndex\":9")||!captured.contains("\"writerIndex\":17")||!Files.exists(root.resolve("continued.flag")))throw new AssertionError("Observer capture/filter/resume self-test failed");
            if (captured.split("\"kind\":\"connection_terminal\"", -1).length - 1 != 7 || !captured.contains("qa_native_local_io") ||
                !captured.contains("acceptRemoteFin") || !captured.contains("readLoop") || !captured.contains("\"tcpReadBytes\":41") ||
                !captured.contains("\"packetListener\":{\"class\":\"net.minecraft.network.Connection$Listener\"}") ||
                !captured.contains("terminal_hooks_ready") || !captured.contains("\"key\":\"disconnect.timeout\"") || captured.contains("terminal_snapshot_failure")) throw new AssertionError("Terminal origin/filter/fields self-test failed");
            if (captured.lines().noneMatch(line -> line.contains("\"method\":\"channelInactive\"") && line.contains("\"f_129471_\":null"))) throw new AssertionError("Bare channel-close null reason not captured");
            if (captured.split("\"kind\":\"keepalive\"", -1).length - 1 != 2 || captured.split("\"challengeId\":704815", -1).length - 1 < 3 ||
                !captured.contains("\"pollingEvents\":false") || !captured.contains("\"pollEventsWaitStart\":12345") ||
                !captured.contains("\"playerLatencyMillis\":12") ||
                captured.lines().noneMatch(line -> line.contains("\"method\":\"m_9942_\"") && line.contains("\"method\":\"tick\"") && line.contains("\"lastKeepAliveMillis\":998877")) ||
                captured.contains("keepalive_snapshot_failure")) throw new AssertionError("Keepalive matching/state/original-disconnect self-test failed");
            Files.writeString(root.resolve("stop.flag"),"stop");if(!child.waitFor(5,TimeUnit.SECONDS)||child.exitValue()!=0)throw new AssertionError("Self-test debuggee did not continue and exit normally");
            Files.writeString(root.resolve("result.json"),json(Map.of("status","PASS","capturedEvents",2,"exactRecipeIds",List.of("qa:caught_recipe","qa:uncaught_recipe"),"emptyArrayCaptured",true,"unrelatedErrorsExcluded",true,"eventThreadsResumed",true,"debuggeeExitCode",child.exitValue(),"logSizes",Map.of("totalBytes",Files.size(game.resolve("logs/debug.log")),"preexistingBytesPreserved",existingLog.length,"newBytes",resultingLog.length-existingLog.length),"targetMethodsInvoked",false,"classMutation",false))+"\n");
            System.out.println("SELF_TEST_PASS "+root.resolve("result.json"));
        } finally {
            Files.writeString(root.resolve("stop.flag"),"stop");
            if(child.isAlive()&&!child.waitFor(5,TimeUnit.SECONDS))child.destroy();
        }
    }
    static void waitFor(Path marker,Process process,long millis)throws Exception{long deadline=System.nanoTime()+TimeUnit.MILLISECONDS.toNanos(millis);while(!Files.exists(marker)&&process.isAlive()&&System.nanoTime()<deadline)Thread.sleep(10);if(!Files.exists(marker))throw new IllegalStateException("Self-test marker absent: "+marker.getFileName());}
}
