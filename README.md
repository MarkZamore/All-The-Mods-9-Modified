# All The Mods 9 Modified

По запросу пользователя 7 ноября 2026 года удалён The Midnight Lurker 3.3.7 и его индикатор безумия. Текущий состав — 514 JAR, 539 полных mod ID и 429 модов/аддонов в игровом счётчике. Управление сохраняет 554 назначения. Исторические отчёты ниже относятся к своим прежним составам. Удаление может привести к потере контента этого мода в старых мирах.

Minecraft 1.20.1 загружается лаунчером из официального источника Mojang в общий кеш. Публичная поставка Modified не содержит оригинальный client JAR. Исходный `tools/upstream-lock.json` сохраняет официальный URL и контрольные суммы для восстановления и QA. Запись прежнего JAR в legacy-инвентаре позволяет распознать и убрать известную копию при обновлении установки.

Отдельная чистая производная от оригинальной **ATM9 1.1.1**, **Minecraft 1.20.1**, **Forge 47.4.0**. ID: `all-the-mods-9-modified`; папка установки: `All the Mods 9 Modified`. Оригинальная ATM9 остаётся самостоятельным профилем. Для Modified подготовлены [собственный источник](https://github.com/MarkZamore/All-The-Mods-9-Modified) и профиль поставки `pack-latest`; прежние наработки Modified не служат входом для этой сборки.

**Предыдущий состав515:** по явному решению пользователя исключён Antlers. Предыдущие удаления, включая Presence Footsteps, Sound Physics Remastered и HSR Phainon, сохраняются. Самостоятельный Simple Voice Chat сохранён. Остальные515 JAR и все554 назначения пресета не изменены. Карточка540mod ID является source-проекцией исторического557 снимка; игровой счётчик и группировка библиотеки описываются отдельно. Steam-подключение подтверждено на лаунчере435: реальная проверка состояния сетевого канала приостанавливает чанки во время заполнения очереди и возобновляет их без изменения дальности. См. [двухсторонний отчёт](tools/qa/steam-network-435-acceptance.json).

Временная JDI-диагностика снята после успешного Steam-теста435: три исполняемых файла, два JVM-флага и временная ownership-строка удалены из поставки; обновление удаляет только их точные известные байты. Постоянное ограниченное логирование сохранено. Официальный ModernFix5.25.0 остаётся как ранее согласованный авторский фикс кэша Ingredient, а не как диагностическая утилита или причина исправления Steam. [Точная очистка](tools/qa/temporary-recipe-diagnostics-cleanup.json), [обоснование ModernFix](tools/qa/modernfix-525-retention.json).

**JourneyMap:** исправлен неоднозначный выбор Java-перегрузок настоящими KubeJS type wrappers и разрешена только штатная корневая ссылка папки saves, полученная от native level storage. Скрипт проверен на настоящем Rhino/Windows и в полном отдельном клиенте515: созданы совпадающие UUID мира и хранилища JourneyMap, получены12 здоровых состояний, мир сохранён, выход0. [Проверки и ограничения](tools/qa/journeymap-world-isolation-v2.json) раскрывают отдельную ошибочную проверку QA-агента о несуществующем глобальном marker; фактические native-наблюдения отделены от его сырого статуса. Переключение миров в полном клиенте этим не объявляется проверенным; архивирование поколений отдельно покрыто lifecycle/IO-тестами.

**Предыдущий состав530:** по явному решению пользователя полностью исключены Dandadan2.0 и Fairy Mine2.6.5 после расследования неправильных MP3-ресурсов. Их11 назначений клавиш удалены; прочие625 значений пресета сохранены. Общие зависимости остаются: Kleiders нужен CursedFate, GeckoLib и PlayerAnimator входят в BASE. Карточка555mod ID является точным вычитанием двух IDs из прежнего native-снимка557; новый игровой/сетевой PASS для530 ещё не заявляется. Старые миры могут потерять контент этих модов; бесшовный перенос не обещается.

**Исправление рецепта ковров Alchemistry:** собственные данные KubeJS сохраняют ID `alchemistry:dissolver/carpets` и меняют только тег входа `minecraft:carpets` на `minecraft:wool_carpets`. Количество, результаты, вероятности и остальные поля совпадают с авторским рецептом; JAR и глобальные теги не меняются. Реальная диагностика выявила пустой ингредиент именно этого рецепта, несмотря на ModernFix5.25.0. Новый data-only слой пока проверен исходниками и двумя штатными циклами восстановления; фактический повторный вход друга после него ещё предстоит. Прежняя native-приёмка ниже относится к родительским1918 файлам, без этого нового ресурса.

**Shooting Star1.5.1-demo / Rimulib1.2.1 / ModernFix5.25.0:** [чистый Root-прогон](tools/qa/native-source-acceptance.json) завершился штатно:26/26 startup scripts без ошибок,23 native-наблюдения мира,1175 Dissolver recipes в двух codec-режимах без сбоев. Осталось104ERROR/0FATAL, без новых product error families относительно прежней private Modified5ddb после раскрытых нормализаций; это не сравнение с Original и не ноль ошибок. Реальное исправление сетевого инцидента и вход друга пока не доказаны.

[Отдельный аудит ModernFix](tools/qa/modernfix-525-static.json) раскрывает14 авторских коммитов/18 файлов, а не однокомандный патч. В контролируемом синтетическом cache-тесте старый invalidate сохраняет пустую soft-reference и воспроизводит Alchemylib ctor44; явное применение официального clear-reference эффекта даёт stone×3. Это описание прежнего синтетического теста до запуска нового JAR. Позднейший native cache-invalidation04 с официальным ModernFix5.25.0 прошёл; причина пользовательского сетевого инцидента и устранение разрыва всё ещё не доказаны. Конфиги сохранены побайтно, performance options не отключались; временный standalone JDI-инструмент поставляется отдельно от контентных Forge-модов.

Текущая поставка переносит скачивание Ollama и всех пяти файлов модели Qwen3 на [собственный GitHub Release](https://github.com/MarkZamore/All-The-Mods-9-Modified/releases/tag/ai-ollama-v0.40.12-qwen3-1.7b-8f68893c), сохраняя точные байты runtime/модели и всех532 JAR. Нужен лаунчер с `local-ai-blob-urls-v1` (424 или новее). В pack-owned logging добавлена только запись четырёх штатных типов пойманных сетевых исключений в файл: это диагностика, а не исправление разрыва соединения; подробный поток пакетов не включён. [Отдельная проверка поставки](tools/qa/delivery-mirror-and-network-diagnostics.json) раскрывает три изменённых runtime-файла и сохраняет прежнюю native-приёмку привязанной к её исходному lock. Новый игровой прогон этим обновлением не заявляется. Лицензии и проверка всех публичных AI-файлов описаны [здесь](tools/ai-mirror/README.md).

**Контент532 прошёл полный native-прогон в родительской поставке: новый мир, более6минут здорового окна без запросов ввода, реальный русский AI и штатное сохранение/выход0.** Родительский lock `0096874596826ede2b8250dc04f70c8db58b8d886d61d958cf69870e34537285`:532 JAR/82requested/19NEWdependencies/18support. Закрытый журнал содержит899ERROR/0FATAL; остатки классифицированы в [отчёте532](tools/qa/final-runtime-532.md). [Root singleplayer acceptance](tools/qa/native-source-acceptance-before-ss151.json) принимает только точный532 content cohort: полный клиент/свежий технический мир/реальный русский AI/сохранение и выход0 с раскрытыми899ERROR. Этот receipt относится только к singleplayer532; более поздняя реальная Steam-сессия Original422 имеет отдельное доказательство и не превращает532 в выполненный тест двух клиентов. Падение533 ниже относится к отдельному историческому lock; не подменяет текущий результат. МиграцияSTATE/LEGACY принята отдельно; публичная поставка имеет собственную проверку CI/assets и этим source-native отчётом не устанавливается. Актуальное состояние отражают [workflow](https://github.com/MarkZamore/All-The-Mods-9-Modified/actions/workflows/publish.yml) и [pack-latest](https://github.com/MarkZamore/All-The-Mods-9-Modified/releases/tag/pack-latest). **Original ATM9 действительно подключилась через Steam на лаунчере422.** [Отдельный public-safe отчёт](tools/qa/original-steam-422.json) фиксирует совпавший Steam game bridge с обеих сторон, вход21:53:26, открытие мира гостем21:55:20 и сохранённые данные хоста до22:00:52 местного времени:446с после допуска/332с после открытия мира, дальнейшая выдача чанков и0disconnect/Connection-debug fault в этом окне. Пользователь подтвердил совместную игру. Это один успешный сеанс, а не доказательство причины или постоянного устранения прежнего intermittent CME/AIOOBE. В422 не применялись CME-обход или ослабление handshake-таймаутов. Для Modified подтверждена общая платформа Minecraft1.20.1/Forge47.4.0 и тот же выбираемый по loader/version Steam-транспорт; это source/code-аналогия, а не фактический двухклиентский runtime PASS её дополнительного контента. Эта граница доказательства не вводит новый обязательный игровой тест для завершения поставки.

## Состав и граница исходной ATM9

Текущий исходник содержит **514 JAR:431 BASE по членству +66 запрошенных дополнений +17 NEW dependencies**. Из BASE429 сохраняют исходные байты; два exact-hash исключения используют официальные AllTheLeaks1.1.4 и ModernFix5.25.0. Текущий состав закреплён в [active lock](tools/modified-lock.json), а исторические native-снимки ниже относятся только к своим ревизиям. Полная source-инвентаризация540 ID используется для проверки состава и памяти; игровой счётчик429 исключает только библиотеки/API. Подтверждённая Steam-сессия435 относится к текущим515 JAR; снятие диагностики и последующая правка JourneyMap не подменяются отдельным непроведённым игровым тестом.

Из 431 BASE-мода **429 JAR сохраняют исходные SHA256**. Два exact-hash исключения используют официальные авторские файлы: AllTheLeaks1.0.7 →1.1.4 и ModernFix5.24.4 →5.25.0; исходный авторский lock остаётся неизменным. Исходный Iron’s Spells 3.4.0.11 и Cupboard 2.7 не обновляются ради аддонов. Снимок 1 794 авторских payload-файлов и 452 исходных pack ID остаётся в [экспорте 7097953](https://www.curseforge.com/minecraft/modpacks/all-the-mods-9/files/7097953), `tools/upstream-lock.json` и `tools/base-mod-ids.json`; effective поставка раскрывает два точных BASE JAR исключения и текстовые overlays.

Эту ревизию нельзя описывать как «только добавленные моды» или обещать побайтную неизменность всех 1 794 файлов. По отдельному запросу локализованы 107 BASE-текстовых ресурсов квестов: их SHA/размеры закреплены в quest `baseReplacements`. Отдельный `baseJarOverrides` разрешает только точные официальные AllTheLeaks1.1.4 и ModernFix5.25.0 и не расширяет locale-guard на JAR. ID, задачи, награды и зависимости квестов не заменяются этим переводом.

Из514 JAR **512 файлов совпадают с соответствующими авторскими файлами**, включая официальный AllTheLeaks. Два NEW JAR — явно разрешённые производные: замороженный русский Verity6.0.0-ru.1 и Grotesque Steve1.4.2-quiet.1. Общий производный e4steam лаунчера описан отдельно. Собственные Forge-моды и Safety-framework не добавляются.

Карточка сохраняет исходные описание и обложку ATM9. Раздел **«Добавленные моды (Остальные в All The Mods 9)»** показывает68 добавленных самостоятельных модов и аддонов, распределённых в четыре категории. Alex’s Caves, Lucent и Simple Voice Chat являются самостоятельными модами, хотя первоначально скачаны как зависимости. Общая с ATM9 Render Patcher в добавлениях не повторяется. Встроенные API и настоящие библиотеки исключены из счётчика. Текущий `library/loaded-mods.json` проецирует539 pack ID из514 source JAR; это полная инвентаризация для проверки файлов и памяти, а не отображаемое число.

В лаунчере433 счётчик ATM9 равен361, Modified —429: разница68 совпадает с добавленными названиями, включая аддоны. Числа вычисляются по ID и ролям метаданных; полная native-инвентаризация и расчёт памяти сохраняются. `modCountScope=all` и категории принадлежат данным сборки, а не правилам C# по её имени. Контрольная база и пересчитываемые множества закреплены в `tools/library-presentation-policy.json`.

### Ручные дополнения (66)

Текущие файлы active lock; вид загрузки не определяет роль библиотеки в карточке.

| Проект | Версия | mod ID |
| --- | --- | --- |
| [Alex's Mobs](https://www.curseforge.com/minecraft/mc-mods/alexs-mobs) | `1.22.9` | `alexsmobs` |
| [Alone in the Dark](https://www.curseforge.com/minecraft/mc-mods/alone-in-the-dark) | `1.3.0` | `alone_in_the_dark` |
| [AmbientSounds](https://www.curseforge.com/minecraft/mc-mods/ambientsounds) | `6.3.11` | `ambientsounds` |
| [AmbiHorror](https://www.curseforge.com/minecraft/mc-mods/ambi-horror-ambience) | `1.0.0` | `ambihorror` |
| [Apex Arcana](https://www.curseforge.com/minecraft/mc-mods/apex-arcana-irons-spells-n-spellbooks-addon) | `1.4.0` | `grandsigil` |
| [Apollyon](https://www.curseforge.com/minecraft/mc-mods/apollyon) | `1.1.1` | `apollyon` |
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
| [Deep Dark: Regrowth](https://www.curseforge.com/minecraft/mc-mods/deep-dark-regrowth) | `1.2.6.1` | `deep_dark_regrowth` |
| [Distant Friends](https://www.curseforge.com/minecraft/mc-mods/distant-friends) | `0.5.6` | `distantfriends` |
| [Doomsday Arsenal](https://www.curseforge.com/minecraft/mc-mods/doomsday-arsenal) | `1.0.0` | `doomsday` |
| [Door Knocker (Horror)](https://www.curseforge.com/minecraft/mc-mods/door-knocker-horror) | `1.3` | `door_knocker` |
| [Draconic Evolution Render Patcher](https://www.curseforge.com/minecraft/mc-mods/draconic-evolution-render-patcher) | `1.3.0` | `derenderpatcher` |
| [Echoes of Nowhere](https://modrinth.com/mod/echoes-of-nowhere) | `1.0.1` | `echoes_of_nowhere` |
| [Enhanced Celestials](https://www.curseforge.com/minecraft/mc-mods/enhanced-celestials) | `5.0.0.4` | `enhancedcelestials` |
| [Eyes in the Darkness](https://www.curseforge.com/minecraft/mc-mods/eyes-in-the-darkness) | `1.3.10` | `eyesinthedarkness` |
| [From Another World](https://www.curseforge.com/minecraft/mc-mods/from-another-world) | `1.2A.1-forge` | `fromanotherworld` |
| [God Wand](https://www.curseforge.com/minecraft/mc-mods/god-wand) | `1.2.0` | `godwand` |
| [Grotesque Steve](https://saskez.gumroad.com/l/stevegrotesque) | `1.4.2-quiet.1` | `grotesque_steve` |
| [Horror Element Mod](https://www.curseforge.com/minecraft/mc-mods/horror-elements-mod) | `1.6.3` | `horror_element_mod` |
| [Liminality](https://www.curseforge.com/minecraft/mc-mods/liminal-reality) | `1.0.0` | `liminality` |
| [Meulti's Backrooms](https://www.curseforge.com/minecraft/mc-mods/meultis-backrooms) | `1.4.0` | `mbackrooms` |
| [Nostalgia](https://www.curseforge.com/minecraft/mc-mods/nostalgia-liminal-spaces) | `1.2.0` | `nostalgia` |
| [Nyctophobia](https://www.curseforge.com/minecraft/mc-mods/nyctophobia-forge) | `2.0.0+mc1.20.1` | `nyctophobia` |
| [Nyf's Spiders](https://www.curseforge.com/minecraft/mc-mods/nyfs-spiders) | `3.0.2` | `nyfsspiders` |
| [Orbital Railgun Forge](https://www.curseforge.com/minecraft/mc-mods/orbital-railgun-reforged) | `1.4.2` | `orbital_railgun` |
| [Rats](https://www.curseforge.com/minecraft/mc-mods/rats) | `1.20.1-8.1.3` | `rats` |
| [ReMorphed](https://www.curseforge.com/minecraft/mc-mods/remorphed) | `4.2` | `remorphed` |
| [Retail 3008](https://www.curseforge.com/minecraft/mc-mods/retail-3008) | `1.0.6` | `retail` |
| [Rolling Giant: Oldest View](https://www.curseforge.com/minecraft/mc-mods/rolling-giant-oldest-view) | `1.0.0` | `rolling_giant_oldest_view` |
| [Rotten Creatures](https://www.curseforge.com/minecraft/mc-mods/rotten-creatures) | `1.1.0` | `rottencreatures` |
| [SAO MOD](https://www.curseforge.com/minecraft/mc-mods/sword-art-online-expansion) | `1.0.0` | `sao_mod` |
| [Siren Head](https://www.curseforge.com/minecraft/mc-mods/siren-head-the-arrival) | `1.1.4` | `siren_head` |
| [Sons of Sins](https://www.curseforge.com/minecraft/mc-mods/sons-of-sins) | `2.2.1` | `sons_of_sins` |
| [Sound of Fear](https://www.curseforge.com/minecraft/mc-mods/sound-of-fear-horror-sounds) | `1.0.0` | `sound_of_fear` |
| [Sounds of the Forest](https://www.curseforge.com/minecraft/mc-mods/sounds-of-the-forest) | `1.0.2` | `sounds_of_the_forest` |
| [The After](https://modrinth.com/mod/the-after) | `0.1.2` | `the_after` |
| [The Backwoods](https://www.curseforge.com/minecraft/mc-mods/backwoods) | `1.6.0` | `the_backwoods` |
| [The End of Herobrine](https://www.curseforge.com/minecraft/mc-mods/endofherobrine) | `1.20.1-1.0.8.2` | `endofherobrine` |
| [The Final Goatman](https://www.curseforge.com/minecraft/mc-mods/the-final-goatman) | `4.3.0` | `goatman` |
| [The Graveyard](https://www.curseforge.com/minecraft/mc-mods/the-graveyard-forge) | `4.0.1+mc1.20.1` | `graveyard` |
| [The Hordes](https://www.curseforge.com/minecraft/mc-mods/the-hordes) | `1.6.3g` | `hordes` |
| [The Midnight](https://www.curseforge.com/minecraft/mc-mods/the-midnight) | `0.6.7` | `midnight` |
| [The Mimicer](https://www.curseforge.com/minecraft/mc-mods/the-mimicer) | `1.7.0` | `themimic_er` |
| [The One Who Watches](https://www.curseforge.com/minecraft/mc-mods/the-one-who-watches) | `1.4.4` | `the_one_who_watches` |
| [The Onlooker](https://www.curseforge.com/minecraft/mc-mods/the-onlooker) | `4.7.1-alpha` | `anta` |
| [The Shooting Star (Demo)](https://www.curseforge.com/minecraft/mc-mods/the-shooting-star-demo) | `1.5.1-demo` | `shooting_star_demo` |
| [The Singing Villager](https://www.curseforge.com/minecraft/mc-mods/the-crying-villager) | `3.5.0` | `singing_villagers` |
| [True Darkness](https://www.curseforge.com/minecraft/mc-mods/true-darkness-forge-updated-fork) | `2.0.103` | `darkness` |
| [Type 95](https://www.curseforge.com/minecraft/mc-mods/type-95-sniper-rifle) | `1.0.2+forge-1.20.1` | `tanya_demo` |
| [Ultimate Elemental Swords](https://www.curseforge.com/minecraft/mc-mods/ultimate-elemental-swords) | `1.0.0-1.20.1` | `ultimate_elemental_swords` |
| [Verity JE](https://www.curseforge.com/minecraft/mc-mods/verity-je) | `6.0.0-ru.1` | `verity` |
| [Weather, Storms & Tornadoes](https://www.curseforge.com/minecraft/mc-mods/weather-storms-tornadoes) | `1.20.1-2.8.3` | `weather2` |
| [Whisperwoods](https://www.curseforge.com/minecraft/mc-mods/whisperwoods) | `1.20.1-2.1.2` | `whisperwoods` |
| [Woodwalkers](https://www.curseforge.com/minecraft/mc-mods/woodwalkers) | `5.8.13` | `walkers` |
| [Zombie Awareness](https://www.curseforge.com/minecraft/mc-mods/zombie-awareness) | `1.20.1-1.13.1` | `zombieawareness` |
| [Zombie Nightmare Expansions](https://www.curseforge.com/minecraft/mc-mods/zoniex) | `1.2.1` | `zoniex` |

### Добавленные зависимости (17)

Текущие файлы active lock; вид загрузки не определяет роль библиотеки в карточке.

| Проект | Версия | mod ID |
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
| [lucent](https://www.curseforge.com/minecraft/mc-mods/lucent) | `1.5.5` | `lucent` |
| [Pehkui](https://www.curseforge.com/minecraft/mc-mods/pehkui) | `3.8.2+1.20.1-forge` | `pehkui` |
| [Photon](https://www.curseforge.com/minecraft/mc-mods/photon) | `1.1.17` | `photon` |
| [platform](https://www.curseforge.com/minecraft/mc-mods/platform) | `1.4.2` | `platform` |
| [rimulib](https://www.curseforge.com/minecraft/mc-mods/rimulib) | `1.2.1` | `rimulib` |
| [simple-voice-chat](https://www.curseforge.com/minecraft/mc-mods/simple-voice-chat) | `1.20.1-2.6.22` | `voicechat, voicechat_api` |
| [VillagersTradingPlus](https://www.curseforge.com/minecraft/mc-mods/villagerstradingplus) | `1.1.1+mc1.20.1` | `villagertradingplus` |
| [YetAnotherConfigLib](https://www.curseforge.com/minecraft/mc-mods/yacl) | `3.6.6+1.20.1-forge` | `yet_another_config_lib_v3` |

KuroLib0.6 и Voice Chat Recording2.1 удалены после исключения их единственных потребителей; самостоятельный Simple Voice Chat сохранён. TravelOptics исключён вместе с обязательным аддоном Apex Tides по решению пользователя; базовый Iron’s Spells 3.4.0.11 не менялся.

AzureLib обновлён адресно как **NEW-зависимость**, а не базовая библиотека:

| Версия AzureLib | SHA256 | Статус |
| --- | --- | --- |
| 1.0.34 | `9aca62c9caf1266617d2734e49204b1b2fe119ca58b0579dde47fb1c8f39a206` | Прежний кандидат, не активен |
| 2.0.41 | `25a95a495c586b72f80bf8b65fd1892b2e21a2d9d2e072808e663aa0938401f6` | Активный официальный выпуск |

Историческая проверка: родной загрузчик 2.0.41 обработал неизменённую геометрию уже исключённого HSR Phainon1.2.3 Dawnmaker формата 1.21.110; проверены 190 прямых обращений From Another World к API AzureLib. Модели не переписывались, native format guards не обходились. Эти проверки не являются PASS полного клиента или обещанием переноса старых миров без потерь registry ID.

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
| [Kimetsunoyaiba](https://www.curseforge.com/minecraft/mc-mods/demonslayer) | Голубая стрелка и пять квадратов HUD сопоставлены с OverlayCooldownTimeOverlay по точным пиксельным якорям. Пользователь выбрал удаление Kimetsu; Jujutsu Craft позднее также удалён отдельным решением пользователя. |
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
| [Soul Eater](https://www.curseforge.com/minecraft/mc-mods/soul-eater-mc) | Безусловно исключён по последнему решению пользователя, независимо от будущего уточнения причин. После NPE очереди ver35/declared1.25.11 удалены JAR/четыре управления/три строки руководства. Автоматически не возвращается; повторное добавление требует нового явного запроса пользователя. |

Это история последних решений, а не неактивные JAR внутри active files. Все перечисленные проекты отсутствуют в выбранном составе. [Десять новых exact-SHA исключений](tools/approved-removals-20261030.json) отделены от активного lock; все они NEW, ни один BASE JAR не удалён. По проверенным declared mandatory edges внешних обязательных зависимых нет; Apex Tides и TravelOptics удалены вместе. Jujutsu Craft, Grotesque Steve, Citadel, Alex’s Caves, Alex’s Mobs и Rats сохранены. Прежние отменённые варианты не возвращаются автоматически; отсутствие удалённых JAR само по себе не является runtime PASS нового набора.

## Адресные изменения AllTheLeaks и Grotesque Steve

AllTheLeaks остаётся BASE по членству, но используется [официальная Forge 1.20.1 версия 1.1.4](https://www.curseforge.com/minecraft/mc-mods/alltheleaks/files/9188826), не собственная модификация его JAR.

| Файл | SHA256 | Размер |
| --- | --- | ---: |
| Авторский BASE `alltheleaks-1.0.7+1.20.1-forge.jar` | `9df833a1e3fb0cc8e4fe43fd2637d5d7745edfe38356a13baaa69457982d4de6` | 1 173 400 |
| Закреплённый официальный `alltheleaks-1.1.4+1.20.1-forge.jar` | `fb72063a7d17df97740d24355444ef2f95eab97728e1256c639bb432c61b7716` | 1 274 164 |

Пользователь выбрал сохранять совместимый pin1.1.4 и при следующих обновлениях авторской ATM9. Новый author import перепривязывает `original` по реальному mod ID и точным новым SHA/размеру, но не заменяет наш pin автоматически даже более новой авторской версией. Изменение этого решения — отдельный review. Пропавшее ownership отклоняется; неизвестные BASE/JAR не перезаписываются, NEW-зависимости не превращаются в BASE. Подробности — в [owner workflow](tools/atm9_quest_updates/OWNER_WORKFLOW.md).

[Полный статический аудит AllTheLeaks](tools/qa/alltheleaks-1.1.4-static.json) проверил весь JAR, вложенные библиотеки и изменённые пути. Новый version guard исключает Citadel2.6.3 до попытки обращаться к уже отсутствующей старой static map. Сам Citadel и его зависимые моды сохранены: утечка, потеря FPS или crash от того прежнего предупреждения не доказаны. Обновление AllTheLeaks также меняет capability/cache/shutdown-поведение; это не обещание исправить Blood Magic или все утечки, а прежний полный клиент531 и штатный выход проверены отдельно в историческом runtime-отчёте; долговременные RAM/FPS-показатели не измерены.

Grotesque Steve сохранён как **1.4.2-quiet.1** по отдельному разрешению: отключены два callback входа с английской action-bar подсказкой, звуками wind/fart и автоматической выдачей книги. В `manualgiver.mcfunction` исправлен один недопустимый начальный `/`; содержимое книги, другие применения звуков, штатная функция `grotesque_steve:give` и advancement-ресурсы сохранены. Четыре ZIP-записи изменены, 2 495 остальных побайтно прежние; новые классы не добавлены. Это адресная производная пользовательской редакции, не новый официальный релиз и не заявленное исправление всех игровых механизмов.

Оригинал Gumroad1.4.2, SHA256 `7edde5b1506a69a725412769525ba16122b1dd4c38e35f3edc5c015eef3a6f63`, хранится в Git как source-only `tools/GrotesqueSteve/source/grotesque_steve-1.4.2-forge-1.20.1.jar`, не второй активный мод. [Точный patcher](tools/grotesque_steve_quiet.py) восстанавливает производный SHA256 `ffa7df6fb07e54217757436b566fa0073b460c5fa4b695cfd2d4d40692208052` локально без загрузки Gumroad или подмены бесплатной редакцией. Оригинал и tool закреплены в transformation; их отсутствие/иные байты приводят к отказу до BASE-записи.

[Подготовка Grotesque quiet](tools/GrotesqueSteve/preparation-report.json) включает 13 положительных/отрицательных тестов, повторное точное воспроизведение и Java17 `-Xverify:all` с настоящими Forge/Minecraft классами. Standalone-проверка callback и command syntax не выдаётся за вход в мир или проверку всей item-registry. Независимая сверка ZIP и структуры классов подтвердила четыре изменённые записи и сохранность всех байтов вне Code двух callback. Границы описаны в [source-only руководстве](tools/GrotesqueSteve/README.md); прежний полный клиент531 загрузил новый мир и завершился штатно. Прежних function-ошибок Grotesque в том закрытом логе нет; все способности этим не объявлены проверенными.

## Добавления после проверенного состава531

**Weather, Storms & Tornadoes (Weather2)2.8.3** — неизменённый официальный JAR Corosus, SHA256 `5eb828f93b2eb370d7f38ad1893739caf7655f32d58dbbdaabae6075ede635db`. Уже установленный NEW CoroUtil1.3.7 удовлетворяет зависимости; BASE и общие библиотеки ради него не обновлялись. [Статический аудит](tools/qa/weather2-2.8.3-static.json) проверил release/source, зависимости и конкретные render call sites; это не Mixin/runtime или испытание всех погодных механик.

Авторский захват блоков торнадо включён и сохранён; опциональное Forge BreakEvent по умолчанию выключено. Отложенный tornado terrain queue, отдельные fire/snow/sand записи не дают подтверждённой FTB claim-защиты; modded inventories не покрываются общей гарантией. Авторский Weather Deflector — игровая механика, не замена claim-интеграции. Пользователь запретил собственный Safety/framework: он не добавлен, механики и defaults не упрощены скрыто. Это явное ограничение защиты мира, не обещание безопасной погоды на чужом участке.

**Draconic Evolution Render Patcher1.3.0** — официальный сторонний клиентский beta-мод Yrley, SHA256 `a59d110b3a0f8ade8c6c4bd9e7c6d6cf265f84391bce89de87ef92de5498d4ef`, а не наш переписанный JAR. [Exact-native статический отчёт](tools/qa/derenderpatcher-1.3.0-static.json) и [sites](tools/qa/derenderpatcher-1.3.0-sites.json) проверили21 target, authored MCP/SRG alternatives и69 внешних ссылок. Базовые Draconic Evolution/Brandon’s Core/CodeChickenLib и Mekalus/Embeddium сохранены. Мод меняет маршруты render targets/private buffers, сохраняя авторские3D модели и assets;2D fallback, собственные quality/distance caps и обходы shader guards не добавляются. Его штатное beta chat-уведомление сохранено.

Клиентский Render Patcher не предназначен для dedicated-server mods; пользовательский встроенный LAN-host остаётся клиентом. Отдельный in-game/визуальный тест этого DE-исправления пользователь разрешил не проводить: это WAIVED, не shader-output/визуальный PASS. Полный запуск нового состава всё равно имеет собственную общую проверку. Оба новых мода остаются NEW при будущих обновлениях JAR и требуют обычного нового compatibility/Safety-review; их добавление не расширяет точечный BASE-override AllTheLeaks.

### Верхнее предупреждение памяти в самой сборке

`kubejs/client_scripts/lanmc_memory_warning_policy.js`, SHA256 `68b42fde0072ce3f366605a7619931cb6388575230ca7a910c23580b58cbaeab`, через native Memory Settings5.9 API меняет только загруженный `disableWarnings=true` до initial game-menu check. Это убирает запрошенную верхнюю панель при heap выше авторских14336MiB (14GiB), сохраняя выбранную игроком память. [Native API/Rhino proof](tools/client-policy/native-proof.json) подтвердил сохранение остальных полей и побайтного личного JSON, повторяемость и точные классы Memory Settings/Cupboard/Rhino. Это standalone native proof, не приёмка меню нового532.

Скрипт не пишет `memorysettings.json`, не вводит предел heap/рендера и не подавляет общий ERROR-журнал. Более ранний low-heap Swing-диалог и constructor log находятся до client scripts и не выключаются этой политикой. Исполнение принадлежит KubeJS сборки, не писателю конфигов в лаунчере.

После следующего author import [source-owned workflow](tools/client-policy/README.md) сначала восстанавливает hash-pinned шаблон `prepare.py --templates-only --apply` до strict support preflight/restore, затем после появления native JAR выполняет `prepare.py --apply` с проверкой действительных public API. Первый этап не выдаётся за API PASS при отсутствующих модах; конфликтующий скрипт отклоняется, изменившийся API требует review. Личные настройки и авторские JAR не переписываются, скрытого скачивания latest нет.

## Пресет управления

Общая раскладка применяется отдельной кнопкой лаунчера и меняет только клавиши. P нужно удерживать для разговора с Verity. Карта M, рюкзак B, квесты на Ё/grave accent, Curios G и обычные WASD сохранены. Настроены основные меню/колёса/циклы/превращения. Назначения исключённых модов убраны. Полная таблица — [руководство по управлению](launcher/controls-guide.md).

Для некоторых боевых веток нужны собственные назначения в меню Minecraft: классические способности Cursed Fate 1–7, четыре Stellar Remote из Shooting Star, а также Laser Mask. Четыре свойства палочки Crystalix также оставлены для выбора кнопок игроком. Это прямые действия без настроенной здесь замены; они не выдаются за полностью управляемые через другое меню. Родные кнопки и остальные неназначенные группы перечислены в руководстве и `tools/keybinds/stock.json`.

Текущий source-пресет содержит554 имени:146 назначены,408 свободны;60 независимых действий мира. Удалены только назначения исключённых модов, остальные значения сохранены. Текущие540mod ID и namespace пресета выведены из исторического native-снимка; нового применения/перезапуска или физического ввода этим обновлением не проверено. Пресет остаётся необязательным и не меняет язык, графику, дальности, голос или микрофон.

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

В этих изменениях используется существующий авторский KubeJS и native API. Скрытого mod-specific писателя Verity TOML в C# нет. В diag12 и отдельно в историческом финальном мире531 измерен настоящий игровой запрос этого маршрута: авторский обработчик получил ответ локального AI и вывел его по-русски. Границы renderer/GL и оставшиеся ERROR того состава описаны в историческом runtime-отчёте; текущий532 имеет отдельный закрытый отчёт ниже.

## Community resource layer Verity JE-RU

По запросу добавлен неизменённый официальный архив сообщества [PAGODI: Verity JE Russian Translation](https://www.curseforge.com/minecraft/texture-packs/verity-je-russian-translation-rusifikator/files/9375140),383380байт, SHA256 `de15104f3ea81fe2ba50116c65f3d74e29692cefbc6ef68192244a7c64740b68`. Он хранится как `kubejs/assets/Verity-JE-RU.zip`, а не новый JAR. Уже установленный KubeJS2001.6.5 сканирует top-level ZIP в assets через свой существующий native resource provider; дополнительных activation JS, выбора ресурспака в личных options и правил лаунчера нет.

[Статическая проверка](tools/qa/verity-je-ru-resourcepack-static.json) установила только три записи:29 RU keys, pack metadata format15 и иконка. Это частичный языковой слой:19 ключей перекрывают прежний RU JAR (13 значений отличаются),10 добавлены,2 прежних ключа сохраняются; совокупность31ключ. Часть новых aliases не доказывает текущий UI caller. Авторский слой меняет некоторые локализованные имена с Verity на «Истина»; Java-coded реплики, русские STT/TTS и полный одобренный `verity-6.0.0-ru.1.jar` SHA`45fc05ee…b85d8` не переписываются. Внешний архив не заменяет этот JAR и не русифицирует Java-код сам.

[Standalone native proof](tools/qa/verity-je-ru-resourcepack-native.json) с реальными FilePackResources/metadata serializer/ClientLanguage подтвердил format15,29 ресурсных значений и String.format, сохранение двух RU fallback и неизменный EN. Полный KubeJS injection lifecycle/пиксели этим standalone-тестом не проверены; последующий общий runtime532 отдельно подтвердил native resource winner, но не пиксели/все UI callers. Дополнительную игру только ради этого resource-only слоя пользователь отменил. Личный порядок selected packs не переписывается; известная ZIP insertion boundary не даёт универсальной гарантии приоритета личных directory packs.

Во время общего runtime532, проводимого для проверки удаления Soul Eater, read-only native ResourceManager в меню и мире подтвердил winner **Verity-JE-RU.zip** для `verity:lang/ru_ru.json`:1938байт/SHA`e67fc9015cc3d0c011a09bca50d56f2a0dce7a0535ff8399a69f136cb7e97328`. Это точечное подтверждение действительного ресурсного источника, не пиксели/все UI callers и не дополнительная игра только ради ZIP.

Для будущего author import архив остаётся pinned source/support-файлом: его надо сохранить в Git до strict restore; missing support отклоняется, restore не скачивает его скрыто. При обновлении KubeJS/provider отдельно перепроверяется этот native путь. В ZIP нет классов, scripts, server data, звуков, shaders или world textures: новых world/inventory paths и Safety-модуля не появляется. Лицензия/происхождение и точные записи сохранены в static report; архив не изменён.

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

В diag12 на диагностической сборке исходников 420 настоящий игровой chat прошёл через авторский обработчик и переносимый Ollama: `/api/chat` вернул HTTP 200 за 37,65 с, ответ был русским. После завершения приватного CLI-координатора тот же мир/backend продолжали работать 48,37 с; штатный выход из игры дал код 0 и завершил принадлежащие запуску Ollama/llama-server, endpoint закрылся. Закрытие полного GUI-лаунчера, физический ввод и игровой микрофон остаются отдельными непроведёнными проверками. Это исторический diag12; текущие результаты532 и границы приёмки приведены ниже и в `TESTING-STATUS.md`.

## Что перенесено из лаунчера и что осталось

[Общий актуальный отчёт для шести сборок](tools/qa/pack-launcher-responsibilities.md) перечисляет pack-owned данные и конкретные оставшиеся generic-launcher исключения; [source-аудит](tools/qa/pack-launcher-responsibilities-audit.json) отдельно фиксирует descriptors и код421.

Фиксированные настройки и совместимость принадлежат исходнику сборки: community Verity resource ZIP, recipe AI, четыре AI-поля, native Verity policy/tag, Rats, предупреждения Meulti и верхнего порога Memory Settings, русские квесты, `config/log4j2.xml` и выбирающий его `launcher/jvm-args.txt`. Логирование сохраняет ERROR; отдельный полный debug.log не создаётся, а уровни/ротация теперь являются явными данными сборки.

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
| Текущие пользовательские уведомления | Содержимое и срок жизни возникают в работающем лаунчере/процессе; это не статический ресурс мода. Прежний полный native-клиент531 проверен отдельно; интерактивный маршрут GUI-уведомлений не проверялся. |
| Заголовок окна из имени локальной папки | Сохраняется прежний явный пользовательский контракт. Локальное имя заранее неизвестно опубликованной сборке; единая native-замена на всех платформах без добавления собственных модов не проверена. Это отдельная UI-задача, не необходимость идентичности. |

Это конкретный перечень оставшегося поведения, а не общее исключение для всех hooks или утверждение принципиальной невозможности будущего native-порта.

### Общий Steam: UI уже изменён в готовом артефакте

[Опубликованный профиль `native-lan-ui-v1`](https://github.com/MarkZamore/e4steam/releases/tag/native-lan-ui-v1) покрывает все 19 выбранных loader/MC-артефактов. В шести современных e4steam 0.3.4 заранее удалены дополнительная кнопка LAN Settings и три перенаправления штатных экранов в промежуточную форму. Steam Invite Friends, аутентификация и транспорт сохранены. У 13 старых 0.3.2 этого окна уже нет, поэтому их авторские байты/исторические URL не менялись.

Каждый современный производный JAR меняет только `PauseScreenMixin.class`, `e4steam.mixins.json` и добавляет downstream NOTICE. Все остальные распакованные записи, включая сетевые классы, metadata, native-библиотеки и лицензии, совпадают с авторскими. In-JAR версия 0.3.4 сохранена для API-совместимости; суффикс `-lanmc-native-ui.1`, DeliveryTag и SHA отдельно обозначают производный артефакт. Оригинальные релизы автора не перезаписаны.

Для текущей Forge-платформы используется `e4steam-forge-mc1.18.2-1.20.2-v0.3.4-lanmc-native-ui.1.jar`: 3 801 104 байта, SHA256 `68ba6bdce76868e2cb43359a13416dfa1b011c628c13b6c4266b653c765b5c40`. Это общий сетевой компонент, не один из 431 базовых или 82 вручную запрошенных JAR.

Исходный cross-version `pack.mcmeta` этого Forge JAR сохраняет формат 18. Для обычного мода Forge 47 использует native `mod_resources` / `DelegatingPackResources` с текущим форматом 15; это отдельно проверено настоящим MC 1.20.1 serializer. Использование самого JAR как обычного ресурспака не эквивалентно этому loader-пути. Проверка иных версий provider не объявляется выполненной только по сохранению metadata.

Linux/Windows source CI, 18 packaging-тестов, независимое сравнение методов приглашения, 20/20 сравнений файлов двух OS и загрузка всех 19 публичных вариантов подтвердили поставку. Это не PASS GUI/Steam двух клиентов всех пяти карточек. В native MC 1.20.1 уже опубликованный мир выбирает `menu.playerReporting`; новый реальный клиентский UI/LAN-маршрут проверяется отдельно. На версиях без native reporting собственный экран жалоб не изобретается.

## Текущий532: полный закрытый native-прогон

[Отчёт532](tools/qa/final-runtime-532.md) и [точный JSON](tools/qa/final-runtime-532.json) относятся только к lock `0096874596826ede2b8250dc04f70c8db58b8d886d61d958cf69870e34537285`. Свежий технический мир был создан для532, без переиспользования мира failed533. В меню/мире нативно прочитаны настоящий русский язык, loaded Memory Settings `disableWarnings=true`,560ModList/557pack ID и638Options/652registry. Source-пресет содержит638имён/184назначенных/454свободных/83независимых действия.

Новый мир подтверждён01.11.2026 14:44:56.594UTC. До первого give/AI-запроса получены393,470с непрерывного здорового мира,122здоровых наблюдения/0плохих/0пауз и0запросов ввода QA-harness. Это не мониторинг физического ввода. Замороженный префикс имеет108ERROR/0FATAL. Give действительно выполнен14:51:33.367UTC, chat —14:51:56.106UTC. Собственный переносимый backend вернул `/api/chat` HTTP200 за41,8с около14:52:39UTC; нативно наблюдалась русская реплика, отличная от статического приветствия. Ответ оказался вопросом/эхом «Верити, как тебя зовут?»: работа модели доказана, правильность ответа о собственном имени — нет. Ответ наблюдался около14:52:39UTC, последнее здоровое native-наблюдение —14:55:24.192UTC; более длинный интервал после ответа не заявляется.

Штатный выход завершился14:55:39.911UTC сcode0 без forced kill:82сообщения сохранения измерений, AllDimensionsSaved и0crash reports. Принадлежащие запуску Java/Ollama остановились, локальный endpoint закрылся. Все1915SOURCE-файлов сохранили исходные SHA; все532runtime content JAR +E4 и community ZIP совпали. Это не утверждение равенства всехsource/runtimeфайлов: приватный default-профиль QA отличается ровно языком/паузой (`ru_ru`/`pauseOnLostFocus=false`), другие101строка и controls seed сохранены. Source и личные миры не менялись. Все638 фактических native mappings сохранились после выхода; source-предустановка не применялась, её bindings/физический input/restart этим не проверены.

Полный журнал: **899ERROR/0FATAL =108префикс +790Verity discovery +1Grand Sigil после запроса выхода**. По происхождению:6NEW metadata/network +87общих/source-attributed фоновых +14намеренных авторских диагностик +2BASE BloodMagic/Curios с недоказанным конкретным NEW-инициатором +790Verity. Шесть собственных заголовков:AzureLib2, Celestisynth1, MeultiBackrooms1, YACL1, CraftedCore1. Grand Sigil — ещё3NEW-owned intentional watchdog-заголовка (2startup/1shutdown), они входят в14 вместе с11BASE JEI progress timers, а не спрятаны в87общих. Их наличие само по себе не устанавливает причину задержек кадров.

Verity инициирует790заголовков Forge:395parent-class сообщений и395handler diagnostics тех же встроенных non-Event классов, что в531; точный JAR не менялся. Прежний native transformer/source proof возвращает unchanged ClassNode: доказательства395потерянных handlers нет. Полная фактическая AI-связь с русским ответом выполнена; все способности и семантическое качество этим не доказаны. BloodMagic/Curios2 остались с точными прежними сигнатурами; определённый NEW-виновник не установлен. Placebo/Iron gear-set и OpenAL в этом окне отсутствовали — это не заявление об исправлении или всеобщем отсутствии.

Новой fault-family сверх исторических exact/source-attributed семейств не выявлено; JEI elapsed values сохранены как наблюдались. GL-debug содержит44INFO (2shader-link/42uniform): семьи совпали с current Original при нормализации native program handles. Weather2, официальный Render Patcher и pack RAM-policy не дали собственных ERROR/FATAL в этом окне. Сравнение не является visual-quality/all-mechanics PASS; общие авторские ERROR не объявляются автоматически намеренными или безвредными. Логи не подавлялись, эффекты/шейдеры/анимации и дальности не менялись.

[Root singleplayer acceptance](tools/qa/native-source-acceptance-before-ss151.json) принимает только точный532 content cohort: полный клиент/свежий технический мир/реальный русский AI/сохранение и выход0 с раскрытыми899ERROR. Этот receipt относится только к singleplayer532; более поздняя реальная Steam-сессия Original422 имеет отдельное доказательство и не превращает532 в выполненный тест двух клиентов. Свежий технический мир не доказывает без потерь перенос личного мира/старых registry ID. STATE/LEGACY migration PASS имеет отдельные доказательства; публичная поставка проверяется отдельно. Для Modified отдельные два клиента, Steam/LAN UI, выбранные скины, первое лицо при превращениях, все способности и визуальная оценка не объявлены выполненными; **Original ATM9 действительно подключилась через Steam на лаунчере422.** [Отдельный public-safe отчёт](tools/qa/original-steam-422.json) фиксирует совпавший Steam game bridge с обеих сторон, вход21:53:26, открытие мира гостем21:55:20 и сохранённые данные хоста до22:00:52 местного времени:446с после допуска/332с после открытия мира, дальнейшая выдача чанков и0disconnect/Connection-debug fault в этом окне. Пользователь подтвердил совместную игру. Это один успешный сеанс, а не доказательство причины или постоянного устранения прежнего intermittent CME/AIOOBE. В422 не применялись CME-обход или ослабление handshake-таймаутов. Для Modified подтверждена общая платформа Minecraft1.20.1/Forge47.4.0 и тот же выбираемый по loader/version Steam-транспорт; это source/code-аналогия, а не фактический двухклиентский runtime PASS её дополнительного контента. Эта граница доказательства не вводит новый обязательный игровой тест для завершения поставки.

## Реальная Steam-сессия Original422 и границы переноса результата

**Original ATM9 действительно подключилась через Steam на лаунчере422.** [Отдельный public-safe отчёт](tools/qa/original-steam-422.json) фиксирует совпавший Steam game bridge с обеих сторон, вход21:53:26, открытие мира гостем21:55:20 и сохранённые данные хоста до22:00:52 местного времени:446с после допуска/332с после открытия мира, дальнейшая выдача чанков и0disconnect/Connection-debug fault в этом окне. Пользователь подтвердил совместную игру. Это один успешный сеанс, а не доказательство причины или постоянного устранения прежнего intermittent CME/AIOOBE. В422 не применялись CME-обход или ослабление handshake-таймаутов. Для Modified подтверждена общая платформа Minecraft1.20.1/Forge47.4.0 и тот же выбираемый по loader/version Steam-транспорт; это source/code-аналогия, а не фактический двухклиентский runtime PASS её дополнительного контента. Эта граница доказательства не вводит новый обязательный игровой тест для завершения поставки.

Лаунчер422 опубликован из [78a6eb55](https://github.com/MarkZamore/LANMinecraft/commit/78a6eb55e2c895d8b301713b85efdc5084651ae3), [CI41327272016](https://github.com/MarkZamore/LANMinecraft/actions/runs/41327272016) успешен:513 Release-проверок/297 adapter-проверок без пропусков. Реальный публичный EXE SHA`9a041a4a0c612db9bbaa195a7b938b3d5d1f61a2b86a9d5c5780df60e8fbc624` и delta421→422 проверены;125native targets охватывают6поддержанных профилей общего Steam-only автосписка/названия мира/имени из лаунчера. Указанный byte-verifier не запускал EXE, но последующий отдельный Original-сеанс уже наблюдал обе стороны на422. UI-исправление доказано для пустого диапазона Track; ограниченная числовая диагностика добавлена для прежнего live overflow-симптома, его полный визуальный фикс этим не заявлен. После422 пользователь вновь подтвердил отсутствие прокрутки/индикатора каталога и невидимый thumb подробностей. Числовой live-снимок установил oversized RootGrid770×1579 при clip770×482, catalogue viewport1519 при extent669/range0 и положение scrollbar x798 за правой clip-границей794. Это доказанный layout/clipping-дефект;423 готовится отдельно, исправление ещё не принято. Публикация контента532 не требует ожидания этой будущей UI-ревизии, но полный результат по пользовательскому UI-запросу не объявлен выполненным.

Пользователь отдельно подтвердил правильные выбранные в лаунчере скины для себя и пира в текущем мире Original. Это user-reported визуальный факт, не автоматическая оценка изображения и не визуальная приёмка Modified. Замороженный log-only Steam-report с `skinOrInventoryVisualPassClaimed:false` не переписывается: подтверждение пользователя последовало отдельно.

**Миграция532 прошла STATE и LEGACY:** все6отчётов основного обновления/history/retired-artifacts имеют PASS, aggregate SHA`0fe0a47f461f55849cf31abd73977ab6c80f397e0ba1d2d7f832ad46e9c4cfa4`. Подтверждены532JAR/1915runtime-файлов, восстановление прерванного скачивания/применения,5синтетических sentinel, exact-SHA удаление известных старых файлов и сохранение изменённых конфигов, повтор с0payload. Исходный reference3938файлов/4000295544байт совпал до/после; личные миры не читались/не копировались. Это отдельная fixture-миграция frozen Debug421 reference, не запуск публичного422 EXE или перенос личного мира без потерь.

У Original после родительского465 опубликован [диагностический source dba4b58](https://github.com/MarkZamore/All-The-Mods-9/commit/dba4b58c162bb06591bba3b00618a1d825095e6d), [CI41322238677](https://github.com/MarkZamore/All-The-Mods-9/actions/runs/41322238677). Единственная runtime-дельта — pack-owned `config/log4j2.xml`: ограниченный native Connection DEBUG capture в файл; Root/Console/прочие настройки не изменены. Публичные config ZIP/library/manifest и1805source-файлов проверены. Последующий Original422 Steam-сеанс наблюдал Connection DEBUG на обеих сторонах; диагностический конфиг сам по себе не является причиной успешного подключения или доказанным исправлением прежнего сбоя. Прежний title-report c598 относится к родительскому runtime и не переименован в этот диагностический состав.

## Историческое падение533 и последующее удаление Soul Eater

[Полный отчёт failed533](tools/qa/failed-runtime-533.md) и [JSON](tools/qa/failed-runtime-533.json) относятся к lock `36859e8f9b67789407e976436bb99070428b2a53cd6b75831861f3ffee145265`, который [архивирован](tools/qa/modified-lock-533-failed.json) вместе с [native ModList533](tools/qa/loaded-mods-533-failed.json). Этот состав не был принят. Run02 дал335,147с/103здоровых наблюдения без ввода/паузы, затем упал в Soul Eater на отложенном `FreeOnEntityTickUpdateProcedure.lambda$execute$9:190` через null Entity.getX; процесс завершился с-1. Прямой владелец ошибки — NEW Soul Eater ver35/declared1.25.11, SHA`ae94fb51f42ae969627f3ab25715bcef7e7080d02c900e347e42a73dbe6f2536`.

Полный run02 содержит108ERROR/2FATAL, префикс —103/0. Поздние5ERROR: два ранее известных Placebo/Iron gear fallback до выдачи предмета и три отчёта одного Soul Eater crash; обаFATAL принадлежат ему же. Нативный give call вернулся14:14:15.768UTC, серверный эффект не проверялся; crash14:14:44UTC. Chat-файл создан14:14:49UTC после crash и не выполнился: actual chat/API/AI-response/790-Verity route отсутствуют. LLM inference не мог быть причиной; один ранний give и Weather listener в списке EventBus не доказывают инициатора null reference.

В run02 классифицированы6 известных NEW metadata/network сообщений,81 общих или source-attributed фоновых,14 намеренных диагностик,4BASE сообщения с неизвестным NEW-инициатором и3 Soul Eater crash reports. AzureLib2, Celestisynth1, MeultiBackrooms1, YACL1 и CraftedCore1 сохраняются как известные собственные заголовки новых компонентов; BloodMagic/Curios2 иPlacebo2 не получили доказанного NEW-виновника. Для Weather2/RenderPatcher/RAM-policy собственных ERROR/FATAL в том окне не найдено; это не все mechanics/visual PASS. OpenAL в обоих533 окнах отсутствовал, что не доказывает исправление; shader-link/uniform семьи совпадали с Original при нормализации native program handles.

После этого пользователь отдельно закрепил безусловное исключение Soul Eater, даже если будущий разбор уточнит его роль. Новый532 убирает точный JAR/четыре keys/три строки guide; автоматического возврата нет, повторное добавление требует нового явного запроса. Отдельный полный прогон532 завершён и раскрыт выше; старые registry ID/world content удалённого мода не обещаются сохранёнными.

## Историческая точность языка и непрерывного окна QA533

При свежем первом запуске run01 авторский DefaultSettings заменил заранее запрошенные технические `ru_ru`/`pauseOnLostFocus=false` в Original и Modified. После выхода Original фактически сохранил `en_us` и `pauseOnLostFocus=true`; в Modified наблюдался PauseScreen. Поэтому namespace/counts, loaded RAM-policy и главное меню run01 остаются измеренными, но RU UI и непрерывные5минут здорового мира из них не выводятся. Прежняя RU-метка не считается native-наблюдением: уточнение Original опубликовано отдельно, а исходные533 записи архивированы.

В run02 повторно открыт тот же технический мир после штатного завершения run01 и QuickPlay, с private QA `config/defaultsettings/Default/options.txt`. Ровно2из103строк изменены: `lang:en_us→ru_ru` и `pauseOnLostFocus:true→false`;101остальная строка и `keys.txt` одинаковы. Авторский source-профиль2249байт/SHA`083ce95f…f62` остаётся прежним; приватная копия2250байт/SHA`98eb66c3…d893` — явное QA-отличие. Поэтому побайтное равенство всех1915 source/runtime-файлов не заявляется. Это не новая политика сборки, не правка личного мира, не предел графики и не CUA. Run02 реально подтвердил RU I18n и335,147с/103здоровых наблюдения/0paused без ввода, но позднее упал; полный AI/нормальный выход не PASS. Исторический lock214b/531 не переименовывается в эти прогоны.

## Новый native title Original и границы сравнения

Source-only [уточнение Original465fcd2](https://github.com/MarkZamore/All-The-Mods-9/commit/465fcd2a71c027f629e43055f9450cdbbb340ea2) исправляет предполагаемый RU на фактически сохранённый EN/пауза=true в metadata/отчёте. Runtime1805,432JAR, preset/quests/configs не изменены; четыре changed пути — README и три source-only tools-файла. [CI41314220858](https://github.com/MarkZamore/All-The-Mods-9/actions/runs/41314220858) завершился успешно, новый library/manifest скачаны и проверены; все219payload сохранили точные SHA предыдущей полной byte/member проверки. Это уточнение доказательств, не изменение языка игрока или новый RU UI PASS.

[Отдельный новый прогон Original](tools/qa/original-native-title-421.json) с разрешёнными официальным DeRenderPatcher/RAM-скриптом прошёл настоящее главное меню, read-only проверку loaded `disableWarnings=true` и штатный выход0. Все432 source JAR и E4 сохранили SHA; native ModList456/453pack ID, native Options488/registry502 сняты заново. Закрытый журнал содержит41ERROR/0FATAL; все41 точные сигнатуры уже встречались в историческом полном Original. Это окно меню без нового мира:96→41 не является уменьшением частоты ошибок или matched world сравнением. DE visual, Steam и выбранные скины этим не проверялись.

Родительская runtime-публикация Original [5c83a25](https://github.com/MarkZamore/All-The-Mods-9/commit/5c83a253137be7133336995bec111aa4ee8ef089) и лаунчер421 [f9b8967](https://github.com/MarkZamore/LANMinecraft/commit/f9b8967d6d0a5a1e20064feca843cf4c48d9d36a) опубликованы и проверены отдельно. [CI Original](https://github.com/MarkZamore/All-The-Mods-9/actions/runs/41312613040) завершился успешно; все1805 runtime-файлов сверены с публичным manifest, изменённые assets скачаны заново, прежние учитывались только по точному SHA ранее реально скачанных байтов. [CI421](https://github.com/MarkZamore/LANMinecraft/actions/runs/41312377974) прошёл503/503 обязательные проверки; настоящий публичный EXE168754605байт/SHA`fe9d2891bcca4df4ed3e1e8f06f8c876eb280155fd5d61819c9bade507ede524` проверен, обновление420→421 воспроизвело те же байты. Публичный byte/delta-verifier отдельно не запускал EXE: Singleplayer532 измерен frozen Debug reference SHA`bcb994f7e5b95597b22df4cdd7f1e61d5b255826be9e29d1f8961a7e4241a599`, native file version1.0.1.0/product1.0.1+b130ef14f0fd9c8dfdca9e3dcc3bb916e1b8d8dc. Рабочий source содержит проверенный421 preflight fix, но эта сборка не побайтно публичный421 или будущий422 EXE. Новая Modified532 имеет собственную native-проверку; Steam/P2P/визуальный PASS из публикации не выводится.

## Исторический полный прогон531, lock214b

[Исторический отчёт531](tools/qa/final-runtime-post-removals-420.md), [структурированные данные](tools/qa/final-runtime-post-removals-420.json) и [сравнение с Original](tools/qa/final-post-removals-comparison.md) относятся именно к lock `214b22b429d73f9b68b88c32021253cde056d10e137199a373b92b810e2fcf09`, а не к QA13, failed533 или текущему532. Снимок состава [архивирован отдельно](tools/qa/loaded-mods-531-214b.json). Все 531 source JAR и общий E4 совпали по SHA256 до и после игры. Три здоровых native-наблюдения меню и мира, ещё 308,894 с мира без ввода, отдельный русский AI-диалог, сохранение 83 измерений и выход0 выполнены. Все 642 активных назначения совпали с пресетом и сохранились. Оба AI-процесса завершились вместе с игрой; тот же локальный API после выхода отказал в соединении.

Полный закрытый лог имеет SHA256 `8caa25571668ea8bd1973a9f8a30df9841152457909804de5ee4ca7c2a1505e0`: **902 ERROR/0 FATAL =109 до ввода +792 после границы до выхода +1 при завершении**. Числа относятся к разной активности и длительности, не являются частотами и не означают 902 сломанных функции. Из 109 событий до ввода: 89 общих BASE/семантических GTCEu, 6 собственных сообщений новых компонентов, 2 BloodMagic и 12 намеренных JEI/Grand Sigil.

Свои новые ERROR оставляют **AzureLib (2), Celestisynth (1), Meulti’s Backrooms (1), YACL (1)** — отсутствующий `minVersion` в mixin metadata — и **CraftedCore (1)** при HTTP404 списка Patreon с резервом. Эти заголовки сами по себе не доказывают отказ инъекций или обычных превращений. Доказанная связь NEW→BASE — **Verity→Forge EventBus:790** диагностик после отдельного AI-чата. Это 395 пар для не-Event классов Jackson/LangChain; совпавшие байты и прежний нативный transformer-probe возвращают неизменённые ClassNode. Потеря 395 игровых handlers не установлена, настоящий русский ответ в этом мире получен. Логи и механики ради результата не подавлялись.

Ещё четыре BASE-заголовка имеют неустановленного NEW-инициатора: два BloodMagic/Curios Optional при первом chat panel и два поздних Placebo/Apotheosis `#irons_spellbooks`. Для Placebo найдено несовпадение неизменённых BASE-данных: Iron хранит подходящий magician в `boss_gear/`, текущий Placebo читает `gear_sets/`. Его штатный код пишет два сообщения и выбирает набор без фильтра, не бросая исключение. Конкретная живая сущность/caller не захвачены, в измеренном Original случай не воспроизведён; близость по времени к AI не доказывает вину Verity. Прежних AllTheLeaks/Citadel `dataMap`, Generic GL173538523, Jade/null BlockPos и ресурсных/function-ошибок удалённых модов в том историческом полном логе нет.

Этот результат не проверяет первый/повторный запуск, все способности, Box, два LAN-клиента, выбранный скин, личные миры или пиксельное качество. Исторический Box crash не объявлен исправленным. Непроведённые проверки не превращаются в PASS и не добавляются как новые общие блокеры к согласованной приёмке.

[Владелец принял прежний native-прогон531](tools/qa/native-source-acceptance-531-214b.json) в согласованных границах полного клиента/нового мира и раскрытых остаточных ERROR. Эта приёмка не заменяет отдельные проверки миграции и публичной поставки.

## Авторские остатки и защита мира

До согласованного исключения Born in Chaos 1.7.5 штатные loaders пропускали Scarlet Persecutor `attack`, прямо запрашиваемый моделью/контроллером. Все 15 официальных Forge 1.20.1 выпусков сохраняли этот дефект. Три старых idle-файла давали parser errors, но текущие Baby Skeleton/Bone Imp использовали чистые `*2`-файлы; потеря их idle не была установлена. Мод исключён по решению пользователя, собственный ресурсный патч не применялся.

До согласованного исключения Solo Leveling: Reawakening 1.2.0 у Kaiselin не загружались idle/walk, а default controller выбирал корректный fly. Поломка штатного полёта не была доказана; все dynamic callers не проверялись. Пользователь выбрал удаление мода; скрытый откат до 0.10.7.5 с потерей Kaiselin и других registry ID не выполнялся. Эти исторические дефекты новых модов не выдаются за ошибки исходной ATM9 или новые остатки после удаления.

Предупреждение Mine Mine no Mi об альтернативной Arclight-инъекции не отменяет найденный primary Forge вызов `KairosekiCoatingHandler` из реального BoatItem. Это проверка caller, а не самостоятельный тест способности.

[Исторический полный QA13](tools/qa/final-runtime-420.md) прежних 541 JAR подтвердил главное меню, нативно созданный новый мир, три здоровых состояния мира и штатное сохранение/выход с кодом 0; собственный AI backend завершился. В полном окне 134 ERROR и 0 FATAL. Чат и PTT в этом прогоне не выполнялись. Русский AI-ответ из diag12 остаётся отдельным доказательством; его 790 записей для 395 пар Jackson/LangChain parent-discovery/transform diagnostics не повторялись без chat и не объявляются исправленными. Точный eventbus/ASM probe возвращал неизменённые ClassNode; подавление логов не применялось.

[Историческая сопоставимая Original](tools/qa/matched-baseline-comparison.md) дала 96 ERROR/0 FATAL, Modified QA13 — 134/0. Разность количества не измеряет частоту или число новых причин. OpenAL `Deleting stream buffers: Invalid operation.`, shader-link/unlinked-uniform и сопоставленные базовые GTCEu сообщения воспроизведены в Original и приняты пользователем как общий некритический фон; удаление новых модов ради них не рекомендуется.

Для новой Generic GL `173538523` синхронный стек установил Roundabout depth-copy caller. [Частный A/B с удалением только Roundabout](tools/qa/roundabout-single-removal-ab.md) дал 0 таких сообщений вместо 30 475 и 0 Jade null-BlockPos заголовков вместо 3; шесть нативных чтений поля без Roundabout были non-null. Вместе с проверенным кодом это положительная причинная проверка двух случаев в данных условиях. Реальные форматы FBO и визуальный ущерб не измерялись. Blood Magic / Curios Optional/chat-overlay сохранилась: 2 ERROR с модом и 2 без него, виновник ещё не установлен. Эти измеренные GL/Jade случаи обосновывают согласованное пользователем исключение Roundabout; итоговая поставка фиксируется отдельно и не выдаётся за уже испытанный A/B-вариант.

В QA13 подтверждён вход естественной и отдельно призванной `verity:box` в native model/animation path с растущим временем модели. Исторический render crash не повторился; это не доказательство его исправления, полного GPU draw или качества изображения. Эффекты и guards ради результата не отключались.


Пользователь запретил собственный Safety/framework, поэтому они не добавляются и exact-SHA защитные профили не создаются. Причина отсутствия такой правки зафиксирована; это не доказательство автоматической claim-защиты. Разрушение мира, инвентари, отложенные способности и native permission gates остаются авторскими, кроме перечисленных явно согласованных конфигурационных изменений. Полная защита всех новых способов изменения мира не проверена.

## Восстановление, проверенная миграция и приёмка

```sh
python tools/client-policy/prepare.py --pack . --templates-only --apply
python tools/restore_modified.py --pack . --cache artifacts/verified-downloads
python tools/client-policy/prepare.py --pack . --apply
python tools/verify_modified.py --pack . --require-loaded-inventory
python tools/network_logging_policy.py verify --pack .
python tools/carpets_recipe_policy.py verify --pack .
python -m unittest discover -s tools -p "test_*.py"
python tools/generate_manifest.py --pack . --out dist --revision YOUR_COMMIT
python tools/generate_manifest.py --pack . --out dist --verify-all
```

Ограниченная запись сетевых исключений закреплена в самой сборке: `config/log4j2.xml`, штатный JVM selector и существующее владение `config/**`. Источник политики и точный receipt находятся в `tools/network_logging_policy.py` и `tools/network-logging-policy.json`. Генератор перед подготовкой поставки вызывает только `verify(pack)` и останавливает публикацию при потере фильтра, selector, владения или совпадения SHA. При запуске игры эти инструменты ничего не переписывают.

Точные байты XML/receipt сохраняются правилом `* -text` в `.gitattributes`; при переносе источника нельзя терять это правило или эквивалентное `config/log4j2.xml -text`. После свежего Git checkout повторите `verify`, чтобы проверить отсутствие нормализации переводов строк.

При будущем импорте новой авторской версии сохраняйте эти исходники и проверьте политику до публикации. Для намеренной подготовки независимой исходной копии используется `python tools/network_logging_policy.py prepare --pack .`: инструмент сохраняет остальные XML-узлы, JVM-флаги и декларации владения, добавляет недостающее и отказывается от конфликтующих настроек. После осознанного изменения самого XML обновите его exact-hash support-pin в `tools/modified-lock.json`; генератор и общий restore затем проверят согласованность. `prepare` не запускается автоматически в лаунчере или публикации и отказывается от установленного экземпляра с служебным маркером. При смене версии Minecraft за пределами проверенных вариантов сначала нужна новая проверка native caller. Это защита исходников от потери диагностики при обновлении, а не исправление причины разрыва соединения.

Коррекция рецепта принадлежит исходникам сборки: `tools/carpets_recipe_policy.py`, точный receipt `tools/carpets-recipe-policy.json` и ресурс `kubejs/data/alchemistry/recipes/dissolver/carpets.json`. Общий restore проверяет политику после восстановления JAR; генератор только проверяет её до публикации. Сохраните helper, receipt и ресурс при импорте автора. Если авторские639 байт изменены или исправлены, публикация останавливается: сначала сравните новый рецепт и удалите или явно перебазируйте только этот известный overlay. Его точный прежний путь/размер/SHA внесён в legacy union для безопасного последующего удаления, без очистки неизвестных личных файлов.

`python tools/carpets_recipe_policy.py prepare --pack .` применяется только оператором после проверки независимого source checkout. Это явное авторское перебазирование, не часть автоматического импорта, CI или запуска: новая версия JAR с прежними байтами рецепта также требует обзора и нового source receipt. Не включайте prepare автоматически. На установленной сборке с маркером инструмент отказывается работать; неизвестный существующий overlay сохраняет и отклоняет. Персональные настройки, миры, остальные рецепты и производительность не меняются этим исправлением.

Локализация BASE-текстов восстанавливается exact-hash профилем перевода: известные изменённые байты нормализуются перед авторским импортом и применяются обратно после него; неизвестные файлы не перезаписываются молча. `tools/legacy-files.json` содержит прежние управляемые SHA только для безопасной очистки старой установки, не как входы новой сборки.

Публикация сначала загружает и проверяет весь payload/библиотеку, затем manifest. Личные миры/профили и сырые логи не шипуются; технические миры не являются бэкапом. Для родительского `0096874596826ede2b8250dc04f70c8db58b8d886d61d958cf69870e34537285` отдельно выполнены собственные532 ModList, полный клиент/новый мир,393,470с здорового окна, действительный русский AI и штатный выход0;899ERROR/0FATAL классифицированы в [отчёте532](tools/qa/final-runtime-532.md). [Root singleplayer acceptance](tools/qa/native-source-acceptance-before-ss151.json) принимает только точный532 content cohort: полный клиент/свежий технический мир/реальный русский AI/сохранение и выход0 с раскрытыми899ERROR. Этот receipt относится только к singleplayer532; более поздняя реальная Steam-сессия Original422 имеет отдельное доказательство и не превращает532 в выполненный тест двух клиентов. STATE/LEGACY миграция пройдена; публичная поставка проверяется отдельно до карточки; актуальные файлы отражают [pack-latest](https://github.com/MarkZamore/All-The-Mods-9-Modified/releases/tag/pack-latest) и [workflow](https://github.com/MarkZamore/All-The-Mods-9-Modified/actions/workflows/publish.yml). QA13/531/failed533 сохраняются исторически. Отдельная игра ради resource-only русского ZIP WAIVED по запросу пользователя; общий532 runtime отдельно подтвердил native resource winner, без pixel/all UI PASS. **Original ATM9 действительно подключилась через Steam на лаунчере422.** [Отдельный public-safe отчёт](tools/qa/original-steam-422.json) фиксирует совпавший Steam game bridge с обеих сторон, вход21:53:26, открытие мира гостем21:55:20 и сохранённые данные хоста до22:00:52 местного времени:446с после допуска/332с после открытия мира, дальнейшая выдача чанков и0disconnect/Connection-debug fault в этом окне. Пользователь подтвердил совместную игру. Это один успешный сеанс, а не доказательство причины или постоянного устранения прежнего intermittent CME/AIOOBE. В422 не применялись CME-обход или ослабление handshake-таймаутов. Для Modified подтверждена общая платформа Minecraft1.20.1/Forge47.4.0 и тот же выбираемый по loader/version Steam-транспорт; это source/code-аналогия, а не фактический двухклиентский runtime PASS её дополнительного контента. Эта граница доказательства не вводит новый обязательный игровой тест для завершения поставки. Подробности — в [TESTING-STATUS.md](TESTING-STATUS.md).

Проверенный runtime остаётся lock009687…/1915файлов. Холодный CI исходного04abb выявил различие URL-представления ForgeCDN024/24 при одинаковом авторском JAR/SHA; адресная правка source-validator сохраняет обязательные hash/size/project checks и не переписывает JAR или game configs. Публичные payload/manifest и карточка принимаются по результатам собственного workflow/release, отдельно от native/migration receipts.


Историческая подготовка диагностики (снята после Steam435; приведённые далее команды больше не поставляются): Оба участника запускают игру как обычно через лаунчер; после открытия игры и до открытия мира для сети хостом/подключения гостем один раз запускают `launcher/diagnostics/Start-RecipeDiagnostics.cmd`, ждут `OBSERVER_READY`, затем пробуют подключиться и отправляют обычный отчёт через лаунчер. Временный v7 читает через JDI только ограниченные данные исходного recipe-исключения и точных точек закрытия соединения:2e4steam68ba+3Minecraft terminal entry breakpoints. Дополнительно3точки фиксируют получение клиентского keepalive, ответ серверу и первоначальный server disconnect до Connectivity-forwarder. Лимиты8recipe+24terminal+32keepalive события и256KiB собственных записей; прежний debug.log не урезается. Поток события кратко приостанавливается и возобновляется до записи на диск; игровой код, транспортные таймауты и рецепты инструмент не заменяет. Изолированный Java17 self-test прошёл, реальный новый peer test ещё предстоит. Неподдерживаемый KubeJS autostart удалён.

После подтверждённого исправления сети удалены все временные диагностические файлы, два JVM-флага и дополнительная ownership-строка по [точному cleanup inventory](tools/qa/temporary-recipe-diagnostics-cleanup.json). Постоянное ограниченное логирование, AI-данные, личные настройки и миры сохраняются. Shooting Star/Rimulib остаются согласованным обновлением; ModernFix отдельно сохраняется при обоснованности либо возвращается к авторской версии по явному review.

При обновлении автора сохраняйте явные исключения Dandadan/FairyMine/MineMineNoMi, текущий carpet data guard и точные support pins. Inventory projection проверяет архивный SHA и допускает только прямое вычитание известных JAR/ID из фактического архивного снимка без изменения оставшихся байтов; она не создаёт новый native-снимок. После подтверждённого сетевого исправления удалены только перечисленные в `tools/qa/temporary-recipe-diagnostics-cleanup.json`3файла,2JVM-строки и временное владение, обновив exact-hash retirement. Остальные launcher/AI/logging данные и личные миры сохраняются.

[Проверка529/v7](tools/qa/mine-mine-removal-and-connectivity-policy.json) отделяет source-проекцию от фактических наблюдений. [Изолированный self-test](tools/recipe-diagnostics/v7/validation.json) и [точный native-профиль](tools/recipe-diagnostics/v7/native-profile.public.json) не являются тестом нового530/529 игрового клиента. Никакой180-секундный startup-скрипт, изменение JSON Connectivity или новая JVM-настройка в этой поставке не добавлены.


### История снятой диагностики v8

В этой поставке изменён только диагностический JAR; 529 контентных JAR, рецепты, настройки и JVM-параметры сохранены. На обоих компьютерах после запуска игры и до открытия мира для сети/подключения запустите `launcher/diagnostics/Start-RecipeDiagnostics.cmd` из папки сборки в `Minecraft/Packs` и дождитесь `OBSERVER_READY`. Инструмент сохраняет собственные строки также в `logs/recipe-diagnostics-<сеанс>.log.gz`, чтобы они пережили очистку `debug.log`. Обычный отчёт лаунчера включает два самых новых архива журналов за последние 24 часа; после следующих сеансов нужный файл может выйти из этой пары.

[Проверка поставки](tools/qa/observer-v8-delivery.json), [self-test и проверка отчёта опубликованного лаунчера429](tools/recipe-diagnostics/v8/validation.json), [инструкция и границы показаний](tools/recipe-diagnostics/v8/README.public.md). Создание keepalive-пакета не доказывает отправку, чтение ID не доказывает обработку. Это временная диагностика, исправление сетевого сбоя и новый успешный игровой тест здесь не заявлены. Таймаут Connectivity остаётся авторским, 60 секунд; политика JourneyMap в эту поставку не входит.


### Разделение точек JourneyMap у новых одиночных миров

Кандидат политики хранит собственный UUID в `saves/<мир>/lanmc-waypoints-world.json` и связывает с ним только каталог точек JourneyMap. При повторном использовании имени папки прежние точки сохраняются в `local/lanmc-waypoint-archives/v1/<слот>/<UUID>/waypoints`; возврат известного UUID в тот же слот восстанавливает соответствующий набор. Изображения карты, настройки JourneyMap и данные игры не переписываются. При первой установке существующие миры принимают свои точки без очистки. Политика работает только с локальным встроенным сервером; удалённые серверы не затронуты.

[Границы проверки](tools/qa/journeymap-waypoint-generation-source.json): проверены исходники, родные API и файловые сценарии на настоящем Rhino; новый полный запуск игры и реальное переключение миров не заявлены. В авторском JourneyMap запись точки смерти выполняется после минимальной задержки в три секунды и ожидания очереди исполнителя без повторной проверки поколения мира. Такой старый callback ещё может записать точку после перехода в другой мир; отдельный фильтр не включён. Одновременная работа двух клиентов с одной папкой игры и внешнее редактирование файлов не поддерживаются; аппаратные сбои питания не моделировались. При ошибке начальной проверки или пути операция пропускается с предупреждением и сохраняет прежние файлы.

При импорте новой авторской версии сохранить `tools/journeymap-policy`, `tools/waypoint_source_policy.py`, `tools/journeymap-waypoints-policy.json` и шаблон в `tools/client-policy/scripts`, а также соответствующую строку `policy.json` и support-lock. Перед восстановлением JAR выполнить `python tools/client-policy/prepare.py --pack . --templates-only --apply`, после восстановления — обычную проверку client-policy и `python tools/waypoint_source_policy.py --pack .`. Генератор проверяет политику без изменения файлов. Неизвестная версия JourneyMap/KubeJS/Rhino или платформы останавливает подготовку до проверки API; личные файлы скриптом публикации не переписываются.


### Историческая поставка диагностики v9 (заменена v10)

Временная утилита v9 дополнительно отмечает завершение кодирования keepalive и читает до 24 ограниченных снимков очередей активного Steam bridge с интервалом не менее пяти секунд. Сохраняются предел 256 КиБ собственных строк, точные SHA библиотек и обычная отправка отчёта. Снимки не атомарны, перечисление объектов создаёт нагрузку; кодирование не доказывает отправку или доставку. [Проверка поставки](tools/qa/observer-v9-and-waypoints-delivery.json), [инструкция и границы](tools/recipe-diagnostics/v9/README.public.md).

Для следующего контроля подключения по локальному IP запуск утилиты необязателен. При последующей проверке Steam оба участника могут запустить её из `Minecraft/Packs/All the Mods 9 Modified/launcher/diagnostics/Start-RecipeDiagnostics.cmd` до открытия мира для сети/подключения. Настройки таймаутов и параметры JVM сохранены; нового EXE и изменений транспорта нет. Диагностические файлы и два временных JVM-параметра удаляются после подтверждённого исправления; постоянная политика точек JourneyMap остаётся в сборке. Новый игровой или сетевой PASS этой публикацией не заявлен.


### Диагностика v10 без поиска по куче JVM

Временная v10 заменяет v9: периодический поиск экземпляров по куче полностью удалён. Ссылки берутся только в двух точных lifecycle-точках будущих соединений и затем используются для ограниченного чтения полей. До 16 сохранённых ссылок каждого типа и 24 снимков не дают полной картины: уже активные до `OBSERVER_READY` объекты, переполнение лимита и сборка мусора могут оставить пробелы. Поля не атомарны; короткие остановки потока на прежних точных событиях и обычные накладные расходы отладчика сохраняются. [Проверка](tools/qa/observer-v10-delivery.json), [инструкция](tools/recipe-diagnostics/v10/README.public.md).

V9 не использовать: её численный предел возвращаемых объектов не ограничивал работу обхода всей кучи. Для текущего контроля по локальному IP утилита v10 тоже не нужна. Постоянная политика JourneyMap, все 529 контентных JAR, таймауты, параметры JVM и ручные CMD/PS сохранены. Утилита остаётся временной и не запускается автоматически; после подтверждённого исправления она и два диагностических JVM-параметра удаляются. Новый игровой или сетевой PASS не заявлен.
