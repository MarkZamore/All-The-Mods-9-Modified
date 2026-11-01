// ATM9 Modified compatibility setting, applied after Forge loads COMMON configs.
// Keep the rest of Verity's personal AI and voice settings untouched.
StartupEvents.postInit(event => {
  const VerityConfig = Java.loadClass('varmite.verity.VerityConfig')
  VerityConfig.KILL_ENTITIES.set(false)
})
