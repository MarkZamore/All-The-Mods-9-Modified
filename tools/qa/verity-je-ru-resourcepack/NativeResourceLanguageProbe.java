import com.google.gson.*;
import java.io.*;
import java.nio.file.*;
import java.security.MessageDigest;
import java.util.*;
import java.util.zip.*;
import net.minecraft.client.resources.language.ClientLanguage;
import net.minecraft.locale.Language;
import net.minecraft.server.packs.*;
import net.minecraft.server.packs.metadata.pack.PackMetadataSection;
import net.minecraft.server.packs.resources.*;

/** Exact native resource/pack-metadata/language serialization only. No Minecraft client/window. */
public final class NativeResourceLanguageProbe {
  static Map<String,String> language(Path zip, String name) throws Exception {
    var result=new TreeMap<String,String>();
    try(var archive=new ZipFile(zip.toFile());var in=archive.getInputStream(archive.getEntry(name))) {
      Language.m_128108_(in,result::put);
    }
    return result;
  }
  static String sha(Path path) throws Exception {
    try(var in=Files.newInputStream(path)) {
      return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(in.readAllBytes()));
    }
  }
  public static void main(String[] args) throws Exception {
    Path jar=Path.of(args[0]),pack=Path.of(args[1]);
    var ownRu=language(jar,"assets/verity/lang/ru_ru.json");
    var ownEn=language(jar,"assets/verity/lang/en_us.json");
    var external=language(pack,"assets/verity/lang/ru_ru.json");
    for(var entry:external.entrySet()) String.format(Locale.ROOT,entry.getValue());
    var author=new FilePackResources("approved_verity_ru_jar",jar.toFile(),false);
    var addition=new FilePackResources("Verity-JE-RU.zip",pack.toFile(),false);
    var metadata=addition.m_5550_(PackMetadataSection.f_243696_);
    if(metadata==null || metadata.m_10374_()!=15)throw new AssertionError("Native pack metadata format mismatch");
    int retained=0;
    try(var resources=new MultiPackResourceManager(PackType.CLIENT_RESOURCES,List.of(author,addition))) {
      var russian=ClientLanguage.m_264420_(resources,List.of("en_us","ru_ru"),false);
      var english=ClientLanguage.m_264420_(resources,List.of("en_us"),false);
      for(var entry:external.entrySet())
        if(!russian.m_118919_(entry.getKey(),"__missing__").equals(entry.getValue()))
          throw new AssertionError("Native overlay value mismatch: "+entry.getKey());
      for(var entry:ownRu.entrySet()) if(!external.containsKey(entry.getKey())) {
        if(!russian.m_118919_(entry.getKey(),"__missing__").equals(entry.getValue()))
          throw new AssertionError("Approved RU fallback lost: "+entry.getKey());
        retained++;
      }
      for(var entry:ownEn.entrySet())
        if(!english.m_118919_(entry.getKey(),"__missing__").equals(entry.getValue()))
          throw new AssertionError("External RU resource modified selected English: "+entry.getKey());
    }
    var report=new LinkedHashMap<String,Object>();
    report.put("status","NATIVE_RESOURCE_METADATA_AND_LANGUAGE_PASS");
    report.put("minecraftVersion","1.20.1");report.put("packFormat",metadata.m_10374_());
    report.put("packSha256",sha(pack));report.put("approvedJarSha256",sha(jar));
    report.put("externalRussianKeys",external.size());report.put("approvedRussianKeys",ownRu.size());
    report.put("retainedApprovedKeysNotInExternal",retained);
    report.put("externalLayerValuesMatched",true);report.put("selectedEnglishUnaffected",true);
    report.put("nativeStringFormatCasesPassed",external.size());
    report.put("actualKubeJsInjectionOrFullClientVerified",false);
    report.put("gameClientWindowOrMinecraftMainStarted",false);
    report.put("limits","Actual native FilePackResources/PackMetadataSection serializer/MultiPackResourceManager/ClientLanguage. Pack order here matches inspected KubeJS insertion before personal packs; actual Mixin lifecycle and rendered pixels are unrun.");
    var json=new GsonBuilder().disableHtmlEscaping().setPrettyPrinting().create().toJson(report)+"\n";
    Files.writeString(Path.of(args[2]),json);System.out.print(json);
  }
}
