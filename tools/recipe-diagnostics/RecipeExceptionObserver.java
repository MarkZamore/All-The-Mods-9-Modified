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
    static final String HEADER = "[RecipeExceptionObserver v5] ";
    static final int MAX_BYTES = 256 * 1024;
    static final int MAX_EVENTS = 8;
    record Config(long pid, long parentPid, Path game, Path output, String librarySha, String chemistrySha, int maxEvents) { }
    record Candidate(long pid, Path game) { }

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
                validate(new Config(pid, pid, game, game.resolve("logs/debug.log"), librarySha, chemistrySha, MAX_EVENTS));
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
            append(config, budget, HEADER + json(Map.of("kind", "observer_ready", "utc", Instant.now().toString(),
                "pid", config.pid, "callerFilter", CALLER, "maxEvents", config.maxEvents,
                "targetMethodsInvoked", false, "classMutation", false)) + "\n");
            ready.run();
            while (captured < config.maxEvents && alive(config.pid) && alive(config.parentPid)) {
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
                if (disconnected) break;
            }
        } finally {
            if (vm != null) {
                try { for (ExceptionRequest request : vm.eventRequestManager().exceptionRequests()) request.disable(); }
                catch (VMDisconnectedException ignored) { }
                try { vm.dispose(); } catch (VMDisconnectedException ignored) { }
            }
        }
    }

    static void exceptionRequest(EventRequestManager manager, ReferenceType type) {
        ExceptionRequest request = manager.createExceptionRequest(type, true, true);
        request.addClassFilter(CALLER); request.setSuspendPolicy(EventRequest.SUSPEND_EVENT_THREAD); request.enable();
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
        var compilerArgs=new ArrayList<String>(List.of("--release","17","-g","-d",classes.toString()));
        for(var row:files.entrySet()){Path file=sources.resolve(row.getKey());Files.createDirectories(file.getParent());Files.writeString(file,row.getValue());compilerArgs.add(file.toString());}
        int compiled=ToolProvider.getSystemJavaCompiler().run(null,null,null,compilerArgs.toArray(String[]::new));if(compiled!=0)throw new IllegalStateException("Self-test compilation failed");
        for(String name:List.of("alchemylib-1.20.1-1.0.30.jar","alchemistry-1.20.1-2.3.4.jar")){try(JarOutputStream zip=new JarOutputStream(Files.newOutputStream(game.resolve("mods").resolve(name)))){zip.putNextEntry(new JarEntry("selftest.marker"));zip.write(name.getBytes(StandardCharsets.UTF_8));zip.closeEntry();}}
        String lib=HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(Files.readAllBytes(game.resolve("mods/alchemylib-1.20.1-1.0.30.jar"))));
        String chem=HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(Files.readAllBytes(game.resolve("mods/alchemistry-1.20.1-2.3.4.jar"))));
        Path childTemp = root.resolve("separate-game-temp"); Files.createDirectories(childTemp);
        if (childTemp.equals(Path.of(System.getProperty("java.io.tmpdir")).toAbsolutePath().normalize())) throw new AssertionError("Self-test temp directories must differ");
        ProcessBuilder childBuilder=new ProcessBuilder(java.toAbsolutePath().toString(),"-Djava.io.tmpdir="+childTemp,"-Dlanminecraft.diagnostics.recipeIds=true","-agentlib:jdwp=transport=dt_socket,address=127.0.0.1:0,server=y,suspend=n","-cp",classes.toString(),"ProbeMain",root.toString()).directory(game.toFile()).redirectOutput(root.resolve("debuggee.out.log").toFile()).redirectError(root.resolve("debuggee.err.log").toFile());
        childBuilder.environment().put("TEMP",childTemp.toString()); childBuilder.environment().put("TMP",childTemp.toString());
        Process child=childBuilder.start();
        byte[] existingLog = new byte[300 * 1024]; Arrays.fill(existingLog, (byte)'P'); Files.write(game.resolve("logs/debug.log"), existingLog);
        CompletableFuture<Void> observing=new CompletableFuture<>();
        try {
            waitFor(root.resolve("boot.flag"),child,10000);
            Candidate selected = discover(minecraft, lib, chem);
            if (selected.pid != child.pid() || !selected.game.equals(game)) throw new AssertionError("Discovery selected wrong game");
            try { selectOne(List.of()); throw new AssertionError("Empty selection accepted"); } catch (IllegalStateException expected) { }
            try { selectOne(List.of(selected, selected)); throw new AssertionError("Ambiguous selection accepted"); } catch (IllegalStateException expected) { }
            Thread observer=new Thread(()->{try{observe(new Config(child.pid(),child.pid(),game,game.resolve("logs/debug.log"),lib,chem,2),()->{try{Files.writeString(root.resolve("start.flag"),"start");}catch(Exception failure){throw new RuntimeException(failure);}});observing.complete(null);}catch(Throwable failure){observing.completeExceptionally(failure);}},"self-test-observer");observer.start();
            observing.get(20,TimeUnit.SECONDS);waitFor(root.resolve("continued.flag"),child,5000);
            String captured=Files.readString(game.resolve("logs/debug.log"));
            byte[] resultingLog=Files.readAllBytes(game.resolve("logs/debug.log")); if(!Arrays.equals(existingLog,Arrays.copyOf(resultingLog,existingLog.length)))throw new AssertionError("Existing log prefix changed");
            if(!captured.contains("qa:caught_recipe")||!captured.contains("qa:uncaught_recipe")||!captured.contains("\"ingredientValuesLength\":0")||!captured.contains("\"caught\":false")||!captured.contains("\"caught\":true")||captured.contains("IllegalStateException")||!captured.contains("\"readerIndex\":9")||!captured.contains("\"writerIndex\":17")||!Files.exists(root.resolve("continued.flag")))throw new AssertionError("Observer capture/filter/resume self-test failed");
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
