// Verity 6.0.0 references two discs which its author never registered.
// Remove only those raw entries before Forge resolves tags; keep all valid discs.
ServerEvents.tags('item', event => {
  event.remove('minecraft:music_discs', 'verity:verity_disc')
  event.remove('minecraft:music_discs', 'verity:verity_edit_disc')
})
