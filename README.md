# Minecraft Mystery Box

**Vanilla Java 26.3 gameplay datapack + resource pack. No mods required.** One shared mystery box in the Overworld. The 1.21.1 backport is feasible but is not an implemented or tested release; see [compatibility](#1211-compatibility).

## License

Original project code, datapack logic and original artwork are licensed under **GNU GPL version 3 only** ([LICENSE](LICENSE)); distributed without warranty. Minecraft names, vanilla assets, and the vanilla-derived witch-laugh audio remain the property of their respective owners and are not relicensed by this project. The audio-generation script rebuilds that sound from a locally installed Minecraft copy. This is an unofficial project, not approved by or associated with Mojang or Microsoft.

## Install in Modrinth

Open the instance's folder from Modrinth. Install these **two separate ZIPs**:

| File | Destination under the instance folder |
| --- | --- |
| `dist/mysterybox-datapack-26.3.zip` | `saves/<your world>/datapacks/` |
| `dist/mysterybox-resourcepack-26.3.zip` | `resourcepacks/` |

1. Back up an existing world first. Start with a disposable world if testing.
2. Enable the resource pack in **Options → Resource Packs**.
3. Open the world and run `/reload` with cheats/operator permission, or reopen the world. `/datapack list enabled` should include the mystery-box pack.
4. The pack attempts to place one box near world spawn. It does not create a platform or overwrite terrain; its three invisible barrier blocks replace only air. If placement fails, an operator can use `/function mysterybox:admin/place` at a clear location.
5. **Right-click any part of the 3-wide × 2-high activation area**, including the row above the solid base, with any item or an empty hand. An opening costs **10 XP points** by default, not whole levels. Ordinary players do not need command permission to buy.

Datapacks are **per world**, not mods: do not put the datapack in Modrinth's `mods` folder or its resource-pack list. On a dedicated server, install the datapack in the server world's `datapacks` folder and supply the resource pack to clients.

The separate **Mystery Box Model Check** instance contains the flat **Mystery Box Asset Preview** test world and the normal-terrain **Mystery Box Survival** world, both with the current datapack installed. Survival has commands enabled for testing. The enabled resource ZIP in that instance retains its earlier `mysterybox-models-26.3.zip` filename, with the updated content. Other instances were not changed.

## Gameplay

- **Category-balanced loot sets:** `weapons`, `default`/`combat`, `weapons_armor`, `weapons_tools`, `extended`, `extra`, and `godmode`. Category weights are **weapons 50, armor 20, tools 15, potions 10, misc 5**, normalized over the categories present in each mode. Entries within a category have equal odds. Axes count only as weapons.
- **Independent gear enchantments:** Minecraft rolls compatible enchantments after choosing the item. Normal limits and mutual exclusions apply; `godmode` raises only the selected enchantments to their vanilla maximum levels. Non-gear supplies do not receive ordinary random enchantments.
- **Mending:** a separate **6.7% chance on eligible gear**, configurable from 0–100%. Other enchantment rolls cannot bypass this setting. A successful Mending roll removes Infinity from a bow.
- **Binding and Vanishing are separate options, both off by default.** Each curse still has an independent **2% chance on vanilla-compatible gear**, with no extra chance from the ordinary enchantment pool. Both can occur together. Enabling either forced-curse switch adds that curse to every reward stack, including supplies and bonuses. Binding affects worn equipment, not whether weapons can be dropped; Vanishing follows vanilla death rules, including `keepInventory`.
- Bows and crossbows include **64 arrows**. TNT includes **one flint and steel**, without ordinary enchantments. The trident display uses its flat inventory sprite; the reward is a dropped item, not a thrown-trident entity.
- The rolling items **rise from floor level (Y 0) to standing-player eye height (Y 1.62) relative to the box base**, then stop and reveal the result at **tick 77 (about 3.85 seconds)**. A weapon gets its separate two-second finished tune. The item drops from the reveal height and closing starts at tick 117 (5.85 seconds); the lid finishes closing at about 6.85 seconds.
- **4% teddy outcome:** no item is awarded; the buyer receives the **actual number of XP points charged**, then the box relocates. A full dragon growl starts at reveal; the louder, higher-pitched three-voice witch laugh starts **2.25 seconds later**, overlapping the growl's last 0.75 seconds and continuing briefly afterward. Both broadcast across dimensions. The laugh is scheduled independently, so closing/moving the box does not skip it. Opening and weapon-finished music remain local.
- The laugh voices start at **0, 33, and 66 ms**, not three coarse command ticks. Only that short laugh is a custom audio asset; the dragon, opening score, and finished score remain independent.
- The default teddy chance is **4%**, independently of the item table. Category percentages below apply to non-teddy rewards; multiply by 96% for probability per opening. All 138 potion variants share one category's allocation rather than crowding out gear.
- Relocation searches **16–64 blocks horizontally**, sampling **Y −63 through 318** and scanning downward for supported locations, including caves. It needs exactly **three blocks wide × one block deep × two blocks high of air**, with **three solid floor blocks directly below**. Adjacent walls and a ceiling above that space are allowed. Floating placement is removed. The floor is checked only on placement: players can break it afterward without the pack restoring it or moving the box. Failed searches keep the existing box and still refund a teddy roll.
- Payment subtracts raw XP points across level boundaries; both the level and XP bar can change. Busy clicks and insufficient XP never charge. Refunds belong to the buyer, retain the original point price after config changes, and survive reload/logout; an offline buyer receives a due refund after returning. Item drops are not private and can be picked up by nearby players.
- A **3×1 barrier base** is solid and survival-unbreakable. Three narrow, two-block-tall interaction columns activate the box across the entire **3×2 front/side area**, including the pass-through row above the base. They also intercept ordinary placement clicks without obstructing movement above the base. This is not general protection against commands, creative administration, pistons, fluids, or blocks placed above that row. Barrier visuals appear only to administrators holding a barrier item.
- The box removes its owned barriers and interaction entities when moving/removing, restoring the air types it replaced. It keeps required chunks loaded, transfers its own tickets on relocation, and does not release tickets already owned by another administrator.
- The box uses **vanilla spruce planks for all wood**, including its three lid notches, with four ordinary brick-textured supports and two blocky question marks. No metal bars, rivets, or carrying handles.
- Locator beams are **0.75-block-wide, camera-facing 2D sprites**. The long shaft is opaque, pale blue with a bright core; only the two-block transition at the box is transparent. Each direction retains six independently positioned 16-block sections. The downward shaft starts **3 blocks below the box** and continues 96 blocks downward. There is **no spin or proximity fading**. Terrain, fog and entity tracking still limit visibility.

## Configure in game

Operator/cheat commands. Changes persist across reloads; rebuilding does not overwrite existing world settings.

```mcfunction
# Price in raw XP POINTS, not whole levels or items:
/data modify storage mysterybox:config price_points set value 10

# Teddy probability in basis points: 400 = 4%, 100 = 1%, 0 = never.
/data modify storage mysterybox:config teddy_basis_points set value 400

# Weapons, armor, potions and combat supplies (default; "combat" is equivalent):
/data modify storage mysterybox:config loot_mode set value "default"
# Example: weapons and tools, no armor:
/data modify storage mysterybox:config loot_mode set value "weapons_tools"

# Independent forced curses: 0 = normal 2% eligible-gear chance; 1 = force on all stacks.
/data modify storage mysterybox:config binding_curse set value 0
/data modify storage mysterybox:config vanishing_curse set value 0
# Independent Mending chance: 670 = 6.7%, 0 = never, 10000 = always on eligible gear.
/data modify storage mysterybox:config mending_basis_points set value 670

# Disable teddy/relocation; every purchase then awards an item.
/data modify storage mysterybox:config relocate set value 0
# Re-enable:
/data modify storage mysterybox:config relocate set value 1

# Placement: 0 = supported surface; 1 = supported locations at any Y,
# including caves (default). Both require solid ground; floating mode is removed.
/data modify storage mysterybox:config placement set value 1

# Enchanting power, NOT the number of enchantments or a Sharpness level.
# Both values must be integers 1–30, with minimum <= maximum.
/data modify storage mysterybox:config enchant_level_min set value 1
/data modify storage mysterybox:config enchant_level_max set value 30
```

| `loot_mode` | Entries | Contents |
|---|---:|---|
| `weapons` | 25 | Swords, axes and spears of every material; bow, crossbow, trident and mace |
| `default` / `combat` | 197 | Weapons + all player armor/elytra + 138 potion variants + 2 enchanted golden apples, 4 golden apples, 16 ender pearls, or 16 TNT with flint and steel |
| `weapons_armor` | 55 | Weapons and player armor/elytra only |
| `weapons_tools` | 50 | Weapons and tools, without armor |
| `extended` | 222 | Combat contents plus tools |
| `extra` | 244 | Extended contents plus 4 emerald blocks, an empty shulker box, a wither skeleton skull, and each of the 19 smithing templates |
| `godmode` | 44 | Extra contents with netherite-only material-tier gear, no bows/potions/regular golden apples, 64 enchanted golden apples instead of 2, and 16 bedrock |

Each listed stack or kit is **one possible reward**, not everything in the row at once. Tools include pickaxes, shovels, hoes, axes, brush, shears, fishing rod and flint and steel. Potions cover all 46 vanilla registered variants (including base/extended/strong variants where available) in drinkable, splash and lingering forms. The shulker is a pickupable **empty shulker box**, never a mob.

Category odds, conditional on receiving an item (rounded):

| Mode | Weapons | Armor | Tools | Potions | Misc |
|---|---:|---:|---:|---:|---:|
| `weapons` | 100% | — | — | — | — |
| `default` / `combat` | 58.82% | 23.53% | — | 11.76% | 5.88% |
| `weapons_armor` | 71.43% | 28.57% | — | — | — |
| `weapons_tools` | 76.92% | — | 23.08% | — | — |
| `extended` / `extra` | 50% | 20% | 15% | 10% | 5% |
| `godmode` | 55.56% | 22.22% | 16.67% | — | 5.56% |

Absent categories are omitted, not replaced by empty rewards. Misc includes supplies, templates and the empty shulker box. Bonus arrows/flint and steel belong to their main reward, not a separate roll.

Godmode retains unique/untiered equipment: crossbow, trident, mace, elytra, brush, shears, fishing rod and flint and steel. It excludes the turtle helmet and all non-netherite material tiers. It maximizes randomly selected enchantment levels, **not the number of enchantments**; Mending still uses its separate chance.

The selected mode, both forced-curse flags and Mending chance are captured when a purchase starts. Changes during the animation affect the next purchase. Mending and teddy chances accept integer basis points from 0–10000. The two random curse chances are each fixed at 2%; supplies and bonus stacks receive curses only when forced.

**Loot-set upgrade:** the first reload changes legacy `loot_mode:"all"` to `"default"` and an unchanged 1000-point teddy chance to 400. Other teddy chances remain unchanged. Missing curse/Mending options get their defaults; subsequent reloads preserve customization.

**Separate-curse upgrade:** the first reload of this version resets both forced-curse switches to `0`, replacing the old default-on behavior. Later reloads preserve your choices. Existing rewards and a reward already captured by an in-progress opening are not rewritten.

`price_points` must be a nonnegative integer; zero makes openings free. Teddy probability accepts 0–10000. `source/defaults.json` defines new-world defaults; existing settings persist in `mysterybox:config`. **Price upgrade:** the first reload changes the previous 95-point default to **10**, preserves other prices, and marks the migration complete. Later reloads preserve all choices, including a deliberately restored price of 95. Missing prices default to 10. Old `price_levels` settings are removed rather than reinterpreted as points; already-owed level refunds keep their original units, and point refunds keep the amount originally charged. Reload also migrates removed floating placement (`2`) to grounded any-height placement (`1`), without moving an existing box. The old emerald `price` and level-up `reward_sound` settings are removed.

**Sprite-beam and click-area update:** replace both ZIPs, run `/reload`, and press **F3+T** (or restart). The next box tick replaces old beams with twelve narrow shaft sections plus one transparent base sprite and replaces the old upper guards with three two-block-tall activation hitboxes. It does not move the box, edit its base blocks, or charge XP. Relocation rebuilds these entities; removal cleans them up. Spin/proximity code and opacity variants have been removed. The latest in-game appearance remains the user's check; see [UC-20260927-03](UNCHECKED.md#uc-20260927-03--dithered-segmented-beam-over-water-and-at-distance).

To guarantee a test teddy, set `teddy_basis_points` to `10000` with `relocate` set to `1`. Restore `teddy_basis_points` to `400` after the opening for the normal 4% chance. This is a persistent probability setting, **not a one-shot override**; the usual XP cost and refund still apply.

Admin tools:

```mcfunction
/function mysterybox:admin/status
/function mysterybox:admin/place
/function mysterybox:admin/remove
```

`admin/place` snaps to block centers at your current Overworld position and requires the same supported 3×1 base and clear row above. It refuses an obstructed or unsupported target without deleting the existing box. `admin/remove` restores owned base air, removes entities, releases owned tickets, and disables respawning; `admin/place` enables it again. **Remove the box before uninstalling**, or its barriers/entities/tickets remain. Keep the datapack installed until any queued refunds have been paid. An older box upgrades its collision only if the footprint is clear; otherwise clear the obstruction and `/reload`, or place it elsewhere.

## Melody: listen and change the volume

The [new piano tutorial](https://www.youtube.com/watch?v=jLhPToHJ7gM) supplies **23 opening notes and six finished-cue notes**. Visible keys and audio attacks replace the previous noisy spectral guesses. Octave doubles and most accompaniment were removed; intentional adjacent-key dyads remain. This is an approximate harp arrangement, not the original recording or full piano polyphony.

### Free previews

Stand in the Overworld:

```mcfunction
/function mysterybox:sound/preview
/function mysterybox:sound/preview_teddy
```

The first plays opening plus the weapon ending; the second plays opening plus the separate dragon/laugh outcome. Neither opens the box nor charges XP. Allow about eight seconds for the teddy cue to finish. **The teddy preview's outcome is also server-wide**, so warn other players before testing. Once a teddy cue starts, its scheduled laugh continues independently even if a new preview is started.

### Independent volume controls — no rebuild or reload

```mcfunction
# Opening notes:
/data modify storage mysterybox:config melody_volume set value 50
# Two-second weapon-finished tune:
/data modify storage mysterybox:config finished_volume set value 60
# Dragon growl:
/data modify storage mysterybox:config dragon_volume set value 35
# Three-voice witch laugh:
/data modify storage mysterybox:config teddy_volume set value 70
# Other effects:
/data modify storage mysterybox:config opening_volume set value 70
/data modify storage mysterybox:config closing_volume set value 70
/data modify storage mysterybox:config moving_volume set value 70
```

Every setting uses **0–100 percent**: `0` mutes that part, `50` halves it, `100` restores full authored volume. A CSV note at 60% and its phase volume at 50% plays at 30%. Also check each client's **Master Volume** and **Blocks** sliders. Server-wide playback does not override a client's mute settings.

`/data modify storage mysterybox:config melody set value 0` disables opening/finished notes during purchases, not the teddy effects or free previews. Set it to `1` to restore music.

### Edit or remove individual notes

Open either file in LibreOffice Calc, Excel, or a text editor; save as **comma-separated CSV**, not XLSX:

- [`source/opening_melody.csv`](source/opening_melody.csv): the spinning music.
- [`source/finished_melody.csv`](source/finished_melody.csv): the weapon-only ending.

```csv
tick,note,cents,volume_percent,instrument
1,B4,0,90,harp
3,C#5,0,90,harp
7,B4,0,85,harp
```

| Column | Meaning |
| --- | --- |
| `tick` | **20 ticks = 1 second**. Matching ticks form a chord. Opening starts at tick 1; finished CSV tick 1 means the moment spinning stops. |
| `note` | Note and octave: `C4`, `F#4`, `Bb3`. Harp's usable range is **F#3–F#5**. |
| `cents` | Fine tuning; keep `0` for normal tuning. 100 cents is a semitone. |
| `volume_percent` | **0–100 for just this note**. Change `90` to `45` to halve it; `0` mutes it. |
| `instrument` | `harp` gives the piano-like sound. Other note-block instruments change timbre/register. |

**Wrong note? Delete its entire row. Too loud? Lower only its `volume_percent`.** For example, `1,B4,0,30,harp` makes the first note quiet. These are readable musical notes, not encoded audio bytes. Native harp decay controls sustain.

Apply score edits:

1. Run `python tools/build_datapack.py` from the repository root.
2. Replace your world's installed datapack ZIP with `dist/mysterybox-datapack-26.3.zip`; do not leave duplicate versions.
3. Run `/reload`, then the appropriate free preview.

CSV edits do not require a resource-pack reinstall. Opening ticks must be **1–76** and finished ticks **1–40**. The builder rejects notes outside those phases rather than silently making the animation longer. To deliberately change timing, edit `reveal_tick` and `duration_ticks` in `source/opening_melody.json`, keeping `duration_ticks = reveal_tick + 40`, then rebuild.

### Change the laugh pitch or echo spacing

[`source/teddy_audio.json`](source/teddy_audio.json) contains readable controls: `pitch_multiplier: 1.5`, `echo_delay_ms: 33`, three `echo_gains` of `0.48, 0.31, 0.21`, and `output_gain: 3`. Higher pitch multipliers make the laugh brighter; the delay is between consecutive voices. Echo gains must total at most 1; output gain raises the mixed laugh above its previously masked level. The shipped OGG peaks at approximately −2.5 dBFS. Recheck peak level if changing pitch, delays, or gains.

After editing, rebuild from your installed vanilla asset cache:

```sh
python tools/build_teddy_audio.py --assets "$HOME/.local/share/ModrinthApp/meta/assets" --index 34
python tools/build_datapack.py
```

This requires FFmpeg. Replace **both** installed pack ZIPs; run `/reload` and reload client resources with **F3+T**. Other players also need the updated resource pack. The generated OGG contains only the witch laugh at 0/33/66 ms; the dragon is not cut short or mixed into it.

### Change other sound choices

```mcfunction
/data modify storage mysterybox:config dragon_sound set value "minecraft:entity.ender_dragon.growl"
/data modify storage mysterybox:config teddy_sound set value "mysterybox:teddy_laugh"
/data modify storage mysterybox:config opening_sound set value "minecraft:block.chest.open"
/data modify storage mysterybox:config closing_sound set value "minecraft:block.chest.close"
/data modify storage mysterybox:config moving_sound set value "minecraft:entity.enderman.teleport"
```

IDs take effect at the next event. The full vanilla dragon starts globally at reveal. The laugh is independently scheduled **45 ticks (2.25 seconds) later**, overlapping its tail; no command stops the dragon. Choosing `minecraft:entity.witch.celebrate` gives the ordinary unlayered vanilla laugh. Weapons use their own ending score. If the custom laugh is missing, install the updated resource pack on every client, press **F3+T**, and check `teddy_volume` plus the client's Master/Blocks sliders.

## 1.21.1 compatibility

**Feasible as a separate generated release, not by marking the 26.3 ZIP compatible.** The shared source can retain payment, random choice, interaction entities, animation, placement, and note timing. A target adapter needs these changes:

| Area | 26.3 release | Required 1.21.1 output |
| --- | --- | --- |
| Pack metadata | Data 121.0; resources 97.1, major/minor metadata | Data `pack_format: 48`; resources `pack_format: 34` |
| Model selection | `minecraft:item_model` and `assets/mysterybox/items/` | Integer `minecraft:custom_model_data`, paper model overrides; avoid collisions with other packs |
| Inline loot modifiers | `type` discriminator | `function` discriminator; adapt inline commands, not just JSON files |
| Enchantment readback | Flat enchantment component | Account for the older `levels` wrapper in the no-enchantment fallback and regression checks |
| Weapon pool | 25 weapons | 16 weapons; exclude copper weapons and every spear |
| Armor pool | 30 armor/elytra entries | Exclude copper armor; regenerate against the 1.21.1 tags |
| Command messages | SNBT text accepted | Emit strict quoted JSON text throughout |
| Visual details | Modern element light emission | Check/remove unsupported model fields and verify older transparency/emission behavior in-game |

Both versions have `/random`, function macros, interaction/display entities, and compatibility-aware enchanting. Both use singular `function` and `loot_table` directories. Their native loot data and version metadata were inspected; the 1.21.1 client was **not** used for gameplay verification. No 1.21.1 installable ZIP is claimed here. Other 26.x releases also need their own schema/runtime check rather than a blanket compatibility promise.

## Model and source files

Original cuboid geometry authored in Blender. The box references the client's vanilla spruce-plank and brick textures; vanilla PNGs and the supplied reference image are not redistributed in the resource pack. Other enabled packs that override those vanilla textures will also affect the box.

- `model/mysterybox.blend`: editable crate, lid animation, shine, beam, and separate teddy.
- `model/assembly.json`: pivots and display transforms.
- `resourcepack/`: generated model JSON and PNG textures.
- `tools/build_assets.py`: Blender authoring/export script; recreates scenes, assets, and renders.
- `tools/build_datapack.py`: gameplay generator; Python 3, no third-party packages.
- `tools/melody.py`: CSV note-name/pitch conversion and validation.
- `tools/economy.py`: XP-point payments and persistent buyer-owned refunds; outstanding pre-upgrade level debts keep their original units.
- `tools/build_teddy_audio.py`: reproducible 33 ms witch echo from the installed vanilla asset cache.
- `source/`: weapon/armor catalog, defaults, opening/finished CSV scores, laugh settings, and transcription provenance.
- `datapack/`: generated gameplay files. Edit the source/generator, not this output.
- `tools/preview-commands.txt`: older model-only manual scene, not gameplay installation.

The box is **2.5 × 1.0625 × 1.0625 blocks**, with a lid opening upward 105°. Opening shine is **2.5 blocks wide and 1.125 blocks tall**. Locator shafts use six **0.75×16-block**, double-sided, vertically billboarded sprites in each direction. The transparent base spans Y **1.0625–3.0625** relative to the box; the opaque upper shaft spans **3.0625–99.0625**. The lower shaft spans **−99 to −3**, leaving a three-block gap below the box. The editable Blender file includes one shaft section and the transparent base; `model/assembly.json` lists all section positions.

The beam meshes are not volumetric lighting. The chest separately places an **invisible level-9 light block immediately above its base**, outside the opaque barriers; it lights nearby terrain without blocking movement or clicks. Normal walls still occlude Minecraft light. Existing boxes receive it on their next tick. Only air is replaced, its original air variant is remembered, and relocation/removal restores it only if the owned level-9 light remains unchanged. Unrelated blocks and pre-existing lights are left alone. The beam remains subject to terrain occlusion, fog, render distance, and entity tracking.

Native Minecraft 26.3 light regression: **0 errors**, including level 9 at the source, level 8 in adjacent air, negative brightness controls, reload preservation, three air-variant restorations, protection of unrelated blocks/pre-existing lights, changed-block cleanup and existing-box upgrade. `python tests/build_light_checks.py <empty-output-directory>` generates the disposable GameTest fixture; include it alongside the gameplay pack, run `lightcheck:light`, and require saved `lightcheck:results` to contain `completed:1,errors:0`. The server test establishes actual light propagation; no client screenshot was taken for this update.

Rebuild the artwork, editable `.blend`, and previews using an installed vanilla client JAR:

```sh
blender --background --threads 8 --python tools/build_assets.py -- --vanilla-jar /path/to/26.3.jar
python tools/build_datapack.py
```

Blender previews load vanilla PNGs into a local cache; the `.blend` references those external files. Regenerate on another workstation to populate its cache. Custom teddy/glyph and lighting textures are packed in the `.blend`.

For faster preview generation, append `--preview-samples 2`; this changes only Blender preview sampling, not the exported Minecraft models or textures.

## Verification and remaining listening check

Latest loot changes were exercised through **Minecraft 26.3's headless GameTest server** in a new disposable world, without controlling the user's client. Saved NBT results were read with `nbtlib 2.0.4`:

- **3,500 native weighted draws:** 500 per canonical mode, all producing rewards from allowed categories. The extended-mode sample contained 251 weapons, 99 armor, 74 tools, 50 potions and 26 misc rewards. Exact category weight ratios, within-category equality and deduplication were also checked against every generated table.
- **47 reward-behavior cases, 0 errors:** primary/bonus drops, empty shulker-box item, trident context, godmode maxima and compatibility, captured settings, all four forced-curse switch combinations, the independent 200/10000 curse boundaries and eligibility, and Mending 0%/100% with bow Infinity removal.
- **160 enchantment samples over 80 gear items, 0 errors:** supported enchantments, compatibility, levels and Mending-disabled behavior. The player-oriented fixture was executed at the loaded box anchor; running it at the headless server's unrelated command-source position had produced invalid fixture results.
- Native entity readback confirmed **12 shaft segments plus one transparent base**, 0.75 width, vertical billboarding, preserved spacing and the three-block lower gap. It also confirmed **three 2.002-high responsive hitboxes** and migration of 95→10 while retaining a custom price of 37.
- The Blender beam preview was inspected. Client rendering over water, mouse activation across the upper row, and actual player pickup/death behavior were not manually rechecked. Earlier native checks covered all 246 distinct item/component outcomes before category reweighting; entry contents are unchanged.
- `/function mbcheck:rewards` runs the native reward regression fixture with an idle box and no nearby loose items; use a disposable world. `/function mbcheck:enchantments` covers gear compatibility. The first combined run exhausted the command-chain limit during duplicate enchantment samples; removing duplicate same-path samples allowed the complete run to finish within the vanilla limit.

Earlier point-economy/model checks used **vanilla 26.3, Java 25**, with the previous 95-point configuration in an isolated copy of the preview world:

- Native economy regression function reported **0 errors**: 94-point rejection, exact 95-point debit across low/mid/high XP ranges, 16/17 and 31/32 level boundaries, scoreboard overflow boundaries, busy rejection, normal/teddy drops, captured-price refunds, duplicate-refund rejection, and preserved pre-upgrade level debts.
- Actual Survival right-clicks spent **190 → 95 → 0 XP points**. At 95 points the player had level 7 plus 4 bar points, rather than losing a fixed number of levels.
- Native screenshots showed the spruce model, four brick supports, upward and below-ground shafts, and the rolling display rising out of the box. Slow-tick screenshots were used to inspect motion; normal 20-tick gameplay was restored. The subsequent Y 0 → 1.62 offset adjustment was rebuilt without manual in-game verification, as requested.
- No function/model/texture load errors were reported for the updated packs. This isolated client had no OpenAL device; audio was not re-verified by this visual/economy run.

Earlier runtime checks for otherwise unchanged behavior:

- **220 native enchanted samples across all 55 items**: zero unsupported enchantments, incompatible pairs, empty results, or excessive levels.
- An Overworld-issued global dragon cue successfully targeted the test player while they were in the Nether. This verifies cross-dimension dispatch with one client, not a multi-client load test.
- The revised resource pack loaded with a working native OpenAL device. The standalone laugh is 48 kHz mono, about 1.059 seconds; its three voices are authored at 0/1584/3168 samples (0/33/66 ms), at 1.5× pitch.
- Base collision/upper click protection was accepted by the user; a native placement attempt also preserved air and the held stack. The beam entity's translation and the editable Blender pivot both showed the new 3.0625-block starting height.
- Grounded-placement regression checks passed with zero errors: unsupported air, a missing floor block in each position, and blocked lower/upper space are rejected; a supported 3×2 opening between walls and under a ceiling is accepted. A real relocation moved the formerly floating box from `[29.5,217,13.5]` to `[-6.5,-60,39.5]`, with all three supporting floor blocks verified.
- The corrected global teddy cue was captured directly from Minecraft's own audio stream. Waveform matching identified the vanilla dragon (correlation 0.956) and shipped triple-laugh asset (0.871), rather than relying only on command success messages.

**Final musical fidelity and sound balance remain the user's listening check.** This is an intentionally reduced harp arrangement; source analysis and command dispatch are not proof that it sounds identical. Multi-client refund isolation/logout acceptance also remains unexercised; see [UNCHECKED.md](UNCHECKED.md).

Optional destructive test-world checks can be generated with:

```sh
python tests/build_runtime_checks.py --minecraft-jar /path/to/26.3.jar
```

Install the resulting checks ZIP alongside the gameplay pack in a **disposable world only**. `/function mbcheck:enchantments` validates real engine output; `/function mbcheck:economy` temporarily changes XP/configuration and replaces held items. It restores XP/configuration, but not held items. `/function mbcheck:placement` runs in Creative from an empty 5×4×3 air volume, creates a bounded floor/wall fixture, and removes it afterward; it refuses occupied space. Remove the checks pack afterward. These checks are not required to play.

## Sources

- [Revised melody reference: piano tutorial](https://www.youtube.com/watch?v=jLhPToHJ7gM)
- [Item modifiers and enchanting](https://minecraft.wiki/w/Item_modifier)
- [Interaction entities](https://minecraft.wiki/w/Interaction) and [display entities](https://minecraft.wiki/w/Display)
- [Resource-pack models](https://minecraft.wiki/w/Model)
- Local vanilla 26.3 and 1.21.1 client JAR metadata, item tags, and loot definitions for version-specific contracts.

## Dedicated server installation and resource-pack downloads

### Install gameplay on the server

1. Use **Java Edition 26.3** on the server and clients. This release targets data format **121.0** and resource format **97.1**; it is not a 1.21.1 pack.
2. Stop the server and back up its world. Copy `dist/mysterybox-datapack-26.3.zip` into `<server>/<level-name>/datapacks/`, where `level-name` is the world directory configured in `server.properties`. Do not put it in `mods/` or send it as the client resource pack.
3. Start the server. As an operator, run `/datapack list enabled` and `/function mysterybox:admin/status`. The box attempts supported placement near Overworld spawn. If necessary, stand at a clear supported location and run `/function mysterybox:admin/place`.
4. Set up the client download below. Test with a regular non-operator player: the spruce model should render, right-click should charge 95 XP points, and the custom teddy sound requires the resource pack.

For later gameplay-only updates, replace the installed datapack ZIP and run `/reload` or restart. Do not leave duplicate versions installed. Resource-pack changes also need distribution to every client.

### Prompt players to download the resource pack

Host **`dist/mysterybox-resourcepack-26.3.zip`**, not the full source bundle, at a public direct-download HTTPS URL. Opening that URL must return the ZIP bytes, not a login page, file-sharing preview, or HTML download button. Minecraft clients—not the game server—download it from this host.

Compute SHA-1 over the final ZIP:

```sh
sha1sum dist/mysterybox-resourcepack-26.3.zip
```

Stop the server, then set these properties, replacing the illustrative URL and checksum:

```properties
resource-pack=https://example.com/minecraft/server-resources-26.3.zip
resource-pack-sha1=REPLACE_WITH_THE_40_HEX_DIGIT_SHA1
resource-pack-prompt={"text":"Download the server resource pack for Mystery Box models and sounds."}
require-resource-pack=true
```

With `require-resource-pack=true`, declining the download disconnects the player. Use `false` if it should be optional; players who decline will not see the intended models or hear the custom laugh. Players can choose **Prompt** or **Enabled** for **Server Resource Packs** in the multiplayer server entry.

`resource-pack-id` is optional: the server derives an ID from the URL if omitted. A host managing stable pack identities may supply its own valid UUID. This is separate from the SHA-1 checksum.

Restart the dedicated server and reconnect a client to test the download prompt. Whenever the ZIP changes, upload the new bytes, update `resource-pack-sha1`, and restart/reconnect. Versioned URLs help avoid stale hosting caches. `/reload` reloads datapacks; it does **not** reload `server.properties` or distribute new client textures.

The download and prompt settings are source-checked, not a claim that a public server has been configured or tested here. See Mojang's [required-pack behavior](https://www.minecraft.net/en-us/article/minecraft-snapshot-20w45a), [custom prompt syntax](https://www.minecraft.net/en-us/article/minecraft-snapshot-21w15a), and [resource-pack IDs/cache behavior](https://www.minecraft.net/en-us/article/minecraft-java-edition-1-20-3).

### One larger server resource pack for future content

**Recommended: one combined resource ZIP maintained by the host.** Keep gameplay datapacks separate. Unpack this resource ZIP and future resource packs into a staging directory with this structure:

```text
pack.mcmeta
assets/
  mysterybox/
  another_namespace/
```

- Keep **one root `pack.mcmeta`**, with metadata valid for all included assets and the target client. For this exact release:

  ```json
  {"pack":{"min_format":[97,1],"max_format":[97,1],"description":"Server resources including Mystery Box"}}
  ```

- Preserve `assets/mysterybox/` and its resource IDs. Different namespaces usually combine cleanly; do not blindly overwrite identical paths. Resolve conflicting models, item definitions, textures, fonts, and other shared files deliberately.
- If multiple inputs contain `assets/<same_namespace>/sounds.json`, merge the sound-event entries into **one JSON object**, resolving duplicate event names intentionally. Do not concatenate JSON files or overwrite one whole sound map.
- Include custom dependencies, but do not copy the whole vanilla asset tree. The spruce and brick references resolve from Minecraft's built-in resources. A pack overriding those vanilla textures changes this box too.
- ZIP the **contents** of the staging directory so `pack.mcmeta` and `assets/` are at the ZIP root. Do not ZIP an enclosing folder or put separate resource-pack ZIPs inside another ZIP.
- Test the merged ZIP locally, calculate a fresh SHA-1, host it, and point `resource-pack` at that combined ZIP. Check every included feature after each update. Keep upstream pack versions and licenses with the host's build records.

Minecraft's protocol supports multiple server packs, but sending and ordering them requires suitable server software; this guide does not assume a plugin or undocumented vanilla command. A single merged pack works with the standard `server.properties` setup above.
