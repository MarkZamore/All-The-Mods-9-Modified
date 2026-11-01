import java.io.*;
import java.lang.reflect.*;
import java.net.*;
import java.nio.file.*;
import java.util.*;
import java.util.zip.*;
import org.objectweb.asm.*;
import org.objectweb.asm.tree.*;

/** Executes the generated methods and checks every other gameplay method structurally. */
public final class VerifyPatch {
    static ClassNode read(byte[] bytes) { ClassNode n = new ClassNode(); new ClassReader(bytes).accept(n, 0); return n; }
    static String shape(MethodNode method) {
        StringBuilder out = new StringBuilder();
        for (AbstractInsnNode i : method.instructions) {
            if (i.getOpcode() < 0) continue;
            out.append(i.getOpcode()).append(':');
            if (i instanceof MethodInsnNode n) out.append(n.owner).append(n.name).append(n.desc).append(n.itf);
            else if (i instanceof FieldInsnNode n) out.append(n.owner).append(n.name).append(n.desc);
            else if (i instanceof TypeInsnNode n) out.append(n.desc);
            else if (i instanceof VarInsnNode n) out.append(n.var);
            else if (i instanceof IntInsnNode n) out.append(n.operand);
            else if (i instanceof LdcInsnNode n) out.append(n.cst instanceof String ? "TEXT" : n.cst);
            else if (i instanceof InvokeDynamicInsnNode n) {
                out.append(n.name).append(n.desc).append(n.bsm);
                for (Object a : n.bsmArgs) out.append(a instanceof String ? "TEXT" : a);
            } else if (i instanceof IincInsnNode n) out.append(n.var).append('/').append(n.incr);
            else if (i instanceof TableSwitchInsnNode n) out.append(n.min).append('/').append(n.max).append('/').append(n.labels.size());
            else if (i instanceof LookupSwitchInsnNode n) out.append(n.keys);
            else if (i instanceof MultiANewArrayInsnNode n) out.append(n.desc).append(n.dims);
            out.append(';');
        }
        return out.toString();
    }
    static Class<?> fixture(MethodNode original, String name) {
        ClassNode node = new ClassNode(); node.version = Opcodes.V17; node.access = Opcodes.ACC_PUBLIC; node.name = name; node.superName = "java/lang/Object";
        original.access = Opcodes.ACC_PUBLIC | Opcodes.ACC_STATIC;
        node.methods.add(original); ClassWriter writer = new ClassWriter(0); node.accept(writer);
        return new ClassLoader() { Class<?> define() { return defineClass(name, writer.toByteArray(), 0, writer.toByteArray().length); } }.define();
    }
    static void require(boolean condition, String message) { if (!condition) throw new AssertionError(message); }
    public static void main(String[] args) throws Exception {
        int invariant = 0, textClasses = 0; Set<String> executableAdded = new TreeSet<>();
        try (ZipFile before = new ZipFile(args[0]); ZipFile after = new ZipFile(args[1])) {
            Set<String> a = new TreeSet<>(), b = new TreeSet<>();
            for (ZipEntry e : Collections.list(before.entries())) if (e.getName().endsWith(".class")) a.add(e.getName());
            for (ZipEntry e : Collections.list(after.entries())) if (e.getName().endsWith(".class")) b.add(e.getName());
            require(a.equals(b), "Executable class set changed");
            for (String path : a) {
                byte[] x = before.getInputStream(before.getEntry(path)).readAllBytes(), y = after.getInputStream(after.getEntry(path)).readAllBytes();
                if (Arrays.equals(x, y)) continue;
                ++textClasses; ClassNode old = read(x), now = read(y);
                require(old.name.equals(now.name) && old.superName.equals(now.superName) && old.interfaces.equals(now.interfaces), "Class identity changed");
                require(old.fields.size() == now.fields.size(), "Native fields changed");
                for (int i = 0; i < old.fields.size(); ++i) require(old.fields.get(i).name.equals(now.fields.get(i).name) && old.fields.get(i).desc.equals(now.fields.get(i).desc), "Field identity changed");
                for (MethodNode method : old.methods) {
                    MethodNode current = now.methods.stream().filter(m -> m.name.equals(method.name) && m.desc.equals(method.desc)).findFirst().orElseThrow();
                    boolean speech = old.name.equals("varmite/verity/client/audio/TTSHandler") && method.name.equals("lambda$initLocalSTT$0");
                    boolean gate = old.name.equals("varmite/verity/event/ModEvents") && method.name.equals("onPlayerChat");
                    if (!speech && !gate) { require(shape(method).equals(shape(current)), "Gameplay instructions changed: " + path + ":" + method.name); ++invariant; }
                }
                for (MethodNode method : now.methods) if (old.methods.stream().noneMatch(m -> m.name.equals(method.name) && m.desc.equals(method.desc))) {
                    require(method.name.equals("toString") || method.name.equals("matchesRequiredName"), "Unexpected added method");
                    executableAdded.add(now.name + "." + method.name);
                }
                if (now.name.equals("varmite/verity/event/ModEvents")) {
                    MethodNode gate = now.methods.stream().filter(m -> m.name.equals("matchesRequiredName")).findFirst().orElseThrow();
                    Method f = fixture(gate, "VerityGateFixture").getMethod("matchesRequiredName", String.class, CharSequence.class);
                    for (String[] row : new String[][]{{"верити помоги", "verity", "true"}, {"verity help", "верити", "true"}, {"hello bob", "bob", "true"}, {"верити", "bob", "false"}, {"help", "verity", "false"}})
                        require(f.invoke(null, row[0], row[1]).equals(Boolean.valueOf(row[2])), "Required-name positive/negative case failed");
                }
                if (now.name.equals("varmite/verity/client/audio/TTSHandler")) {
                    MethodNode normalize = now.methods.stream().filter(m -> m.name.equals("sanitizeTranscript")).findFirst().orElseThrow();
                    Method f = fixture(normalize, "VeritySpeechNameFixture").getMethod("sanitizeTranscript", String.class);
                    require(f.invoke(null, "Верити, найди руду").equals("Verity, найди руду"), "Russian name not normalized");
                    require(f.invoke(null, "верите, найди руду").equals("Verity, найди руду"), "Russian speech variant not normalized");
                    require(f.invoke(null, "обычная речь").equals("обычная речь"), "Unrelated Russian words changed");
                    require(f.invoke(null, "Verdi, help").equals("Verity, help"), "Original Latin alias changed");
                }
            }
        }
        try (URLClassLoader loader = new URLClassLoader(new URL[]{Path.of(args[1]).toUri().toURL()}, ClassLoader.getPlatformClassLoader())) {
            for (String simple : List.of("TTSLanguage", "TTSProvider", "STTProvider", "AiModelPreset")) {
                Class<?> type = loader.loadClass("varmite.verity.types." + simple);
                for (Object value : type.getEnumConstants()) {
                    String name = ((Enum<?>)value).name();
                    require(type.getMethod("valueOf", String.class).invoke(null, name) == value, "Enum name/valueOf identity changed");
                    require(!value.toString().isBlank(), "Empty enum label");
                }
            }
            Object english = loader.loadClass("varmite.verity.types.TTSLanguage").getMethod("valueOf", String.class).invoke(null, "English");
            require(english.toString().equals("Английский"), "Russian language display missing");
        }
        System.out.println("PASS invariant gameplay methods=" + invariant + "; changed original classes=" + textClasses + "; added display/name methods=" + executableAdded.size() + "; new executable classes=0; positive/negative name and enum identity checks passed");
    }
}
