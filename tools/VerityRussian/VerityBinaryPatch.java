import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;
import java.util.zip.*;
import org.objectweb.asm.*;
import org.objectweb.asm.tree.*;

/** Offline author-JAR editor; never packaged or loaded by Minecraft. */
public final class VerityBinaryPatch {
    static final Base64.Encoder B64 = Base64.getEncoder();
    static final Base64.Decoder FROM64 = Base64.getDecoder();
    record Key(String owner, String method, String descriptor, String kind, String original) { }
    record Site(Key key, int ordinal) { }
    static final Map<Key,String> replacements = new LinkedHashMap<>();
    static final Map<Site,String> exactReplacements = new LinkedHashMap<>();
    static final Set<Site> exactApplied = new HashSet<>();
    static final Map<Key,Integer> seen = new HashMap<>();
    static final Map<Key,Integer> applied = new LinkedHashMap<>();
    static PrintWriter inventory;
    static boolean editing;

    static String b64(String text) { return B64.encodeToString(text.getBytes(StandardCharsets.UTF_8)); }
    static String un64(String text) { return new String(FROM64.decode(text), StandardCharsets.UTF_8); }
    static String text(String owner, String method, String descriptor, String kind, String value) {
        Key key = new Key(owner, method, descriptor, kind, value);
        int ordinal = seen.merge(key, 1, Integer::sum) - 1;
        Site site = new Site(key, ordinal);
        if (inventory != null) inventory.println(String.join("\t", b64(owner), b64(method), b64(descriptor), b64(kind), b64(value), Integer.toString(ordinal)));
        String replacement = exactReplacements.get(site);
        if (replacement != null) exactApplied.add(site);
        else replacement = replacements.get(key);
        if (replacement == null) return value;
        applied.merge(key, 1, Integer::sum);
        return replacement;
    }

    static void annotation(String owner, String method, String descriptor, AnnotationNode annotation) {
        if (annotation.values == null) return;
        for (int i = 1; i < annotation.values.size(); i += 2)
            annotation.values.set(i, annotationValue(owner, method, descriptor, annotation.values.get(i)));
    }
    @SuppressWarnings({"unchecked", "rawtypes"})
    static Object annotationValue(String owner, String method, String descriptor, Object value) {
        if (value instanceof String s) return text(owner, method, descriptor, "annotation", s);
        if (value instanceof AnnotationNode node) annotation(owner, method, descriptor, node);
        if (value instanceof List list) for (int i = 0; i < list.size(); ++i)
            list.set(i, annotationValue(owner, method, descriptor, list.get(i)));
        return value;
    }
    static void annotations(String owner, String method, String descriptor, List<AnnotationNode> list) {
        if (list != null) for (AnnotationNode node : list) annotation(owner, method, descriptor, node);
    }

    static byte[] process(byte[] bytes) {
        int before = applied.values().stream().mapToInt(Integer::intValue).sum();
        boolean nativeChanged = false;
        ClassNode node = new ClassNode();
        new ClassReader(bytes).accept(node, 0);
        if (!node.name.startsWith("varmite/verity/")) return bytes;
        annotations(node.name, "", "", node.visibleAnnotations);
        annotations(node.name, "", "", node.invisibleAnnotations);
        for (FieldNode field : node.fields) {
            if (field.value instanceof String s) field.value = text(node.name, field.name, field.desc, "field", s);
            annotations(node.name, field.name, field.desc, field.visibleAnnotations);
            annotations(node.name, field.name, field.desc, field.invisibleAnnotations);
        }
        for (MethodNode method : node.methods) {
            annotations(node.name, method.name, method.desc, method.visibleAnnotations);
            annotations(node.name, method.name, method.desc, method.invisibleAnnotations);
            if (method.visibleParameterAnnotations != null) for (List<AnnotationNode> list : method.visibleParameterAnnotations)
                annotations(node.name, method.name, method.desc, list);
            if (method.invisibleParameterAnnotations != null) for (List<AnnotationNode> list : method.invisibleParameterAnnotations)
                annotations(node.name, method.name, method.desc, list);
            for (AbstractInsnNode insn : method.instructions.toArray()) {
                if (insn instanceof LdcInsnNode ldc && ldc.cst instanceof String s)
                    ldc.cst = text(node.name, method.name, method.desc, "ldc", s);
                if (insn instanceof InvokeDynamicInsnNode indy && indy.bsm.getOwner().equals("java/lang/invoke/StringConcatFactory")) {
                    for (int i = 0; i < indy.bsmArgs.length; ++i)
                        if (indy.bsmArgs[i] instanceof String s) indy.bsmArgs[i] = text(node.name, method.name, method.desc, "concat", s);
                }
            }
            if (editing && node.name.equals("varmite/verity/client/audio/TTSHandler") && method.name.equals("lambda$initLocalSTT$0")) {
                int injected = 0;
                for (AbstractInsnNode insn : method.instructions.toArray()) {
                    if (insn instanceof MethodInsnNode call && call.owner.equals("com/k2fsa/sherpa/onnx/OfflineWhisperModelConfig$Builder") && call.name.equals("build")) {
                        InsnList settings = new InsnList();
                        settings.add(new LdcInsnNode("ru"));
                        settings.add(new MethodInsnNode(Opcodes.INVOKEVIRTUAL, call.owner, "setLanguage", "(Ljava/lang/String;)Lcom/k2fsa/sherpa/onnx/OfflineWhisperModelConfig$Builder;", false));
                        settings.add(new LdcInsnNode("transcribe"));
                        settings.add(new MethodInsnNode(Opcodes.INVOKEVIRTUAL, call.owner, "setTask", "(Ljava/lang/String;)Lcom/k2fsa/sherpa/onnx/OfflineWhisperModelConfig$Builder;", false));
                        method.instructions.insertBefore(call, settings);
                        ++injected;
                    }
                }
                if (injected != 1) throw new IllegalStateException("Expected one exact native Whisper builder, found " + injected);
                method.maxStack += 2;
                nativeChanged = true;
            }
            if (editing && node.name.equals("varmite/verity/event/ModEvents") && method.name.equals("onPlayerChat")) {
                int changed = 0;
                for (AbstractInsnNode insn : method.instructions.toArray()) {
                    if (insn instanceof MethodInsnNode call && call.owner.equals("java/lang/String") && call.name.equals("contains") && call.desc.equals("(Ljava/lang/CharSequence;)Z")) {
                        method.instructions.set(call, new MethodInsnNode(Opcodes.INVOKESTATIC, node.name, "matchesRequiredName", "(Ljava/lang/String;Ljava/lang/CharSequence;)Z", false));
                        ++changed;
                    }
                }
                if (changed != 1) throw new IllegalStateException("Expected one exact native required-name gate");
                nativeChanged = true;
            }
        }
        if (editing) {
            if (node.name.equals("varmite/verity/event/ModEvents")) {
                if (node.methods.stream().anyMatch(m -> m.name.equals("matchesRequiredName"))) throw new IllegalStateException("Name alias method already exists");
                MethodNode alias = new MethodNode(Opcodes.ACC_PRIVATE | Opcodes.ACC_STATIC, "matchesRequiredName", "(Ljava/lang/String;Ljava/lang/CharSequence;)Z", null, null);
                Label other = new Label(), russian = new Label(), reject = new Label();
                alias.visitCode(); alias.visitVarInsn(Opcodes.ALOAD, 0); alias.visitVarInsn(Opcodes.ALOAD, 1);
                alias.visitMethodInsn(Opcodes.INVOKEVIRTUAL, "java/lang/String", "contains", "(Ljava/lang/CharSequence;)Z", false);
                alias.visitJumpInsn(Opcodes.IFEQ, other); alias.visitInsn(Opcodes.ICONST_1); alias.visitInsn(Opcodes.IRETURN);
                alias.visitLabel(other); alias.visitFrame(Opcodes.F_SAME, 0, null, 0, null);
                alias.visitVarInsn(Opcodes.ALOAD, 1); alias.visitLdcInsn("verity");
                alias.visitMethodInsn(Opcodes.INVOKEVIRTUAL, "java/lang/Object", "equals", "(Ljava/lang/Object;)Z", false);
                alias.visitJumpInsn(Opcodes.IFEQ, russian); alias.visitVarInsn(Opcodes.ALOAD, 0); alias.visitLdcInsn("верити");
                alias.visitMethodInsn(Opcodes.INVOKEVIRTUAL, "java/lang/String", "contains", "(Ljava/lang/CharSequence;)Z", false); alias.visitInsn(Opcodes.IRETURN);
                alias.visitLabel(russian); alias.visitFrame(Opcodes.F_SAME, 0, null, 0, null);
                alias.visitVarInsn(Opcodes.ALOAD, 1); alias.visitLdcInsn("верити");
                alias.visitMethodInsn(Opcodes.INVOKEVIRTUAL, "java/lang/Object", "equals", "(Ljava/lang/Object;)Z", false);
                alias.visitJumpInsn(Opcodes.IFEQ, reject); alias.visitVarInsn(Opcodes.ALOAD, 0); alias.visitLdcInsn("verity");
                alias.visitMethodInsn(Opcodes.INVOKEVIRTUAL, "java/lang/String", "contains", "(Ljava/lang/CharSequence;)Z", false); alias.visitInsn(Opcodes.IRETURN);
                alias.visitLabel(reject); alias.visitFrame(Opcodes.F_SAME, 0, null, 0, null); alias.visitInsn(Opcodes.ICONST_0); alias.visitInsn(Opcodes.IRETURN);
                alias.visitMaxs(2, 2); alias.visitEnd(); node.methods.add(alias); nativeChanged = true;
            }
            Map<String,String> labels = switch (node.name) {
                case "varmite/verity/types/TTSLanguage" -> Map.of("English", "Английский", "German", "Немецкий");
                case "varmite/verity/types/AiModelPreset" -> Map.of("SMART", "Умная", "FAST", "Быстрая");
                case "varmite/verity/types/TTSProvider" -> Map.of("NATIVE", "Системный голос", "LOCAL", "Локальный голос");
                case "varmite/verity/types/STTProvider" -> Map.of("NATIVE", "Локальное распознавание", "WHISPER", "Сервер Whisper");
                default -> null;
            };
            if (labels != null) {
                // YACL's verified default formatter uses Enum.toString, while config serialization
                // uses Enum.name/valueOf. Only presentation is changed; enum identity is intact.
                if (node.methods.stream().anyMatch(m -> m.name.equals("toString") && m.desc.equals("()Ljava/lang/String;")))
                    throw new IllegalStateException("Unexpected author enum display override");
                List<String> values = node.fields.stream().filter(f -> (f.access & Opcodes.ACC_ENUM) != 0).map(f -> f.name).toList();
                if (!values.containsAll(labels.keySet())) throw new IllegalStateException("Author enum choices changed");
                MethodNode display = new MethodNode(Opcodes.ACC_PUBLIC, "toString", "()Ljava/lang/String;", null, null);
                display.visitCode(); display.visitVarInsn(Opcodes.ALOAD, 0);
                display.visitMethodInsn(Opcodes.INVOKEVIRTUAL, "java/lang/Enum", "ordinal", "()I", false);
                Label fallback = new Label(); Label[] branches = new Label[values.size()];
                for (int i = 0; i < branches.length; ++i) branches[i] = new Label();
                display.visitTableSwitchInsn(0, branches.length - 1, fallback, branches);
                for (int i = 0; i < branches.length; ++i) {
                    display.visitLabel(branches[i]); display.visitFrame(Opcodes.F_SAME, 0, null, 0, null);
                    display.visitLdcInsn(labels.getOrDefault(values.get(i), values.get(i))); display.visitInsn(Opcodes.ARETURN);
                }
                display.visitLabel(fallback); display.visitFrame(Opcodes.F_SAME, 0, null, 0, null);
                display.visitVarInsn(Opcodes.ALOAD, 0); display.visitMethodInsn(Opcodes.INVOKEVIRTUAL, "java/lang/Enum", "name", "()Ljava/lang/String;", false);
                display.visitInsn(Opcodes.ARETURN); display.visitMaxs(1, 1); display.visitEnd();
                node.methods.add(display); nativeChanged = true;
            }
        }
        if (!editing || (!nativeChanged && before == applied.values().stream().mapToInt(Integer::intValue).sum())) return bytes;
        ClassWriter writer = new ClassWriter(0);
        node.accept(writer);
        return writer.toByteArray();
    }

    public static void main(String[] args) throws Exception {
        if (args.length != 3 && args.length != 4) throw new IllegalArgumentException("inventory <jar> <tsv> | patch <jar> <class-output-dir> <map.tsv>");
        editing = args[0].equals("patch");
        if (editing) {
            for (String line : Files.readAllLines(Path.of(args[3]), StandardCharsets.UTF_8)) {
                if (line.isBlank()) continue;
                String[] columns = line.split("\t", -1);
                if (columns.length != 6 && columns.length != 7) throw new IllegalArgumentException("Invalid map row");
                Key key = new Key(un64(columns[0]), un64(columns[1]), un64(columns[2]), un64(columns[3]), un64(columns[4]));
                if (columns.length == 7) {
                    if (exactReplacements.put(new Site(key, Integer.parseInt(columns[6])), un64(columns[5])) != null)
                        throw new IllegalArgumentException("Duplicate exact translation site");
                } else if (replacements.put(key, un64(columns[5])) != null) throw new IllegalArgumentException("Duplicate translation key");
            }
        } else inventory = new PrintWriter(Files.newBufferedWriter(Path.of(args[2]), StandardCharsets.UTF_8));
        try (ZipFile zip = new ZipFile(args[1])) {
            for (ZipEntry entry : Collections.list(zip.entries())) {
                if (!entry.getName().startsWith("varmite/verity/") || !entry.getName().endsWith(".class")) continue;
                byte[] input = zip.getInputStream(entry).readAllBytes();
                byte[] output = process(input);
                if (editing && !Arrays.equals(input, output)) {
                    Path target = Path.of(args[2]).resolve(entry.getName());
                    Files.createDirectories(target.getParent()); Files.write(target, output);
                }
            }
        } finally { if (inventory != null) inventory.close(); }
        if (editing) {
            for (Key key : replacements.keySet()) if (!applied.containsKey(key))
                throw new IllegalStateException("Translation did not match exact author site: " + key);
            for (Site site : exactReplacements.keySet()) if (!exactApplied.contains(site))
                throw new IllegalStateException("Translation did not match exact ordinal: " + site);
            System.out.println("Applied translation keys: " + applied.size() + "; sites: " + applied.values().stream().mapToInt(Integer::intValue).sum());
        }
    }
}
