var startupCallbacks=[],loginCallbacks=[],warnings=[];
var model={saveRoot:'saves/Combined',mapRoot:'journeymap/data/sp/Combined',singleplayer:true};
var rootResource={};
var mcModel={
  hasSingleplayerServer:function(){return model.singleplayer;},
  getSingleplayerServer:function(){return {getWorldPath:function(resource){
    if(resource!==rootResource)throw new Error('Wrong world resource');
    return NativeBridge.getFileFromPath(model.saveRoot).toPath();
  }};}
};
var MinecraftModel={getInstance:function(){return mcModel;}};
var ResourceModel={ROOT:rootResource};
var MapModel={getJMWorldDir:function(mc){if(mc!==mcModel)throw new Error('Wrong Minecraft model');return NativeBridge.getFileFromPath(model.mapRoot);}};
var Java={loadClass:function(name){
  if(name==='dev.latvian.mods.kubejs.util.UtilsJS')return NativeBridge;
  if(name==='org.apache.commons.io.FileUtils')return FileUtilsType;
  if(name==='java.util.UUID')return UuidType;
  if(name==='net.minecraft.client.Minecraft')return MinecraftModel;
  if(name==='net.minecraft.world.level.storage.LevelResource')return ResourceModel;
  if(name==='journeymap.client.io.FileHandler')return MapModel;
  throw new Error('Unexpected class '+name);
}};
var Platform={isClientEnvironment:function(){return true;},isLoaded:function(name){return name==='journeymap';}};
var StartupEvents={postInit:function(f){startupCallbacks.push(f);}};
var ForgeEvents={onEvent:function(name,f){if(name!=='net.minecraftforge.client.event.ClientPlayerNetworkEvent$LoggingIn')throw new Error('Unexpected event '+name);loginCallbacks.push(f);}};
var console={warn:function(text){warnings.push(String(text));}};
var global={};
NativeBridge.writeTest(model.saveRoot+'/level.dat','SYNTHETIC-SAME-SEED-42');
NativeBridge.writeTest(model.mapRoot+'/waypoints/legitA.json','{"payload":"A"}');
NativeBridge.writeTest(model.mapRoot+'/DIM0/region.png','IMAGE');
