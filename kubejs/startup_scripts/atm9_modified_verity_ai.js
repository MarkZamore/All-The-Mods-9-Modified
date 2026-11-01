// Pack-owned Verity AI policy; evaluated before Forge COMMON config loading.
// Run at startup script evaluation, before Forge COMMON CONFIG_LOAD.
// Launcher cwd is the instance game directory; all mod-specific policy is here.
;(function () {
const context = JsonIO.read('launcher-runtime/launch-context.json')
if (context === null || Number(context.schemaVersion) !== 1 || context.values === undefined) {
  throw new Error('Missing runtime context')
}
const endpoint = String(context.values['localAi.endpoint'])
if (!/^http:\/\/127\.0\.0\.1:[1-9][0-9]{0,4}$/.test(endpoint)) {
  throw new Error('Invalid local Ollama binding')
}
const port = Number(endpoint.substring(endpoint.lastIndexOf(':') + 1))
if (port > 65535) throw new Error('Invalid local Ollama port')
const CommentedFileConfig = Java.loadClass('com.electronwill.nightconfig.core.file.CommentedFileConfig')
const config = CommentedFileConfig['builder(java.lang.String)']('config/verity-common.toml').sync().preserveInsertionOrder().build()
try {
  config.load()
  config['set(java.lang.String,java.lang.Object)']('AISettings.aiProvider', 'OLLAMA')
  config['set(java.lang.String,java.lang.Object)']('AISettings.aiModel', 'qwen3:1.7b')
  config['set(java.lang.String,java.lang.Object)']('AISettings.aiThink', false)
  config['set(java.lang.String,java.lang.Object)']('AISettings.aiEndpoint', endpoint)
  config.save()
} finally {
  config.close()
}
})()
