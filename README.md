# All the Mods 9 Modified

Отдельная чистая производная от оригинальной **ATM9 1.1.1**, **Minecraft 1.20.1**, **Forge 47.4.0**. ID: `all-the-mods-9-modified`; папка установки: `All the Mods 9 Modified`. Оригинальная ATM9 остаётся самостоятельным профилем. Для Modified подготовлены [собственный источник](https://github.com/MarkZamore/All-The-Mods-9-Modified) и профиль поставки `pack-latest`; прежние наработки Modified не служат входом для этой сборки.

**Текущий состав прошёл полный клиентский прогон, новый мир, настоящий русский AI-диалог и штатный выход.** Lock `214b22b429d73f9b68b88c32021253cde056d10e137199a373b92b810e2fcf09` включает десять согласованных исключений, официальный AllTheLeaks1.1.4 и Grotesque Steve1.4.2-quiet.1. [Текущий runtime-отчёт](tools/qa/final-runtime-post-removals-420.md) фиксирует 902 ERROR/0 FATAL с раздельной классификацией, а не отсутствие ошибок. QA13 и A/B ниже исторические. Исторический Box crash не объявляется исправленным; у Blood Magic и позднего Placebo новый инициатор не установлен. Этот source-native отчёт не устанавливает результат миграции или публичной поставки: они проверяются отдельно до добавления карточки. Границы проверок — в [TESTING-STATUS.md](TESTING-STATUS.md), актуальная публикация — в [workflow](https://github.com/MarkZamore/All-The-Mods-9-Modified/actions/workflows/publish.yml) и [pack-latest](https://github.com/MarkZamore/All-The-Mods-9-Modified/releases/tag/pack-latest).

## Состав и граница исходной ATM9

В исходнике **531 JAR: 431 BASE по членству +81 запрошенное дополнение +19 NEW dependencies**, 100 NEW JAR и 16 support-файлов. Точный [active lock](tools/modified-lock.json): `214b22b429d73f9b68b88c32021253cde056d10e137199a373b92b810e2fcf09`. Из BASE 430 сохраняют прежние байты, один заменён официальным авторским файлом. Во всей поставке 529 авторских JAR и два согласованных NEW derivatives. Native ModList текущей ревизии содержит 559 записей вместе с платформой и общим Steam, из них 556 pack ID. Прежние 566/569 ID от QA13 остаются историческими.

Из 431 BASE-мода **430 JAR сохраняют исходные SHA256**, а AllTheLeaks по прямому разрешению пользователя обновлён официальным авторским файлом 1.0.7 →1.1.4. Исходный Iron’s Spells 3.4.0.11 и Cupboard 2.7 не обновляются ради аддонов. Снимок 1 794 авторских payload-файлов и 452 исходных pack ID остаётся в [экспорте 7097953](https://www.curseforge.com/minecraft/modpacks/all-the-mods-9/files/7097953), `tools/upstream-lock.json` и `tools/base-mod-ids.json`; effective поставка раскрывает отдельную BASE JAR замену и текстовые overlays.

Эту ревизию нельзя описывать как «только добавленные моды» или обещать побайтную неизменность всех 1 794 файлов. По отдельному запросу локализованы 107 BASE-текстовых ресурсов квестов: их SHA/размеры закреплены в quest `baseReplacements`. Отдельный `baseJarOverrides` разрешает только точный официальный AllTheLeaks1.1.4 и не расширяет locale-guard на JAR. ID, задачи, награды и зависимости квестов не заменяются этим переводом.

В 531 JAR **529 совпадают с соответствующими авторскими файлами**, включая новый официальный AllTheLeaks. Два NEW JAR — явно разрешённые производные: замороженный русский Verity6.0.0-ru.1 и Grotesque Steve1.4.2-quiet.1. Последний меняет только два login callbacks и синтаксис одной функции, как раскрыто ниже. Отдельно описан общий производный e4steam лаунчера. Собственные Forge-моды, Safety-framework и прежние helper JAR не добавляются; runtime LAN/UUID/skin-адаптация раскрыта отдельно.

Карточка сохраняет исходные краткое описание, описание и обложку ATM9. Раздел **«Дополнительные моды»** показывает только 81 выбранное ручное дополнение; BASE, автоматические зависимости и встроенные библиотеки не выдаются за ручные добавления. Реальные 556 загруженных pack ID закреплены текущим native ModList и проверены по 531 source JAR; инфраструктура E4 учитывается отдельно.

### Ручные дополнения (81)

Ниже данные текущего active lock: официальная страница, версия из метаданных JAR и объявленные mod ID. Версия внутри JAR может отличаться от имени файла или заголовка релиза. Точные имена, file ID, размеры и SHA256 остаются в lock.

| Проект и официальная страница | Версия из JAR | Mod ID |
| --- | --- | --- |
| [Alex's Mobs](https://www.curseforge.com/minecraft/mc-mods/alexs-mobs) | `1.22.9` | `alexsmobs` |
| [Alone in the Dark](https://www.curseforge.com/minecraft/mc-mods/alone-in-the-dark) | `1.3.0` | `alone_in_the_dark` |
| [AmbientSounds](https://www.curseforge.com/minecraft/mc-mods/ambientsounds) | `6.3.11` | `ambientsounds` |
| [AmbiHorror](https://www.curseforge.com/minecraft/mc-mods/ambi-horror-ambience) | `1.0.0` | `ambihorror` |
| [Anomaly Rephased](https://www.curseforge.com/minecraft/mc-mods/the-anomaly) | `2.0.032` | `anomaly_rephased` |
| [Antlers](https://www.curseforge.com/minecraft/mc-mods/antlers-the-wendigo) | `1.0.0` | `antlers` |
| [Apex Arcana](https://www.curseforge.com/minecraft/mc-mods/apex-arcana-irons-spells-n-spellbooks-addon) | `1.4.0` | `grandsigil` |
| [Apollyon](https://www.curseforge.com/minecraft/mc-mods/apollyon) | `1.1.1` | `apollyon` |
| [Arthropod Phobia Expansions](https://www.curseforge.com/minecraft/mc-mods/arphex) | `5.0.2` | `arphex` |
| [Biomancy 2](https://www.curseforge.com/minecraft/mc-mods/biomancy) | `2.8.19.0` | `biomancy` |
| [Black Sun](https://www.curseforge.com/minecraft/mc-mods/black-sun) | `1.1.0` | `blacksun` |
| [Boiled One Reimagined](https://www.curseforge.com/minecraft/mc-mods/the-boiled-one-reimagined) | `1.0.12` | `boiled_reimagined` |
| [Burnt Basic](https://www.curseforge.com/minecraft/mc-mods/burnt-basic) | `1.10.5.3` | `burnt` |
| [Capybara's Liminal Spaces](https://www.curseforge.com/minecraft/mc-mods/capybaras-liminal-spaces) | `1.4.1` | `capybaras_liminal_spaces` |
| [Cave Dweller Evolved](https://www.curseforge.com/minecraft/mc-mods/cave-dweller-evolved) | `1.7.0` | `cave_dweller` |
| [Celestisynth](https://www.curseforge.com/minecraft/mc-mods/celestisynth) | `1.20.1-1.3.4` | `celestisynth` |
| [Cracker's Wither Storm Mod](https://www.curseforge.com/minecraft/mc-mods/crackers-wither-storm-mod) | `4.2.1` | `witherstormmod` |
| [Creepy Horror Sounds](https://www.curseforge.com/minecraft/mc-mods/creepy-horror-sounds) | `1.2` | `creepymod` |
| [Cult of Azazel](https://www.curseforge.com/minecraft/mc-mods/cult-of-azazel) | `1.1.4.12` | `netherman` |
| [Cursed Fate](https://www.curseforge.com/minecraft/mc-mods/cursed-fate) | `1.0.0` | `cursedfate` |
| [Dandadan](https://www.curseforge.com/minecraft/mc-mods/dandadan) | `2.0` | `dandadan` |
| [Deep Dark: Regrowth](https://www.curseforge.com/minecraft/mc-mods/deep-dark-regrowth) | `1.2.6.1` | `deep_dark_regrowth` |
| [Distant Friends](https://www.curseforge.com/minecraft/mc-mods/distant-friends) | `0.5.6` | `distantfriends` |
| [Doomsday Arsenal](https://www.curseforge.com/minecraft/mc-mods/doomsday-arsenal) | `1.0.0` | `doomsday` |
| [Door Knocker (Horror)](https://www.curseforge.com/minecraft/mc-mods/door-knocker-horror) | `1.3` | `door_knocker` |
| [Echoes of Nowhere](https://modrinth.com/mod/echoes-of-nowhere) | `1.0.1` | `echoes_of_nowhere` |
| [Enhanced Celestials](https://www.curseforge.com/minecraft/mc-mods/enhanced-celestials) | `5.0.0.4` | `enhancedcelestials` |
| [Eyes in the Darkness](https://www.curseforge.com/minecraft/mc-mods/eyes-in-the-darkness) | `1.3.10` | `eyesinthedarkness` |
| [Fairy Mine](https://www.curseforge.com/minecraft/mc-mods/fairy-mine) | `2.6.5` | `fairy_mine` |
| [From Another World](https://www.curseforge.com/minecraft/mc-mods/from-another-world) | `1.2A.1-forge` | `fromanotherworld` |
| [God Wand](https://www.curseforge.com/minecraft/mc-mods/god-wand) | `1.2.0` | `godwand` |
| [Grotesque Steve](https://saskez.gumroad.com/l/stevegrotesque) | `1.4.2-quiet.1` | `grotesque_steve` |
| [Horror Element Mod](https://www.curseforge.com/minecraft/mc-mods/horror-elements-mod) | `1.6.3` | `horror_element_mod` |
| [HSR Phainon](https://www.curseforge.com/minecraft/mc-mods/hsr-phainon) | `1.2.3` | `hsrphainon` |
| [Jujutsu Craft](https://www.curseforge.com/minecraft/mc-mods/sorceryfight) | `51` | `jujutsucraft` |
| [Liminality](https://www.curseforge.com/minecraft/mc-mods/liminal-reality) | `1.0.0` | `liminality` |
| [Meulti's Backrooms](https://www.curseforge.com/minecraft/mc-mods/meultis-backrooms) | `1.4.0` | `mbackrooms` |
| [Mine Mine no Mi](https://www.curseforge.com/minecraft/mc-mods/mine-mine-no-mi) | `0.11.6` | `mineminenomi` |
| [Nostalgia](https://www.curseforge.com/minecraft/mc-mods/nostalgia-liminal-spaces) | `1.2.0` | `nostalgia` |
| [Nyctophobia](https://www.curseforge.com/minecraft/mc-mods/nyctophobia-forge) | `2.0.0+mc1.20.1` | `nyctophobia` |
| [Nyf's Spiders](https://www.curseforge.com/minecraft/mc-mods/nyfs-spiders) | `3.0.2` | `nyfsspiders` |
| [Orbital Railgun Forge](https://www.curseforge.com/minecraft/mc-mods/orbital-railgun-reforged) | `1.4.2` | `orbital_railgun` |
| [Playmate](https://www.curseforge.com/minecraft/mc-mods/playmate) | `1.0.0` | `knock_knock` |
| [Presence Footsteps (Forge)](https://www.curseforge.com/minecraft/mc-mods/presence-footsteps-forge) | `1.20.1-1.9.1-beta.1` | `presencefootsteps` |
| [Rats](https://www.curseforge.com/minecraft/mc-mods/rats) | `1.20.1-8.1.3` | `rats` |
| [ReMorphed](https://www.curseforge.com/minecraft/mc-mods/remorphed) | `4.2` | `remorphed` |
| [Retail 3008](https://www.curseforge.com/minecraft/mc-mods/retail-3008) | `1.0.6` | `retail` |
| [Revervox](https://www.curseforge.com/minecraft/mc-mods/revervox) | `2.1` | `revervox_mod` |
| [Rolling Giant: Oldest View](https://www.curseforge.com/minecraft/mc-mods/rolling-giant-oldest-view) | `1.0.0` | `rolling_giant_oldest_view` |
| [Rotten Creatures](https://www.curseforge.com/minecraft/mc-mods/rotten-creatures) | `1.1.0` | `rottencreatures` |
| [Sanity: Descent Into Madness](https://www.curseforge.com/minecraft/mc-mods/sanity-descent-into-madness) | `1.1.0` | `sanitydim` |
| [SAO MOD](https://www.curseforge.com/minecraft/mc-mods/sword-art-online-expansion) | `1.0.0` | `sao_mod` |
| [SCP:Overtime](https://www.curseforge.com/minecraft/mc-mods/scp-overtime) | `3.1.2` | `scpo` |
| [Siren Head](https://www.curseforge.com/minecraft/mc-mods/siren-head-the-arrival) | `1.1.4` | `siren_head` |
| [Sons of Sins](https://www.curseforge.com/minecraft/mc-mods/sons-of-sins) | `2.2.1` | `sons_of_sins` |
| [Soul Eater](https://www.curseforge.com/minecraft/mc-mods/soul-eater-mc) | `1.25.11` | `soul_eater` |
| [Sound of Fear](https://www.curseforge.com/minecraft/mc-mods/sound-of-fear-horror-sounds) | `1.0.0` | `sound_of_fear` |
| [Sound Physics Remastered](https://www.curseforge.com/minecraft/mc-mods/sound-physics-remastered) | `1.20.1-1.4.10` | `sound_physics_remastered` |
| [Sounds of the Forest](https://www.curseforge.com/minecraft/mc-mods/sounds-of-the-forest) | `1.0.2` | `sounds_of_the_forest` |
| [The After](https://modrinth.com/mod/the-after) | `0.1.2` | `the_after` |
| [The Backwoods](https://www.curseforge.com/minecraft/mc-mods/backwoods) | `1.6.0` | `the_backwoods` |
| [The End of Herobrine](https://www.curseforge.com/minecraft/mc-mods/endofherobrine) | `1.20.1-1.0.8.2` | `endofherobrine` |
| [The Final Goatman](https://www.curseforge.com/minecraft/mc-mods/the-final-goatman) | `4.3.0` | `goatman` |
| [The Graveyard](https://www.curseforge.com/minecraft/mc-mods/the-graveyard-forge) | `4.0.1+mc1.20.1` | `graveyard` |
| [The Hordes](https://www.curseforge.com/minecraft/mc-mods/the-hordes) | `1.6.3g` | `hordes` |
| [The Midnight](https://www.curseforge.com/minecraft/mc-mods/the-midnight) | `0.6.7` | `midnight` |
| [The Midnight Lurker](https://www.curseforge.com/minecraft/mc-mods/the-midnight-lurker) | `3.3.7` | `midnightlurker` |
| [The Mimicer](https://www.curseforge.com/minecraft/mc-mods/the-mimicer) | `1.7.0` | `themimic_er` |
| [The Obsessed](https://www.curseforge.com/minecraft/mc-mods/obsessed) | `1.5.2` | `the_obsessed` |
| [The One Who Watches](https://www.curseforge.com/minecraft/mc-mods/the-one-who-watches) | `1.4.4` | `the_one_who_watches` |
| [The Onlooker](https://www.curseforge.com/minecraft/mc-mods/the-onlooker) | `4.7.1-alpha` | `anta` |
| [The Shooting Star (Demo)](https://www.curseforge.com/minecraft/mc-mods/the-shooting-star-demo) | `1.4.4-demo` | `shooting_star_demo` |
| [The Singing Villager](https://www.curseforge.com/minecraft/mc-mods/the-crying-villager) | `3.5.0` | `singing_villagers` |
| [True Darkness](https://www.curseforge.com/minecraft/mc-mods/true-darkness-forge-updated-fork) | `2.0.103` | `darkness` |
| [Type 95](https://www.curseforge.com/minecraft/mc-mods/type-95-sniper-rifle) | `1.0.2+forge-1.20.1` | `tanya_demo` |
| [Ultimate Elemental Swords](https://www.curseforge.com/minecraft/mc-mods/ultimate-elemental-swords) | `1.0.0-1.20.1` | `ultimate_elemental_swords` |
| [Verity JE](https://www.curseforge.com/minecraft/mc-mods/verity-je) | `6.0.0-ru.1` | `verity` |
| [Whisperwoods](https://www.curseforge.com/minecraft/mc-mods/whisperwoods) | `1.20.1-2.1.2` | `whisperwoods` |
| [Woodwalkers](https://www.curseforge.com/minecraft/mc-mods/woodwalkers) | `5.8.13` | `walkers` |
| [Zombie Awareness](https://www.curseforge.com/minecraft/mc-mods/zombie-awareness) | `1.20.1-1.13.1` | `zombieawareness` |
| [Zombie Nightmare Expansions](https://www.curseforge.com/minecraft/mc-mods/zoniex) | `1.2.1` | `zoniex` |

### Добавленные зависимости (19)

Эти библиотеки не показаны в карточке как ручные дополнения. Уже имеющиеся зависимости ATM9 используются без второй копии. Новая зависимость остаётся NEW и после последующего обновления своего JAR.

| Проект и официальная страница | Версия из JAR | Mod ID |
| --- | --- | --- |
| [Alex's Caves](https://www.curseforge.com/minecraft/mc-mods/alexs-caves) | `2.0.2` | `alexscaves` |
| [atlas-lib](https://www.curseforge.com/minecraft/mc-mods/atlas-lib) | `1.1.12` | `atlaslib` |
| [AzureLib](https://www.curseforge.com/minecraft/mc-mods/azurelib) | `2.0.41` | `azurelib` |
| [Citadel](https://www.curseforge.com/minecraft/mc-mods/citadel) | `2.6.3` | `citadel` |
| [coroutil](https://www.curseforge.com/minecraft/mc-mods/coroutil) | `1.20.1-1.3.7` | `coroutil` |
| [crafted-core](https://www.curseforge.com/minecraft/mc-mods/crafted-core) | `5.8.2` | `craftedcore` |
| [CreativeCore](https://www.curseforge.com/minecraft/mc-mods/creativecore) | `2.12.40` | `creativecore` |
| [FromAnotherLibrary](https://www.curseforge.com/minecraft/mc-mods/fromanotherlibrary) | `1.0.2` | `fromanotherlibrary` |
| [Kleiders Custom Renderer API](https://www.curseforge.com/minecraft/mc-mods/kleiders-custom-renderer-api) | `7.4.0` | `kleiders_custom_renderer` |
| [KuroLib](https://www.curseforge.com/minecraft/mc-mods/kurolib) | `0.6` | `kurolib` |
| [lucent](https://www.curseforge.com/minecraft/mc-mods/lucent) | `1.5.5` | `lucent` |
| [Pehkui](https://www.curseforge.com/minecraft/mc-mods/pehkui) | `3.8.2+1.20.1-forge` | `pehkui` |
| [Photon](https://www.curseforge.com/minecraft/mc-mods/photon) | `1.1.17` | `photon` |
| [platform](https://www.curseforge.com/minecraft/mc-mods/platform) | `1.4.2` | `platform` |
| [rimulib](https://www.curseforge.com/minecraft/mc-mods/rimulib) | `1.1.2` | `rimulib` |
| [simple-voice-chat](https://www.curseforge.com/minecraft/mc-mods/simple-voice-chat) | `1.20.1-2.6.22` | `voicechat`, `voicechat_api` |
| [VillagersTradingPlus](https://www.curseforge.com/minecraft/mc-mods/villagerstradingplus) | `1.1.1+mc1.20.1` | `villagertradingplus` |
| [voice-chat-recording](https://www.curseforge.com/minecraft/mc-mods/voice-chat-recording) | `2.1` | `voicechatrecording` |
| [YetAnotherConfigLib](https://www.curseforge.com/minecraft/mc-mods/yacl) | `3.6.6+1.20.1-forge` | `yet_another_config_lib_v3` |

KuroLib0.6 сохранён для авторских обращений SCP:Overtime. TravelOptics исключён вместе с обязательным аддоном Apex Tides по решению пользователя; базовый Iron’s Spells 3.4.0.11 не менялся.

AzureLib обновлён адресно как **NEW-зависимость**, а не базовая библиотека:

| Версия AzureLib | SHA256 | Статус |
| --- | --- | --- |
| 1.0.34 | `9aca62c9caf1266617d2734e49204b1b2fe119ca58b0579dde47fb1c8f39a206` | Прежний кандидат, не активен |
| 2.0.41 | `25a95a495c586b72f80bf8b65fd1892b2e21a2d9d2e072808e663aa0938401f6` | Активный официальный выпуск |

Родной загрузчик 2.0.41 обработал неизменённую геометрию HSR Phainon1.2.3 Dawnmaker формата 1.21.110; проверены 190 прямых обращений From Another World к API AzureLib. Модели не переписывались, native format guards не обходились. Эти проверки не являются PASS полного клиента или обещанием переноса старых миров без потерь registry ID.

### Исключённые проекты

| Исключённый проект | Последнее решение и причина |
| --- | --- |
| [Alpha Below](https://www.curseforge.com/minecraft/mc-mods/theworldbelow) | Принудительно разворачивает весь ленивый реестр моделей ModernFix. Пользователь выбрал удаление вместо изменения исходных настроек ATM9. |
| [Attack On Block: Season Two](https://www.curseforge.com/minecraft/mc-mods/attack-on-block) | Ресурс геометрии в каталоге анимаций приводил к ошибке AzureLib. Пользователь выбрал удаление вместо собственного ресурса-исправления; From Another World сохранён. |
| [BleachCraft (kojima_here)](https://www.curseforge.com/minecraft/mc-mods/bleachcraft) | По точным авторским текстуре и overlay определён добавленный HUD Physical Attack с кулаком. Пользователь попросил убрать этот мод; в оригинальной ATM9 его нет. |
| [Chainsaw Man](https://www.curseforge.com/minecraft/mc-mods/chainsaw-man-mod) | Пользователь исключил мод после подтверждения безусловной выдачи Health Boost на 99999999 тиков в обработчике игрока. |
| [Dreamshift](https://www.curseforge.com/minecraft/mc-mods/dreamshift) | Обнаружен принудительный обход ленивых моделей ModernFix при длительной загрузке. Выбрано удаление; исходное dynamic_resources=true не отключается. |
| [Dusk Mod](https://www.curseforge.com/minecraft/mc-mods/dusk) | Версия 4.2 обращается к отсутствующему API исходного Cupboard 2.7. Пользователь отказался от урезанной старой Dusk 3.7 и сохранил базовый Cupboard. |
| [Frieren - Singularity](https://www.curseforge.com/minecraft/mc-mods/frieren-spells-zoltraak-singularity-irons-spells) | Требует Iron’s Spells 3.16.x. Пользователь сохранил исходный Iron’s 3.4.0.11. |
| [Kimetsunoyaiba](https://www.curseforge.com/minecraft/mc-mods/demonslayer) | Голубая стрелка и пять квадратов HUD сопоставлены с OverlayCooldownTimeOverlay по точным пиксельным якорям. Пользователь выбрал удаление Kimetsu; похожий Jujutsu Craft оставлен. |
| [Mine Piece](https://www.curseforge.com/minecraft/mc-mods/mine-piece) | Callback удаления эффекта повторно меняет карту эффектов, добавляя Slowness; в цепочке очистки возникала ConcurrentModificationException. Совместимый авторский конфиг/выпуск не найден, выбран отказ от мода. Mine Mine no Mi сохранён. |
| [Mushoku Tensei (Wiwar)](https://www.curseforge.com/minecraft/mc-mods/mushoku-tensei-mod) | Пользователь попросил убрать добавленный экран Choose a Class (Mage/Swordsman), принадлежащий ClassPickGUIScreen этого мода. |
| [Mushoku Tensei Addon](https://www.curseforge.com/minecraft/mc-mods/mushoku-tensei-addon) | Исключён вместе с обязательным родительским Mushoku Tensei по последнему решению пользователя. |
| [Tenshō: Eclipse Legacy](https://www.curseforge.com/minecraft/mc-mods/tensho-spellbooks-destruction-spells) | Требует Iron’s Spells 3.16.x. Пользователь сохранил исходный Iron’s 3.4.0.11. |
| [The Shooting Star Addition](https://www.curseforge.com/minecraft/mc-mods/the-shooting-star-addition) | Авторская инъекция скрытия солнца/луны не соответствует целевому методу. Исключён весь аддон, включая Halley и Luna; Shooting Star Demo сохранён. |
| [The Shooting Star: SS-21 Quasar](https://www.curseforge.com/minecraft/mc-mods/the-shooting-star-addition-ss-21-quasar) | У 1.7.1 отсутствует refmap HUD. Совместимая старая связка 1.7.0 требует отката других модов; пользователь выбрал удаление Quasar и сохранил Shooting Star Demo. |
| [Vocaloid Stars](https://www.curseforge.com/minecraft/mc-mods/miku-star-a-shooting-star-addon) | Пользователь исключил весь аддон после ошибки линковки шейдера нового декоративного tooltip Stellar Remote в 1.4.4.2. Shooting Star Demo сохранён. |
| [Void Manifestations: Iron's Spellbooks](https://www.curseforge.com/minecraft/mc-mods/void-manifestations-spells-addon) | Требует Iron’s Spells 3.16.x. Пользователь сохранил исходный Iron’s 3.4.0.11. |
| [Roundabout](https://www.curseforge.com/minecraft/mc-mods/roundabout-the-jojo-mod) | Положительный частный A/B и native callers связали новые Generic GL/Jade ошибки с этим модом; пользователь согласовал исключение. |
| [Born in Chaos](https://www.curseforge.com/minecraft/mc-mods/born-in-chaos) | Авторский Scarlet attack не загружался и имел реальный caller. Пользователь выбрал исключение без собственного исправления JAR. |
| [Null Presence](https://www.curseforge.com/minecraft/mc-mods/null-presence) | Две неверные функции имеют активные scenario callers; исключение согласовано. |
| [T.O Magic ’n Extras / TravelOptics](https://www.curseforge.com/minecraft/mc-mods/to-tweaks-irons-spells) | Неверная дополнительная loot table вызывается собственным modifier. Исключён NEW dependency, не BASE JAR. |
| [Apex Arcana: Tides](https://www.curseforge.com/minecraft/mc-mods/apex-arcana-tides-t-o-magic-n-extras-addon) | Исключён вместе с обязательным TravelOptics. |
| [DimensionalDoors](https://www.curseforge.com/minecraft/mc-mods/dimensionaldoors) | Пользователь выбрал исключение после новых palette-frame диагностик в BASE Moonlight/Amendments; полная причинность всех последствий не заявляется. |
| [Solo Leveling: Reawakening](https://www.curseforge.com/minecraft/mc-mods/solo-craft-reawakening) | Пользователь выбрал исключение после двух неверных Kaiselin animation clips; default fly был корректным. |
| [The Knocker](https://www.curseforge.com/minecraft/mc-mods/the-knocker) | Неверный общий durability tag ссылался на отсутствующий knife item. |
| [Gachiakuta](https://www.curseforge.com/minecraft/mc-mods/gachiakuta) | Неверная дополнительная loot table ссылалась на незарегистрированный предмет. |
| [From The Fog](https://www.curseforge.com/minecraft/mc-mods/from-the-fog) | Неверная `watching:check` function; обычный текущий caller не установлен. Пользователь всё же выбрал исключение. |

Это история последних решений, а не неактивные JAR внутри active files. Все перечисленные проекты отсутствуют в выбранном составе. [Десять новых exact-SHA исключений](tools/approved-removals-20261030.json) отделены от активного lock; все они NEW, ни один BASE JAR не удалён. По проверенным declared mandatory edges внешних обязательных зависимых нет; Apex Tides и TravelOptics удалены вместе. Jujutsu Craft, Grotesque Steve, Citadel, Alex’s Caves, Alex’s Mobs и Rats сохранены. Прежние отменённые варианты не возвращаются автоматически; отсутствие удалённых JAR само по себе не является runtime PASS нового набора.

## Адресные изменения AllTheLeaks и Grotesque Steve

AllTheLeaks остаётся BASE по членству, но используется [официальная Forge 1.20.1 версия 1.1.4](https://www.curseforge.com/minecraft/mc-mods/alltheleaks/files/9188826), не собственная модификация его JAR.

| Файл | SHA256 | Размер |
| --- | --- | ---: |
| Авторский BASE `alltheleaks-1.0.7+1.20.1-forge.jar` | `9df833a1e3fb0cc8e4fe43fd2637d5d7745edfe38356a13baaa69457982d4de6` | 1 173 400 |
| Закреплённый официальный `alltheleaks-1.1.4+1.20.1-forge.jar` | `fb72063a7d17df97740d24355444ef2f95eab97728e1256c639bb432c61b7716` | 1 274 164 |

Пользователь выбрал сохранять совместимый pin1.1.4 и при следующих обновлениях авторской ATM9. Новый author import перепривязывает `original` по реальному mod ID и точным новым SHA/размеру, но не заменяет наш pin автоматически даже более новой авторской версией. Изменение этого решения — отдельный review. Пропавшее ownership отклоняется; неизвестные BASE/JAR не перезаписываются, NEW-зависимости не превращаются в BASE. Подробности — в [owner workflow](tools/atm9_quest_updates/OWNER_WORKFLOW.md).

[Полный статический аудит AllTheLeaks](tools/qa/alltheleaks-1.1.4-static.json) проверил весь JAR, вложенные библиотеки и изменённые пути. Новый version guard исключает Citadel2.6.3 до попытки обращаться к уже отсутствующей старой static map. Сам Citadel и его зависимые моды сохранены: утечка, потеря FPS или crash от того прежнего предупреждения не доказаны. Обновление AllTheLeaks также меняет capability/cache/shutdown-поведение; это не обещание исправить Blood Magic или все утечки, а текущий полный клиент и штатный выход проверены отдельно в указанном runtime-отчёте; долговременные RAM/FPS-показатели не измерены.

Grotesque Steve сохранён как **1.4.2-quiet.1** по отдельному разрешению: отключены два callback входа с английской action-bar подсказкой, звуками wind/fart и автоматической выдачей книги. В `manualgiver.mcfunction` исправлен один недопустимый начальный `/`; содержимое книги, другие применения звуков, штатная функция `grotesque_steve:give` и advancement-ресурсы сохранены. Четыре ZIP-записи изменены, 2 495 остальных побайтно прежние; новые классы не добавлены. Это адресная производная пользовательской редакции, не новый официальный релиз и не заявленное исправление всех игровых механизмов.

Оригинал Gumroad1.4.2, SHA256 `7edde5b1506a69a725412769525ba16122b1dd4c38e35f3edc5c015eef3a6f63`, хранится в Git как source-only `tools/GrotesqueSteve/source/grotesque_steve-1.4.2-forge-1.20.1.jar`, не второй активный мод. [Точный patcher](tools/grotesque_steve_quiet.py) восстанавливает производный SHA256 `ffa7df6fb07e54217757436b566fa0073b460c5fa4b695cfd2d4d40692208052` локально без загрузки Gumroad или подмены бесплатной редакцией. Оригинал и tool закреплены в transformation; их отсутствие/иные байты приводят к отказу до BASE-записи.

[Подготовка Grotesque quiet](tools/GrotesqueSteve/preparation-report.json) включает 13 положительных/отрицательных тестов, повторное точное воспроизведение и Java17 `-Xverify:all` с настоящими Forge/Minecraft классами. Standalone-проверка callback и command syntax не выдаётся за вход в мир или проверку всей item-registry. Независимая сверка ZIP и структуры классов подтвердила четыре изменённые записи и сохранность всех байтов вне Code двух callback. Границы описаны в [source-only руководстве](tools/GrotesqueSteve/README.md); текущий полный клиент загрузил новый мир и завершился штатно. Прежних function-ошибок Grotesque в его закрытом логе нет; все способности этим не объявлены проверенными.

## Пресет управления

Общая раскладка применяется отдельной кнопкой лаунчера и меняет только клавиши. P нужно удерживать для разговора с Verity. Карта M, рюкзак B, квесты на Ё/grave accent, Curios G и обычные WASD сохранены. Настроены основные меню/колёса/циклы/превращения и все восемь самостоятельных действий Jujutsu. Назначения исключённых модов убраны. Полная таблица — [руководство по управлению](launcher/controls-guide.md).

Для некоторых боевых веток нужны собственные назначения в меню Minecraft: классические способности Cursed Fate 1–7, все пять действий HSR Phainon, четыре Stellar Remote из Shooting Star, а также Dash Fairy Mine, Resonate/Soul Perception и Laser Mask. Действие мебели SCP Overtime и четыре свойства палочки Crystalix также оставлены для выбора кнопок игроком. Это прямые действия без настроенной здесь замены; они не выдаются за полностью управляемые через другое меню. Родные кнопки и остальные неназначенные группы перечислены в руководстве и `tools/keybinds/stock.json`.

Текущий файл содержит 642 имени: 186 назначений и 456 свободных строк. У 85 независимых действий мира разные физические кнопки; исходные GUI и авторские спутники ввода сохранены отдельно, поэтому ноль всех красных строк Controls screen не заявляется. Некоторые назначения используют цифровой блок, Menu и боковые кнопки мыши; при отсутствии этих клавиш нужны свои варианты. Пресет не меняет язык, графику, дальности, голос или микрофон. Нативные getters текущего клиента подтвердили все 642 имени, клавиши и модификаторы; после штатного выхода все 642 активных назначения сохранены. В техническом options.txt остались 40 незагруженных строк старого QA-пресета: их нет в текущих Options и поставляемом пресете. Это проверка заранее инициализированного технического профиля, не первый запуск. QA13 с 682 назначениями остаётся отдельной историей.

**Сначала запустите новую установку до главного меню и штатно закройте игру, затем применяйте пресет.** Авторский DefaultSettings при первой инициализации копирует свой профиль поверх `options.txt`, поэтому пресет, применённый раньше, может быть заменён. Пресет остаётся необязательным действием игрока; авторские DefaultSettings и его профиль не изменялись.

## Русские квесты и разрешённые изменения BASE-текстов

Основа перевода — [Scriptora](https://www.mc-scriptora.ru/) из [CurseMen/ATM9 1.0.8](https://github.com/CurseMen/ATM9/releases/tag/1.0.8), адаптированная к точной структуре ATM9 1.1.1. Это отдельная адаптация, не новый официальный релиз автора. Полное MIT-уведомление сохранено; происхождение описано в `library/ru-quests-provenance.md` и поставляемых `kubejs/atm9_ru_quests_license.txt` / `kubejs/atm9_ru_quests_provenance.md`.

Изменены 106 существующих SNBT и дополнен исходный английский `kubejs/assets/kubejs/lang/en_us.json`: всего 107 BASE-ресурсов. Добавлены 325 стабильных языковых ключей, все 7 212 прежних английских значений сохранены. Новый `kubejs/assets/kubejs/lang/ru_ru.json` содержит 7 538 ключей, SHA256 `18fde6566400e636cc82fa3fa111cd76359c9266d828180f318ce892262772e4`.

Точный native-разбор 145 SNBT подтвердил 327 разрешённых display-различий в `title`, `subtitle`, `description`, `hover`, включая подписи задач/наград. Остальные 80 167 leaf-тегов совпадают: ID, типы, задачи, награды, координаты, зависимости и другие данные не менялись. Обратное сравнение JSON-компонентов сохранило действия, стили и цели кнопок. Английское отображение совпало в 326 местах; в одном исправлена прежняя лишняя закрывающая скобка. Все 327 русских display-строк разрешились; 7 538 строк прошли native I18n/macro-проверку без ошибок формата.

Служебные скрытые уведомления об авторстве, изображения, химические символы, бренды, имена и URL сохраняются. Их наличие на исходном языке не означает потерянный перевод обычного текста. `tools/atm9_ru_quests.py` и `tools/atm9_ru_quests/manifest.json` закрепляют обратимую exact-hash нормализацию/применение; неизвестные изменения отклоняются до записи. Проверки структуры и перевода не подтверждают все экраны или прохождение каждого задания.

Для следующих авторских версий добавлен [маршрут подготовки и review перевода](tools/atm9_quest_updates/OWNER_WORKFLOW.md) через [update_atm9_quests.py](tools/update_atm9_quests.py). Свежий подтверждённый авторский или совместимый community RU имеет приоритет над ручным fallback; ручная строка применяется только при совпадении английского fingerprint. Устаревший или отсутствующий перевод уходит в отчёт и штатный EN fallback, не замораживая обновление сборки. Свежий внешний перевод запрашивается только явной командой владельца; обычные CI/restore используют закреплённые данные без скрытого обращения к latest.

Schema2 reader уже поддерживает будущие reviewed data/locks без переписывания validator под число глав или версию. Он сохраняет строгую проверку нового BASE, неизвестных JAR/конфигов и допустимых display-полей. Quest-profile 1.1.1 остаётся прежним: tool `8be48f…`, manifest `9ebb5a…` и все 108 текстовых ресурсов не меняются добавлением инструментов; адресные JAR-изменения закреплены отдельными записями lock. Общие [проверка профиля](tools/atm9_quest_profile.py) и [восстановление](tools/atm9_quest_restore.py) совпадают с опубликованной Original `0555209`; это source-only workflow, не игровой мод и не доказательство совместимости будущих дополнений.

## Данные самой сборки: предупреждения, Rats и Verity

Rats включает свой встроенный Ratlantis для новых миров через собственный COMMON-конфиг. Старый 1.16-аддон или собственный помощник не используются. Подтверждение включения в предыдущем техническом мире не заменяет новый полный прогон этой ревизии.

По запросу пользователя удалено предупреждение Meulti’s Backrooms до игры и при загрузке мира. `tools/photosensitivity-removal.json` закрепляет:

| Файл | Точное изменение |
| --- | --- |
| `config/mbackrooms/Mbackrooms-Config-Common.toml` | Native `photosensitivityWarningDisplayed=true`. Полный COMMON-файл управляется сборкой; остальные авторские значения, включая вспышки и jumpscares, сохранены. SHA256 `6303f72e29904d154d40098f291f0093862ad8c9e1f3b5d277a3585f887f6c93`. |
| `kubejs/assets/mbackrooms/textures/gui/photosensitivity_warning/title.png` | Только эта картинка заменена неизменённым прозрачным 1×1 `empty.png` того же автора: 350 байт, SHA256 `581b9352f1c1b0af5ce7bfb36e5db6ea55bc6b409f722db965abcd2ee0b0a76b`. |

Авторский Meulti JAR не изменён. Это намеренное изменение предупреждения через данные, без отключения вспышек, jumpscares, шейдеров и прочих эффектов. В работающем клиенте diag12 Native ResourceManager подтвердил победивший KubeJS-ресурс; декодирование отдельно проверено Java ImageIO/Pillow. Визуальная оценка предупреждения отдельно не объявляется. Синхронизация управляемого COMMON-файла не обещает сохранять его личные правки.

Совместимость Verity задаётся самой сборкой в `tools/verity-native-compatibility.json`:

- На `StartupEvents.postInit`, после Forge CONFIG_LOAD, штатный `VerityConfig.KILL_ENTITIES.set(false)` отключает только автоматические смерти животных/жителей при появлении/загрузке сущностей. Это отдельное решение пользователя после зависания цепочки с базовым EvilCraft; другие AI/боевые обработчики не меняются. Значение сохраняется native autosave: одно удаление скрипта не вернёт его вtrue.
- Перед native TagLoader.build из общего тега `minecraft:music_discs` удаляются только два несуществующих авторских ID `verity:verity_disc` и `verity:verity_edit_disc`. Весь тег не заменяется; вклад других модов сохраняется. Это устраняет источник неверных ссылок, затрагивавший зависимые теги Botania/Biomancy, без переписывания их JAR.
- Ранний `atm9_modified_verity_ai.js` задаёт локальный AI до первого native consumer endpoint; один postInit для этого опаздывает. Прочие настройки и выбранные игроком параметры голоса сохраняются.

В этих изменениях используется существующий авторский KubeJS и native API. Скрытого mod-specific писателя Verity TOML в C# нет. В diag12 и отдельно в текущем финальном мире измерен настоящий игровой запрос этого маршрута: авторский обработчик получил ответ локального AI и вывел его по-русски. Итоговый текущий прогон, границы renderer/GL и оставшиеся ERROR описаны в runtime-отчёте.

## Русский Verity и переносимый локальный AI

По прямому разрешению пользователя Verity JE6.0.0 локализован и заморожен как **6.0.0-ru.1**, с прежним mod ID `verity`. Автоматическое обновление этого замороженного JAR не предусматривается.

| Verity | SHA256 |
| --- | --- |
| Официальный вход 6.0.0 | `f76f641f17ea3e3b2e8486596790ae65c27c2b016fae6ed8557c67887816b7d0` |
| Русский 6.0.0-ru.1 | `45fc05ee600c24e989a5a2c17fab099fa5bd15415ee9d848e73885e8f42b85d8` |

`tools/verity_russian.py` и `tools/VerityRussian/` описывают точные входы, текстовые изменения и четыре побайтно одинаковые полные Windows/Linux-пересборки. Протокольные ID и авторские игровые методы сохранены; native конфигурационные исключения перечислены выше.

Внутри JAR используются русский Piper Denis medium для TTS и multilingual Whisper base int8 с русской транскрипцией для STT. Отдельные native-тесты выполнялись с реальными байтами моделей без микрофона/воспроизведения; распознавание вероятностно. Заменены три речевых клипа, два коротких вызова — явно контекстные адаптации «Привет!» и «Кто-нибудь здесь?». Остальные музыка/эффекты и 248 кадров вступления сохранены.

После **«Играть»** общий установщик подготавливает закреплённые официальные Ollama 0.40.12 Windows amd64 и `qwen3:1.7b` в переносимом дереве лаунчера, проверяет SHA/размеры и повторно использует кеш. Заранее установленная Ollama, API-ключ, подписка и ручной запуск сервера не требуются. Версия runtime, URL, модель, хэши и относительная схема установки принадлежат `launcher/ollama-recipe.json`; `launcher/local-ai.json` закрепляет сам recipe и Verity JAR. Их нельзя подменять непроверенным содержимым кеша.

Статические `aiProvider=OLLAMA`, модель и `aiThink=false` задаёт pack startup-скрипт. Лаунчер передаёт только созданный для текущего запуска loopback endpoint через необязательный строгий контракт `launcher/launch-context.json` в приватный instance-owned `launcher-runtime/launch-context.json`. Этот runtime-файл не входит в поставку; окружение, личные пути и секреты в него не выгружаются. Рецепт и новый контракт требуют поддерживающий их лаунчер; 417 не является подходящей версией для этой новой поставки.

Запись AI-полей выполняет native NightConfig внутри pack startup, не лаунчер. Личные голосовые значения остаются нешипуемой конфигурацией игрока; штатные свежие LOCAL TTS/NATIVE STT не подменяются C#-писателем. Повреждённый TOML не исправляется молча; проверка parser/writer не является гарантией аварийного завершения всего клиента при script error или атомарной записи NightConfig.

В diag12 на диагностической сборке исходников 420 настоящий игровой chat прошёл через авторский обработчик и переносимый Ollama: `/api/chat` вернул HTTP 200 за 37,65 с, ответ был русским. После завершения приватного CLI-координатора тот же мир/backend продолжали работать 48,37 с; штатный выход из игры дал код 0 и завершил принадлежащие запуску Ollama/llama-server, endpoint закрылся. Закрытие полного GUI-лаунчера, физический ввод и игровой микрофон остаются отдельными непроведёнными проверками. Итоговая приёмка ещё открыта; подробности в `TESTING-STATUS.md`.

## Что перенесено из лаунчера и что осталось

Фиксированные настройки и совместимость принадлежат исходнику сборки: recipe AI, четыре AI-поля, native Verity policy/tag, Rats, предупреждение Meulti, русские квесты, `config/log4j2.xml` и выбирающий его `launcher/jvm-args.txt`. Логирование сохраняет ERROR; отдельный полный debug.log не создаётся, а уровни/ротация теперь являются явными данными сборки.

Глобальные принудительные настройки ModernFix и общий 5-секундный HTTP-таймаут убраны из C#; исходное ATM9 `dynamic_resources=true` сохранено без обхода native guards. Собственные пределы 16 для рендера, симуляции, теней и отдачи чанков удалены. Действуют штатные авторские значения и выбор игрока, с сохранением native аппаратных/форматных проверок. Глобальная правка регистрации меню контентных модов не выдаётся за необходимость UUID/скинов; Modified не содержит её целевых классов. Изменения иных сборок принадлежат их отдельным источникам и проверкам.

| Что остаётся в общем контуре запуска | Почему это не фиксированный конфиг сборки |
| --- | --- |
| Проверка/загрузка Java, loader, общих компонентов, кешей и блокировок процесса | Эти файлы должны быть готовы до загрузки модов; пути, свободное место, текущие процессы и состояние кеша определяются на конкретной машине. Данные поставки и SHA закрепляются отдельно. |
| Подготовка общего e4steam | Лаунчер проверяет точный сетевой артефакт подходящей платформы до Forge/NeoForge. GUI-политика уже содержится в опубликованном JAR, не создаётся правкой при запуске; источник/авторские и производные координаты раскрыты ниже. |
| Текущие Steam identity, UUID/skin-сопоставления и общий LAN-контур | Используют текущий вход, участника, соединение и native `isPublished`; личные реестры нельзя публиковать как общий конфиг. Это не разрешение на посторонние изменения контентных модов. |
| Общая нативная публикация LAN/«Жалобы», совместимость движения гостя и сетевой выдачи чанков там, где активированы проверенные caller/site | Решения зависят от живого мира/игрока/сессии и различающихся native API. Универсальная штатная замена через статические pack-файлы для всех поддерживаемых веток без собственных контентных модов не подтверждена. Лимита дальности здесь нет; независимые конечные сетевые бюджеты не равны пределу обзора. |
| Переносимые пути, child environment, память и loopback binding | Их конкретные значения известны только при старте. Статическая AI-модель и настройки уже перенесены в recipe/pack startup; приватный endpoint — только вход запуска. |
| Личные миры, профили, skin/waypoint/identity-данные и транзакции их сохранения | Это данные игрока, не payload сборки. Общий код сохраняет/переносит их с проверкой ownership вместо публикации личной копии в репозитории. |
| Явно выбранное применение пресета | Данные пресета принадлежат сборке, а общий merge изменяет только выбранные параметры существующего личного файла по действию пользователя. Он не навязывает новые графические лимиты. |
| Текущие пользовательские уведомления | Содержимое и срок жизни возникают в работающем лаунчере/процессе; это не статический ресурс мода. Полный native-клиент проверен отдельно; интерактивный маршрут GUI-уведомлений не проверялся. |
| Заголовок окна из имени локальной папки | Сохраняется прежний явный пользовательский контракт. Локальное имя заранее неизвестно опубликованной сборке; единая native-замена на всех платформах без добавления собственных модов не проверена. Это отдельная UI-задача, не необходимость идентичности. |

Это конкретный перечень оставшегося поведения, а не общее исключение для всех hooks или утверждение принципиальной невозможности будущего native-порта.

### Общий Steam: UI уже изменён в готовом артефакте

[Опубликованный профиль `native-lan-ui-v1`](https://github.com/MarkZamore/e4steam/releases/tag/native-lan-ui-v1) покрывает все 19 выбранных loader/MC-артефактов. В шести современных e4steam 0.3.4 заранее удалены дополнительная кнопка LAN Settings и три перенаправления штатных экранов в промежуточную форму. Steam Invite Friends, аутентификация и транспорт сохранены. У 13 старых 0.3.2 этого окна уже нет, поэтому их авторские байты/исторические URL не менялись.

Каждый современный производный JAR меняет только `PauseScreenMixin.class`, `e4steam.mixins.json` и добавляет downstream NOTICE. Все остальные распакованные записи, включая сетевые классы, metadata, native-библиотеки и лицензии, совпадают с авторскими. In-JAR версия 0.3.4 сохранена для API-совместимости; суффикс `-lanmc-native-ui.1`, DeliveryTag и SHA отдельно обозначают производный артефакт. Оригинальные релизы автора не перезаписаны.

Для текущей Forge-платформы используется `e4steam-forge-mc1.18.2-1.20.2-v0.3.4-lanmc-native-ui.1.jar`: 3 801 104 байта, SHA256 `68ba6bdce76868e2cb43359a13416dfa1b011c628c13b6c4266b653c765b5c40`. Это общий сетевой компонент, не один из 431 базовых или 81 вручную запрошенного JAR.

Исходный cross-version `pack.mcmeta` этого Forge JAR сохраняет формат 18. Для обычного мода Forge 47 использует native `mod_resources` / `DelegatingPackResources` с текущим форматом 15; это отдельно проверено настоящим MC 1.20.1 serializer. Использование самого JAR как обычного ресурспака не эквивалентно этому loader-пути. Проверка иных версий provider не объявляется выполненной только по сохранению metadata.

Linux/Windows source CI, 18 packaging-тестов, независимое сравнение методов приглашения, 20/20 сравнений файлов двух OS и загрузка всех 19 публичных вариантов подтвердили поставку. Это не PASS GUI/Steam двух клиентов всех пяти карточек. В native MC 1.20.1 уже опубликованный мир выбирает `menu.playerReporting`; новый реальный клиентский UI/LAN-маршрут проверяется отдельно. На версиях без native reporting собственный экран жалоб не изобретается.

## Текущий полный прогон после исключений

[Текущий отчёт](tools/qa/final-runtime-post-removals-420.md), [структурированные данные](tools/qa/final-runtime-post-removals-420.json) и [сравнение с Original](tools/qa/final-post-removals-comparison.md) относятся именно к lock `214b22b429d73f9b68b88c32021253cde056d10e137199a373b92b810e2fcf09`, а не к QA13. Все 531 source JAR и общий E4 совпали по SHA256 до и после игры. Три здоровых native-наблюдения меню и мира, ещё 308,894 с мира без ввода, отдельный русский AI-диалог, сохранение 83 измерений и выход0 выполнены. Все 642 активных назначения совпали с пресетом и сохранились. Оба AI-процесса завершились вместе с игрой; тот же локальный API после выхода отказал в соединении.

Полный закрытый лог имеет SHA256 `8caa25571668ea8bd1973a9f8a30df9841152457909804de5ee4ca7c2a1505e0`: **902 ERROR/0 FATAL =109 до ввода +792 после границы до выхода +1 при завершении**. Числа относятся к разной активности и длительности, не являются частотами и не означают 902 сломанных функции. Из 109 событий до ввода: 89 общих BASE/семантических GTCEu, 6 собственных сообщений новых компонентов, 2 BloodMagic и 12 намеренных JEI/Grand Sigil.

Свои новые ERROR оставляют **AzureLib (2), Celestisynth (1), Meulti’s Backrooms (1), YACL (1)** — отсутствующий `minVersion` в mixin metadata — и **CraftedCore (1)** при HTTP404 списка Patreon с резервом. Эти заголовки сами по себе не доказывают отказ инъекций или обычных превращений. Доказанная связь NEW→BASE — **Verity→Forge EventBus:790** диагностик после отдельного AI-чата. Это 395 пар для не-Event классов Jackson/LangChain; совпавшие байты и прежний нативный transformer-probe возвращают неизменённые ClassNode. Потеря 395 игровых handlers не установлена, настоящий русский ответ в этом мире получен. Логи и механики ради результата не подавлялись.

Ещё четыре BASE-заголовка имеют неустановленного NEW-инициатора: два BloodMagic/Curios Optional при первом chat panel и два поздних Placebo/Apotheosis `#irons_spellbooks`. Для Placebo найдено несовпадение неизменённых BASE-данных: Iron хранит подходящий magician в `boss_gear/`, текущий Placebo читает `gear_sets/`. Его штатный код пишет два сообщения и выбирает набор без фильтра, не бросая исключение. Конкретная живая сущность/caller не захвачены, в измеренном Original случай не воспроизведён; близость по времени к AI не доказывает вину Verity. Прежних AllTheLeaks/Citadel `dataMap`, Generic GL173538523, Jade/null BlockPos и ресурсных/function-ошибок удалённых модов в текущем полном логе нет.

Этот результат не проверяет первый/повторный запуск, все способности, Box, два LAN-клиента, выбранный скин, личные миры или пиксельное качество. Исторический Box crash не объявлен исправленным. Непроведённые проверки не превращаются в PASS и не добавляются как новые общие блокеры к согласованной приёмке.

[Владелец принял текущий native-прогон](tools/qa/native-source-acceptance.json) в согласованных границах полного клиента/нового мира и раскрытых остаточных ERROR. Эта приёмка не заменяет отдельные проверки миграции и публичной поставки.

## Авторские остатки и защита мира

До согласованного исключения Born in Chaos 1.7.5 штатные loaders пропускали Scarlet Persecutor `attack`, прямо запрашиваемый моделью/контроллером. Все 15 официальных Forge 1.20.1 выпусков сохраняли этот дефект. Три старых idle-файла давали parser errors, но текущие Baby Skeleton/Bone Imp использовали чистые `*2`-файлы; потеря их idle не была установлена. Мод исключён по решению пользователя, собственный ресурсный патч не применялся.

До согласованного исключения Solo Leveling: Reawakening 1.2.0 у Kaiselin не загружались idle/walk, а default controller выбирал корректный fly. Поломка штатного полёта не была доказана; все dynamic callers не проверялись. Пользователь выбрал удаление мода; скрытый откат до 0.10.7.5 с потерей Kaiselin и других registry ID не выполнялся. Эти исторические дефекты новых модов не выдаются за ошибки исходной ATM9 или новые остатки после удаления.

Предупреждение Mine Mine no Mi об альтернативной Arclight-инъекции не отменяет найденный primary Forge вызов `KairosekiCoatingHandler` из реального BoatItem. Это проверка caller, а не самостоятельный тест способности.

[Исторический полный QA13](tools/qa/final-runtime-420.md) прежних 541 JAR подтвердил главное меню, нативно созданный новый мир, три здоровых состояния мира и штатное сохранение/выход с кодом 0; собственный AI backend завершился. В полном окне 134 ERROR и 0 FATAL. Чат и PTT в этом прогоне не выполнялись. Русский AI-ответ из diag12 остаётся отдельным доказательством; его 790 записей для 395 пар Jackson/LangChain parent-discovery/transform diagnostics не повторялись без chat и не объявляются исправленными. Точный eventbus/ASM probe возвращал неизменённые ClassNode; подавление логов не применялось.

[Сопоставимая текущая Original](tools/qa/matched-baseline-comparison.md) дала 96 ERROR/0 FATAL, Modified QA13 — 134/0. Разность количества не измеряет частоту или число новых причин. OpenAL `Deleting stream buffers: Invalid operation.`, shader-link/unlinked-uniform и сопоставленные базовые GTCEu сообщения воспроизведены в Original и приняты пользователем как общий некритический фон; удаление новых модов ради них не рекомендуется.

Для новой Generic GL `173538523` синхронный стек установил Roundabout depth-copy caller. [Частный A/B с удалением только Roundabout](tools/qa/roundabout-single-removal-ab.md) дал 0 таких сообщений вместо 30 475 и 0 Jade null-BlockPos заголовков вместо 3; шесть нативных чтений поля без Roundabout были non-null. Вместе с проверенным кодом это положительная причинная проверка двух случаев в данных условиях. Реальные форматы FBO и визуальный ущерб не измерялись. Blood Magic / Curios Optional/chat-overlay сохранилась: 2 ERROR с модом и 2 без него, виновник ещё не установлен. Эти измеренные GL/Jade случаи обосновывают согласованное пользователем исключение Roundabout; итоговая поставка фиксируется отдельно и не выдаётся за уже испытанный A/B-вариант.

В QA13 подтверждён вход естественной и отдельно призванной `verity:box` в native model/animation path с растущим временем модели. Исторический render crash не повторился; это не доказательство его исправления, полного GPU draw или качества изображения. Эффекты и guards ради результата не отключались.


Пользователь запретил собственный Safety/framework, поэтому они не добавляются и exact-SHA защитные профили не создаются. Причина отсутствия такой правки зафиксирована; это не доказательство автоматической claim-защиты. Разрушение мира, инвентари, отложенные способности и native permission gates остаются авторскими, кроме перечисленных явно согласованных конфигурационных изменений. Полная защита всех новых способов изменения мира не проверена.

## Восстановление, миграция и приёмка

```sh
python tools/restore_modified.py --pack . --cache artifacts/verified-downloads
python tools/verify_modified.py --pack . --require-loaded-inventory
python -m unittest discover -s tools -p "test_*.py"
python tools/generate_manifest.py --pack . --out dist --revision YOUR_COMMIT
python tools/generate_manifest.py --pack . --out dist --verify-all
```

Локализация BASE-текстов восстанавливается exact-hash профилем перевода: известные изменённые байты нормализуются перед авторским импортом и применяются обратно после него; неизвестные файлы не перезаписываются молча. `tools/legacy-files.json` содержит прежние управляемые SHA только для безопасной очистки старой установки, не как входы новой сборки.

Публикация должна сначала загрузить и проверить весь payload/библиотеку, затем manifest. Копии личных миров, профилей и сырые логи не шипуются; тестовые миры одноразовые. Удаление модов не обещает перенос старого мира без потери registry ID. Для текущего `214b22b429d73f9b68b88c32021253cde056d10e137199a373b92b810e2fcf09` выполнены полный клиент, новый мир, настоящий русский AI-диалог, штатный выход и классификация ERROR. Этот source-native отчёт не устанавливает результат миграции или публичной поставки. Их проверяют отдельно до добавления Modified card; актуальные опубликованные файлы и ход поставки отражают [pack-latest](https://github.com/MarkZamore/All-The-Mods-9-Modified/releases/tag/pack-latest) и [workflow](https://github.com/MarkZamore/All-The-Mods-9-Modified/actions/workflows/publish.yml). QA13/`2f48…` сохраняется исторически. Подробные результаты и отдельные непроведённые проверки — в [TESTING-STATUS.md](TESTING-STATUS.md).
