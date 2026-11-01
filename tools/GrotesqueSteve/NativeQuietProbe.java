import java.lang.reflect.*;
import java.nio.file.*;
import java.util.*;
import java.util.zip.*;
import com.google.gson.*;
import com.mojang.brigadier.CommandDispatcher;
import com.mojang.brigadier.arguments.StringArgumentType;
import com.mojang.brigadier.builder.LiteralArgumentBuilder;
import com.mojang.brigadier.builder.RequiredArgumentBuilder;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.CommandFunction;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.packs.metadata.pack.PackMetadataSectionSerializer;

/** Standalone real native parser/VM checks; never launches Minecraft. */
public final class NativeQuietProbe {
  public static void main(String[] args) throws Exception {
    String mode=args[0];
    if (mode.equals("callbacks")) {
      Class<?> event=Class.forName("net.minecraftforge.event.entity.player.PlayerEvent$PlayerLoggedInEvent",false,NativeQuietProbe.class.getClassLoader());
      for (String name: List.of("GrotesqueMessageProcedure","AdvancementtriggerProcedure")) {
        Class<?> type=Class.forName("net.mde.grotesquesteve.procedures."+name);
        Method callback=type.getDeclaredMethod("onPlayerLoggedIn",event);
        try {
          callback.invoke(null,new Object[]{null});
          if (!args[1].equals("quiet")) throw new AssertionError("Author handler unexpectedly inert");
          System.out.println("QUIET_CALLBACK_RETURNED "+name);
        } catch (InvocationTargetException ex) {
          if (!args[1].equals("author") || !(ex.getCause() instanceof NullPointerException)) throw ex;
          System.out.println("AUTHOR_NULL_EVENT_DEREFERENCE "+name);
        }
      }
      return;
    }
    try (ZipFile zip=new ZipFile(args[1])) {
      JsonObject doc=JsonParser.parseString(new String(zip.getInputStream(zip.getEntry("pack.mcmeta")).readAllBytes(),java.nio.charset.StandardCharsets.UTF_8)).getAsJsonObject();
      int format=new PackMetadataSectionSerializer().m_6322_(doc.getAsJsonObject("pack")).m_10374_();
      if (format!=15) throw new AssertionError("Wrong native pack format");
      System.out.println("NATIVE_PACK_METADATA_FORMAT "+format);
      CommandDispatcher<CommandSourceStack> dispatcher=new CommandDispatcher<>();
      dispatcher.register(LiteralArgumentBuilder.<CommandSourceStack>literal("give").then(RequiredArgumentBuilder.<CommandSourceStack,String>argument("arguments",StringArgumentType.greedyString()).executes(c->1)));
      String line=new String(zip.getInputStream(zip.getEntry("data/minecraft/functions/manualgiver.mcfunction")).readAllBytes(),java.nio.charset.StandardCharsets.UTF_8);
      try {
        CommandFunction function=CommandFunction.m_77984_(new ResourceLocation("minecraft:manualgiver"),dispatcher,null,List.of(line));
        if (!mode.equals("quiet") || function.m_77989_().length!=1) throw new AssertionError("Unexpected function parse");
        System.out.println("NATIVE_FUNCTION_LINE_ACCEPTED "+line);
      } catch (IllegalArgumentException ex) {
        if (!mode.equals("author") || !ex.getMessage().contains("Do not use a preceding forwards slash")) throw ex;
        System.out.println("NATIVE_AUTHOR_LEADING_SLASH_REJECTED");
      }
    }
  }
}
