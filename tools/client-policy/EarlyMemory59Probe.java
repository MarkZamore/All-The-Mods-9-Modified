import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.memorysettings.Memory;
import com.memorysettings.config.CommonConfiguration;
import net.minecraftforge.fml.loading.FMLPaths;

import java.nio.file.Files;
import java.nio.file.Path;

public final class EarlyMemory59Probe {
    public static void main(String[] args) throws Exception {
        Path fixture = Path.of(args[0]).toRealPath();
        Path source = Path.of(args[1]).toRealPath();
        Path config = fixture.resolve("config/memorysettings.json");
        if (!Files.isRegularFile(config) || Files.exists(fixture.resolve("mods"))) {
            throw new IllegalArgumentException("Use a disposable fixture containing only the prepared config");
        }
        FMLPaths.loadAbsolutePaths(fixture);
        CommonConfiguration loaded = CommonConfiguration.config.getCommonConfig();
        JsonObject nativeOriginal = JsonParser.parseString(Files.readString(source)).getAsJsonObject();
        if (!nativeOriginal.has("earlyWarningMinimumMemory")) {
            nativeOriginal.add("earlyWarningMinimumMemory",
                    new CommonConfiguration().serialize().get("earlyWarningMinimumMemory"));
        }
        CommonConfiguration originalSettings = new CommonConfiguration();
        originalSettings.deserialize(nativeOriginal);
        nativeOriginal.getAsJsonObject("minimumClient").addProperty("minimumClient", 0);
        CommonConfiguration expectedSettings = new CommonConfiguration();
        expectedSettings.deserialize(nativeOriginal);
        if (originalSettings.minimumClient != 8192 || !expectedSettings.serialize().equals(loaded.serialize())
                || loaded.minimumClient != 0 || loaded.disableWarnings) {
            throw new AssertionError("Exact native loader did not keep all other settings");
        }
        Memory.recordMemory();
        if (Memory.heapSetting >= 8192 - 150 || Memory.heapSetting <= 0) {
            throw new AssertionError("Use an intentionally low JVM heap in the disposable fixture");
        }
        Memory.doEarlyWarnings();
        System.out.printf("PASS native Memory Settings 5.9 returned at %d MiB without the early advisory%n",
                Memory.heapSetting);
        String model = System.getProperty("sun.arch.data.model");
        int originalSystemMemory = Memory.systemMemory;
        try {
            System.setProperty("sun.arch.data.model", "32");
            Memory.systemMemory = 8192;
            try {
                Memory.doEarlyWarnings();
                throw new AssertionError("The 32-bit Java dialog path did not run");
            } catch (NoClassDefFoundError expected) {
                if (!"org/lwjgl/util/tinyfd/TinyFileDialogs".equals(expected.getMessage())) throw expected;
                System.out.println("PASS native 32-bit Java warning reaches the dialog provider");
            }
        } finally {
            System.setProperty("sun.arch.data.model", model);
            Memory.systemMemory = originalSystemMemory;
        }
    }
}
