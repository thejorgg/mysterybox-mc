"""Canonical gameplay source and deterministic Java 26.3 pack generator.

Run with Python 3. No Minecraft libraries or network access required.
Catalog and melody inputs are versioned separately under source/.
"""
import json
from pathlib import Path
import textwrap
import zipfile
from melody import read_notes
from economy import register as register_economy
from loot import LOOT_MODES, gear_items, loot_tables

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'datapack'
CATALOG = json.loads((ROOT / 'source/catalog-26.3.json').read_text())
GEAR = gear_items(CATALOG)
LOOT_TABLES = loot_tables(CATALOG)
DEFAULTS = json.loads((ROOT / 'source/defaults.json').read_text())
MELODY = json.loads((ROOT / 'source/opening_melody.json').read_text())
MELODY['notes'] = read_notes(ROOT / 'source' / MELODY['notes_file'])
MELODY['finished_notes'] = read_notes(ROOT / 'source' / MELODY['finished_notes_file'])
DURATION = MELODY['duration_ticks']
REVEAL = MELODY['reveal_tick']
if MELODY['finished_duration_ticks'] != 40 or DURATION != REVEAL + 40:
    raise ValueError('melody duration must end 40 ticks after reveal_tick')
if not 1 < REVEAL or any(note['tick'] >= REVEAL for note in MELODY['notes']):
    raise ValueError('opening notes must precede reveal_tick')
if any(note['tick'] > MELODY['finished_duration_ticks'] for note in MELODY['finished_notes']):
    raise ValueError('finished notes must fit within finished_duration_ticks')
FUNCTIONS = {}


def function(name, commands):
    FUNCTIONS[name] = textwrap.dedent(commands).strip() + '\n'

register_economy(function, REVEAL)


def json_file(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n')


function('load', '''
    scoreboard objectives add mb dummy
    scoreboard objectives add mb_music dummy
    function mysterybox:economy/load
    scoreboard players set #sixteen mb 16
    scoreboard players set #four mb 4
    execute unless score #state mb matches 0.. run scoreboard players set #state mb 0
    function mysterybox:defaults
    execute in minecraft:overworld run data remove entity @e[tag=mysterybox.anchor,limit=1] data.collision_blocked
''')
function('defaults', '\n'.join([
    f'execute unless data storage mysterybox:config {key} run data modify storage mysterybox:config {key} set value {json.dumps(value)}'
    for key, value in DEFAULTS.items()
] + [
    'execute if data storage mysterybox:config {teddy_sound:"minecraft:entity.ghast.warn"} run data modify storage mysterybox:config teddy_sound set value "mysterybox:teddy_laugh"',
    'execute if data storage mysterybox:config {teddy_sound:"minecraft:entity.witch.celebrate"} run data modify storage mysterybox:config teddy_sound set value "mysterybox:teddy_laugh"',
    'data remove storage mysterybox:config price',
    'data remove storage mysterybox:config price_levels',
    'data remove storage mysterybox:config reward_sound',
    'execute if data storage mysterybox:config {placement:2} run data modify storage mysterybox:config placement set value 1',
    'execute unless data storage mysterybox:runtime {loot_sets_v1:1b} run function mysterybox:config/loot_upgrade',
    'execute unless data storage mysterybox:runtime {separate_curses_v1:1b} run function mysterybox:config/curse_upgrade',
    'execute unless data storage mysterybox:runtime {price_ten_v1:1b} run function mysterybox:config/price_upgrade',
]))
function('config/loot_upgrade', '''
    execute if data storage mysterybox:config {loot_mode:"all"} run data modify storage mysterybox:config loot_mode set value "default"
    execute if data storage mysterybox:config {teddy_basis_points:1000} run data modify storage mysterybox:config teddy_basis_points set value 400
    execute if data storage mysterybox:runtime {loot_table:"mysterybox:all_gear"} run data modify storage mysterybox:runtime loot_table set value "mysterybox:weapons_armor"
    data modify storage mysterybox:runtime loot_sets_v1 set value 1b
''')
function('config/curse_upgrade', '''
    data modify storage mysterybox:config binding_curse set value 0
    data modify storage mysterybox:config vanishing_curse set value 0
    data modify storage mysterybox:runtime separate_curses_v1 set value 1b
''')
function('config/price_upgrade', '''
    execute if data storage mysterybox:config {price_points:95} run data modify storage mysterybox:config price_points set value 10
    data modify storage mysterybox:runtime price_ten_v1 set value 1b
''')
function('tick', '''
    function mysterybox:economy/tick
    execute in minecraft:overworld as @e[type=marker,tag=mysterybox.music_preview] at @s run function mysterybox:sound/preview_tick
    execute if data storage mysterybox:runtime {disabled:1b} run return 0
    execute unless data storage mysterybox:runtime {initialized:1b} run function mysterybox:initialize
    execute in minecraft:overworld at @e[type=marker,tag=mysterybox.anchor,limit=1] run function mysterybox:box/tick
''')
function('initialize', '''
    execute unless data storage mysterybox:runtime boot_requested run function mysterybox:initialize_request
    execute unless loaded ~ ~ ~ run return 0
    execute align xz positioned ~0.5 ~ ~0.5 run summon marker ~ ~ ~ {Tags:["mysterybox.all","mysterybox.anchor"],data:{owned_chunk:0b}}
    data modify entity @e[type=marker,tag=mysterybox.anchor,limit=1] data.owned_chunk set from storage mysterybox:runtime boot_owned
    data modify storage mysterybox:runtime initialized set value 1b
    scoreboard players set #crate mb 0
    scoreboard players set #state mb 0
    scoreboard players set #good mb 0
    scoreboard players set #mode mb 0
    execute as @e[type=marker,tag=mysterybox.anchor,limit=1] at @s positioned over world_surface run tp @s ~ ~ ~
    execute at @e[type=marker,tag=mysterybox.anchor,limit=1] run function mysterybox:placement/check
    execute if score #good mb matches 1 at @e[type=marker,tag=mysterybox.anchor,limit=1] run function mysterybox:box/spawn
    execute if score #good mb matches 0 run function mysterybox:placement/start
''')
function('initialize_request', '''
    execute store success score #forced mb run forceload query ~ ~
    data modify storage mysterybox:runtime boot_owned set value 0b
    execute if score #forced mb matches 0 run data modify storage mysterybox:runtime boot_owned set value 1b
    execute if score #forced mb matches 0 run forceload add ~ ~
    data modify storage mysterybox:runtime boot_requested set value 1b
''')

# Three two-block-tall interaction columns cover the base and the pass-through row.
# Interaction width applies to both X and Z, so a single width-3 entity is too deep.
base_clear = ' '.join(f'if block ~{x} ~{y} ~ #minecraft:air' for x in (-1, 0, 1) for y in (0, 1))
function('collision/check', f'''
    scoreboard players set #clear_base mb 0
    execute {base_clear} run scoreboard players set #clear_base mb 1
''')
collision_install = [
    'function mysterybox:collision/check',
    'execute unless score #clear_base mb matches 1 run return 0',
]
for x, key in ((-1, 'left'), (1, 'right')):
    collision_install += [
        f'data modify entity @e[tag=mysterybox.anchor,limit=1] data.collision.{key}_owned set value 0b',
        f'execute store success score #edge_forced mb run forceload query ~{x} ~',
        f'execute if score #edge_forced mb matches 0 store success entity @e[tag=mysterybox.anchor,limit=1] data.collision.{key}_owned byte 1 run forceload add ~{x} ~',
        f'execute store success score #edge_forced mb run forceload query ~{x} ~',
        'execute unless score #edge_forced mb matches 1 run return 0',
    ]
collision_restore = []
for x, key in ((-1, 'left'), (0, 'center'), (1, 'right')):
    collision_install.append(f'data modify entity @e[tag=mysterybox.anchor,limit=1] data.collision.{key} set value "minecraft:air"')
    for air in ('cave_air', 'void_air'):
        collision_install.append(f'execute if block ~{x} ~ ~ minecraft:{air} run data modify entity @e[tag=mysterybox.anchor,limit=1] data.collision.{key} set value "minecraft:{air}"')
    collision_install += [
        f'setblock ~{x} ~ ~ minecraft:barrier',
    ]
    collision_restore.append(f'$execute if block ~{x} ~ ~ minecraft:barrier run setblock ~{x} ~ ~ $({key})')
collision_install += [
    'function mysterybox:collision/hitboxes',
    'data modify entity @e[tag=mysterybox.anchor,limit=1] data.collision.active set value 1b',
    'function mysterybox:light/install',
    'data remove entity @e[tag=mysterybox.anchor,limit=1] data.collision_blocked',
]
function('collision/install', '\n'.join(collision_install))
function('collision/restore', '\n'.join(collision_restore))
function('collision/hitboxes', '\n'.join([
    'kill @e[type=interaction,tag=mysterybox.interaction]',
    'kill @e[type=interaction,tag=mysterybox.guard]',
] + [
    f'summon interaction ~{x} ~ ~ {{Tags:["mysterybox.all","mysterybox.interaction"],width:1.02f,height:2.002f,response:1b}}'
    for x in (-1, 0, 1)
] + [
    'data modify entity @e[tag=mysterybox.anchor,limit=1] data.collision.hitboxes_version set value 2b',
]))
# The light occupies air above the solid base, never the opaque barrier itself.
function('light/install', '''
    execute if data entity @e[tag=mysterybox.anchor,limit=1] data.light_air run return 0
    execute unless block ~ ~1 ~ #minecraft:air run return 0
    data modify entity @e[tag=mysterybox.anchor,limit=1] data.light_air set value "minecraft:air"
    execute if block ~ ~1 ~ minecraft:cave_air run data modify entity @e[tag=mysterybox.anchor,limit=1] data.light_air set value "minecraft:cave_air"
    execute if block ~ ~1 ~ minecraft:void_air run data modify entity @e[tag=mysterybox.anchor,limit=1] data.light_air set value "minecraft:void_air"
    setblock ~ ~1 ~ minecraft:light[level=9,waterlogged=false]
''')
function('light/restore', '''
    $execute if block ~ ~1 ~ minecraft:light[level=9,waterlogged=false] run setblock ~ ~1 ~ $(light_air)
''')
function('light/remove', '''
    execute if data entity @e[tag=mysterybox.anchor,limit=1] data.light_air run function mysterybox:light/restore with entity @e[tag=mysterybox.anchor,limit=1] data
    data remove entity @e[tag=mysterybox.anchor,limit=1] data.light_air
''')
function('collision/remove', '''
    execute unless entity @e[tag=mysterybox.anchor,nbt={data:{collision:{active:1b}}}] run return 0
    function mysterybox:light/remove
    function mysterybox:collision/restore with entity @e[tag=mysterybox.anchor,limit=1] data.collision
    kill @e[type=interaction,tag=mysterybox.interaction]
    kill @e[type=interaction,tag=mysterybox.guard]
    execute if entity @e[tag=mysterybox.anchor,nbt={data:{collision:{left_owned:1b}}}] run forceload remove ~-1 ~
    execute if entity @e[tag=mysterybox.anchor,nbt={data:{collision:{right_owned:1b}}}] run forceload remove ~1 ~
    data modify entity @e[tag=mysterybox.anchor,limit=1] data.collision.active set value 0b
''')
function('collision/upgrade', '''
    execute if entity @e[tag=mysterybox.anchor,nbt={data:{collision_blocked:1b}}] run return 0
    function mysterybox:collision/check
    execute if score #clear_base mb matches 1 run return run function mysterybox:collision/install
    tellraw @a {"text":"Mystery box collision upgrade blocked: its 3x1 base and row above must be empty. Clear the obstruction and /reload, or use admin/place at a clear location. No terrain was overwritten.","color":"yellow"}
    data modify entity @e[tag=mysterybox.anchor,limit=1] data.collision_blocked set value 1b
''')

# Body displays share the anchor; beam sections have their own world positions.
parts = [
    ('body', [0, 0, 0], [1, 1, 1], False),
    ('lid', [0, .875, .5], [1, 1, 1], False),
    ('shine', [0, .5625, 0], [0, 0, 0], True),
]
spawn = []
for name, translation, scale, bright in parts:
    nbt = {'Tags': ['mysterybox.all', 'mysterybox.part', 'mysterybox.' + name],
           'item': {'id': 'minecraft:paper', 'count': 1, 'components': {'minecraft:item_model': 'mysterybox:' + name}},
           'transformation': {'translation': translation, 'scale': scale, 'left_rotation': [0., 0., 0., 1.], 'right_rotation': [0., 1., 0., 0.]},
           'view_range': 2}
    if bright:
        nbt['brightness'] = {'block': 15, 'sky': 15}
    spawn.append('summon item_display ~ ~ ~ ' + json.dumps(nbt, separators=(',', ':')))
spawn += ['scoreboard players set #crate mb 1', 'scoreboard players set #state mb 0',
          'data modify storage mysterybox:runtime position set from entity @e[tag=mysterybox.anchor,limit=1] Pos',
          'function mysterybox:collision/install',
          'function mysterybox:box/beam_spawn']
function('box/spawn', '\n'.join(spawn))
function('box/beam_remove', '''
    kill @e[type=item_display,tag=mysterybox.beam]
    kill @e[type=item_display,tag=mysterybox.beam_down]
''')
beam_spawn = ['function mysterybox:box/beam_remove']
for direction in ('up', 'down'):
    for section in range(6):
        y = 3.0625 + 16 * section if direction == 'up' else -3 - 16 * (section + 1)
        nbt = {
            'Tags': ['mysterybox.all', 'mysterybox.part', 'mysterybox.beam', 'mysterybox.beam_' + direction],
            'item': {'id': 'minecraft:paper', 'count': 1, 'components': {'minecraft:item_model': 'mysterybox:beam'}},
            'transformation': {'translation': [0., 0., 0.], 'scale': [1., 16., 1.],
                               'left_rotation': [0., 0., 0., 1.], 'right_rotation': [0., 1., 0., 0.]},
            'billboard': 'vertical', 'width': .75, 'height': 16., 'view_range': 8.,
            'brightness': {'block': 15, 'sky': 15},
        }
        beam_spawn.append(f'summon item_display ~ ~{y} ~ ' + json.dumps(nbt, separators=(',', ':')))
beam_spawn += [
    'summon item_display ~ ~1.0625 ~ {Tags:["mysterybox.all","mysterybox.part","mysterybox.beam","mysterybox.beam_base"],item:{id:"minecraft:paper",count:1,components:{"minecraft:item_model":"mysterybox:beam_base"}},transformation:{translation:[0f,0f,0f],scale:[1f,2f,1f],left_rotation:[0f,0f,0f,1f],right_rotation:[0f,1f,0f,0f]},billboard:"vertical",width:0.75f,height:2f,view_range:8f,brightness:{block:15,sky:15}}',
    'data modify entity @e[tag=mysterybox.anchor,limit=1] data.segmented_beams set value 4b',
    'data remove entity @e[tag=mysterybox.anchor,limit=1] data.beam_opacity',
    'scoreboard players reset #beam_spin mb',
]
function('box/beam_spawn', '\n'.join(beam_spawn))
function('box/tick', '''
    execute if score #crate mb matches 1 unless entity @e[tag=mysterybox.anchor,nbt={data:{collision:{active:1b}}}] run function mysterybox:collision/upgrade
    execute if score #crate mb matches 1 if entity @e[tag=mysterybox.anchor,nbt={data:{collision:{active:1b}}}] unless entity @e[tag=mysterybox.anchor,nbt={data:{collision:{hitboxes_version:2b}}}] run function mysterybox:collision/hitboxes
    execute if score #crate mb matches 1 unless entity @e[tag=mysterybox.anchor,nbt={data:{segmented_beams:4b}}] run function mysterybox:box/beam_spawn
    execute if score #crate mb matches 1 if entity @e[tag=mysterybox.anchor,nbt={data:{collision:{active:1b}}}] run function mysterybox:light/install
    execute as @e[type=interaction,tag=mysterybox.interaction] if data entity @s interaction on target run function mysterybox:purchase
    execute as @e[type=interaction,tag=mysterybox.interaction] run data remove entity @s interaction
    execute if score #state mb matches 3 run function mysterybox:box/close_tick
    execute if score #state mb matches 1 run function mysterybox:box/open_tick
    execute if score #state mb matches 2 run function mysterybox:placement/tick
''')
function('purchase', '''
    execute unless entity @s[type=player,gamemode=!spectator] run return 0
    execute unless score #state mb matches 0 run return run tellraw @s {text:"The mystery box is busy.",color:"gray"}
    execute store result score #price mb run data get storage mysterybox:config price_points
    execute store result score #chance mb run data get storage mysterybox:config teddy_basis_points
    execute store result score #mending_chance mb run data get storage mysterybox:config mending_basis_points
    execute store result score #minimum mb run data get storage mysterybox:config enchant_level_min
    execute store result score #maximum mb run data get storage mysterybox:config enchant_level_max
    execute unless score #chance mb matches 0..10000 run return run function mysterybox:config_error
    execute unless score #mending_chance mb matches 0..10000 run return run function mysterybox:config_error
    execute unless score #minimum mb matches 1..30 run return run function mysterybox:config_error
    execute unless score #maximum mb matches 1..30 run return run function mysterybox:config_error
    execute if score #minimum mb > #maximum mb run return run function mysterybox:config_error
    execute unless data storage mysterybox:config {binding_curse:0} unless data storage mysterybox:config {binding_curse:1} run return run function mysterybox:config_error
    execute unless data storage mysterybox:config {vanishing_curse:0} unless data storage mysterybox:config {vanishing_curse:1} run return run function mysterybox:config_error
    execute store result score #loot_valid mb run function mysterybox:reward/select_mode
    execute unless score #loot_valid mb matches 1 run return run function mysterybox:config_error
    execute store result score #can_pay mb run function mysterybox:economy/check
    execute unless score #can_pay mb matches 1 run return 0
    execute store result score #charged mb run function mysterybox:economy/charge
    execute unless score #charged mb matches 1 run return 0
    scoreboard players set #state mb 1
    scoreboard players set #timer mb 0
    scoreboard players set #bear mb 0
    execute store result score #roll mb run random value 1..10000
    execute if score #roll mb <= #chance mb if data storage mysterybox:config {relocate:1} run scoreboard players set #bear mb 1
    execute if score #bear mb matches 1 run function mysterybox:economy/queue_teddy
    summon item_display ~ ~ ~ {Tags:["mysterybox.all","mysterybox.reward"],billboard:"vertical",transformation:{translation:[0f,0f,0f],scale:[0.8f,0.8f,0.8f],left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f]},item:{id:"minecraft:paper",count:1}}
    function mysterybox:reward/draw with storage mysterybox:runtime
    execute if score #bear mb matches 0 run function mysterybox:reward/prepare
    execute if score #bear mb matches 1 run data modify storage mysterybox:runtime reward set value {id:"minecraft:paper",count:1,components:{"minecraft:item_model":"mysterybox:teddy"}}
    data merge entity @e[tag=mysterybox.lid,limit=1] {start_interpolation:0,interpolation_duration:20,transformation:{left_rotation:[0.79335334f,0f,0f,0.60876143f]}}
    data merge entity @e[tag=mysterybox.shine,limit=1] {transformation:{scale:[1f,1f,1f]}}
    function mysterybox:sound/opening with storage mysterybox:config
''')
function('config_error', 'tellraw @s {text:"Mystery box configuration is invalid; no XP points were taken. Ask an administrator.",color:"red"}')
# Capture the mode once: later configuration edits must not change this opening.
select_mode = []
for setting, table in LOOT_MODES.items():
    select_mode.append(f'execute if data storage mysterybox:config {{loot_mode:"{setting}"}} run return run function mysterybox:reward/mode_{table}')
for table in LOOT_TABLES:
    function('reward/mode_' + table, f'''
        data modify storage mysterybox:runtime loot_mode set value "{table}"
        data modify storage mysterybox:runtime loot_table set value "mysterybox:{table}"
        data modify storage mysterybox:runtime binding_curse set from storage mysterybox:config binding_curse
        data modify storage mysterybox:runtime vanishing_curse set from storage mysterybox:config vanishing_curse
        data modify storage mysterybox:runtime mending_basis_points set from storage mysterybox:config mending_basis_points
        return 1
    ''')
function('reward/select_mode', '\n'.join(select_mode + ['return 0']))
function('reward/draw', '''
    $loot replace entity @e[tag=mysterybox.reward,limit=1] contents loot $(loot_table)
    function mysterybox:reward/visual
''')
# Context none selects the trident's projectile-style renderer; GUI uses its sprite.
function('reward/visual', '''
    data merge entity @e[tag=mysterybox.reward,limit=1] {item_display:"none"}
    execute if items entity @e[tag=mysterybox.reward,limit=1] contents minecraft:trident run data merge entity @e[tag=mysterybox.reward,limit=1] {item_display:"gui"}
''')
function('reward/prepare', '''
    execute if items entity @e[tag=mysterybox.reward,limit=1] contents #mysterybox:gear run function mysterybox:reward/prepare_gear
    execute if data storage mysterybox:runtime {binding_curse:1} run data modify entity @e[tag=mysterybox.reward,limit=1] item.components."minecraft:enchantments"."minecraft:binding_curse" set value 1
    execute if data storage mysterybox:runtime {vanishing_curse:1} run data modify entity @e[tag=mysterybox.reward,limit=1] item.components."minecraft:enchantments"."minecraft:vanishing_curse" set value 1
    data modify storage mysterybox:runtime reward set from entity @e[tag=mysterybox.reward,limit=1] item
''')
function('reward/prepare_gear', '''
    function mysterybox:reward/enchant with storage mysterybox:config
    data remove entity @e[tag=mysterybox.reward,limit=1] item.components."minecraft:enchantments"."minecraft:mending"
    data remove entity @e[tag=mysterybox.reward,limit=1] item.components."minecraft:enchantments"."minecraft:binding_curse"
    data remove entity @e[tag=mysterybox.reward,limit=1] item.components."minecraft:enchantments"."minecraft:vanishing_curse"
    execute store result score #enchanted mb run data get entity @e[tag=mysterybox.reward,limit=1] item.components."minecraft:enchantments"
    execute if score #enchanted mb matches 0 run function mysterybox:reward/fallback_enchant
    execute if items entity @e[tag=mysterybox.reward,limit=1] contents #minecraft:enchantable/durability run function mysterybox:reward/mending
    execute store result score #binding_roll mb run random value 1..10000
    execute store result score #vanishing_roll mb run random value 1..10000
    function mysterybox:reward/random_curses
    execute if data storage mysterybox:runtime {loot_mode:"godmode"} run function mysterybox:reward/max_enchantments
''')
function('reward/enchant', '$item modify entity @e[tag=mysterybox.reward,limit=1] contents {\"type\":\"minecraft:enchant_with_levels\",\"levels\":{\"type\":\"minecraft:uniform\",\"min\":$(enchant_level_min),\"max\":$(enchant_level_max)}}')
function('reward/fallback_enchant', 'item modify entity @e[tag=mysterybox.reward,limit=1] contents ' + json.dumps({
    'type': 'minecraft:enchant_randomly', 'only_compatible': True,
    'options': [entry['id'] for entry in CATALOG['enchantments'] if entry['id'] not in ('minecraft:mending', 'minecraft:binding_curse', 'minecraft:vanishing_curse')],
}, separators=(',', ':')))
function('reward/random_curses', '''
    execute if score #binding_roll mb matches 1..200 if items entity @e[tag=mysterybox.reward,limit=1] contents #minecraft:enchantable/equippable run data modify entity @e[tag=mysterybox.reward,limit=1] item.components."minecraft:enchantments"."minecraft:binding_curse" set value 1
    execute if score #vanishing_roll mb matches 1..200 if items entity @e[tag=mysterybox.reward,limit=1] contents #minecraft:enchantable/vanishing run data modify entity @e[tag=mysterybox.reward,limit=1] item.components."minecraft:enchantments"."minecraft:vanishing_curse" set value 1
''')
function('reward/mending', '''
    execute store result score #mending_chance mb run data get storage mysterybox:runtime mending_basis_points
    execute unless score #mending_chance mb matches 1..10000 run return 0
    execute store result score #mending_roll mb run random value 1..10000
    execute if score #mending_roll mb <= #mending_chance mb run function mysterybox:reward/add_mending
''')
function('reward/add_mending', '''
    data remove entity @e[tag=mysterybox.reward,limit=1] item.components."minecraft:enchantments"."minecraft:infinity"
    data modify entity @e[tag=mysterybox.reward,limit=1] item.components."minecraft:enchantments"."minecraft:mending" set value 1
''')
# Upgrade only enchantments actually rolled, preserving vanilla compatibility.
function('reward/max_enchantments', '\n'.join(
    f'execute if data entity @e[tag=mysterybox.reward,limit=1] item.components."minecraft:enchantments"."{enchantment["id"]}" run data modify entity @e[tag=mysterybox.reward,limit=1] item.components."minecraft:enchantments"."{enchantment["id"]}" set value {enchantment["max_level"]}'
    for enchantment in CATALOG['enchantments']
))
function('box/open_tick', f'''
    scoreboard players add #timer mb 1
    execute if score #timer mb matches 2 run data merge entity @e[tag=mysterybox.reward,limit=1] {{start_interpolation:0,interpolation_duration:{REVEAL-2},transformation:{{translation:[0f,1.62f,0f]}}}}
    scoreboard players operation #frame mb = #timer mb
    scoreboard players operation #frame mb %= #four mb
    execute if score #timer mb matches ..{REVEAL-1} if score #frame mb matches 0 run function mysterybox:reward/draw with storage mysterybox:runtime
    execute if score #timer mb matches {REVEAL} run data modify entity @e[tag=mysterybox.reward,limit=1] item set from storage mysterybox:runtime reward
    execute if score #timer mb matches {REVEAL} run function mysterybox:reward/visual
    execute if score #timer mb matches {REVEAL} if score #bear mb matches 1 run function mysterybox:sound/teddy_reveal
    scoreboard players operation #note_tick mb = #timer mb
    execute if score #timer mb matches ..{REVEAL-1} if data storage mysterybox:config {{melody:1}} run function mysterybox:sound/melody
    execute if score #timer mb matches {REVEAL}.. if score #bear mb matches 0 if data storage mysterybox:config {{melody:1}} run function mysterybox:sound/finished_tick
    execute if score #timer mb matches {DURATION}.. run function mysterybox:box/finish
''')
function('box/finish', '''
    execute if score #bear mb matches 0 run function mysterybox:reward/drop
    scoreboard players set #state mb 3
    scoreboard players set #timer mb 0
    data merge entity @e[tag=mysterybox.lid,limit=1] {start_interpolation:0,interpolation_duration:20,transformation:{left_rotation:[0f,0f,0f,1f]}}
    data merge entity @e[tag=mysterybox.shine,limit=1] {transformation:{scale:[0f,0f,0f]}}
    kill @e[tag=mysterybox.reward]
    function mysterybox:sound/closing with storage mysterybox:config
''')
function('reward/drop', '''
    summon item ~ ~1.62 ~ {Tags:["mysterybox.drop_pending"],Item:{id:"minecraft:paper",count:1},PickupDelay:10s,Motion:[0d,0.12d,-0.12d]}
    data modify entity @e[type=item,tag=mysterybox.drop_pending,limit=1] Item set from storage mysterybox:runtime reward
    execute if data storage mysterybox:runtime reward{id:"minecraft:bow"} run function mysterybox:reward/arrows
    execute if data storage mysterybox:runtime reward{id:"minecraft:crossbow"} run function mysterybox:reward/arrows
    execute if data storage mysterybox:runtime reward{id:"minecraft:tnt"} run summon item ~ ~1.62 ~ {Tags:["mysterybox.drop_pending"],Item:{id:"minecraft:flint_and_steel",count:1},PickupDelay:10s,Motion:[0.08d,0.12d,-0.12d]}
    execute if data storage mysterybox:runtime {binding_curse:1} as @e[type=item,tag=mysterybox.drop_pending] run data modify entity @s Item.components."minecraft:enchantments"."minecraft:binding_curse" set value 1
    execute if data storage mysterybox:runtime {vanishing_curse:1} as @e[type=item,tag=mysterybox.drop_pending] run data modify entity @s Item.components."minecraft:enchantments"."minecraft:vanishing_curse" set value 1
    tag @e[type=item,tag=mysterybox.drop_pending] remove mysterybox.drop_pending
''')
function('reward/arrows', 'summon item ~ ~1.62 ~ {Tags:["mysterybox.drop_pending"],Item:{id:"minecraft:arrow",count:64},PickupDelay:10s,Motion:[0.08d,0.12d,-0.12d]}')
function('box/close_tick', '''
    scoreboard players add #timer mb 1
    execute unless score #timer mb matches 20.. run return 0
    scoreboard players set #state mb 0
    execute if score #bear mb matches 1 run function mysterybox:placement/start
''')

# Random horizontal annulus; no terrain edits. Owned forceload tickets are released,
# but chunks already forced by another pack/admin are never unforced here.
function('placement/start', '''
    scoreboard players set #state mb 2
    scoreboard players set #phase mb 0
    scoreboard players set #attempts mb 0
    execute store result score #mode mb run data get storage mysterybox:config placement
    execute unless score #mode mb matches 0 run scoreboard players set #mode mb 1
''')
function('placement/tick', '''
    execute if score #attempts mb matches 128.. run return run function mysterybox:placement/abort
    execute if score #phase mb matches 0 run return run function mysterybox:placement/candidate
    execute if score #phase mb matches 1 run function mysterybox:placement/wait with storage mysterybox:runtime target
''')
function('placement/candidate', '''
    scoreboard players add #attempts mb 1
    execute store result score #dx mb run random value -64..64
    execute store result score #dz mb run random value -64..64
    scoreboard players operation #distance mb = #dx mb
    scoreboard players operation #distance mb *= #dx mb
    scoreboard players operation #square mb = #dz mb
    scoreboard players operation #square mb *= #dz mb
    scoreboard players operation #distance mb += #square mb
    execute unless score #distance mb matches 256..4096 run return 0
    execute store result score #x mb run data get entity @e[tag=mysterybox.anchor,limit=1] Pos[0]
    execute store result score #z mb run data get entity @e[tag=mysterybox.anchor,limit=1] Pos[2]
    scoreboard players operation #x mb += #dx mb
    scoreboard players operation #z mb += #dz mb
    scoreboard players operation #cx mb = #x mb
    scoreboard players operation #cz mb = #z mb
    scoreboard players operation #cx mb /= #sixteen mb
    scoreboard players operation #cz mb /= #sixteen mb
    execute store result score #old_cx mb run data get entity @e[tag=mysterybox.anchor,limit=1] Pos[0] 0.0625
    execute store result score #old_cz mb run data get entity @e[tag=mysterybox.anchor,limit=1] Pos[2] 0.0625
    execute if score #cx mb = #old_cx mb if score #cz mb = #old_cz mb run return 0
    execute unless score #x mb matches -29999980..29999980 run return 0
    execute unless score #z mb matches -29999980..29999980 run return 0
    execute store result storage mysterybox:runtime target.x int 1 run scoreboard players get #x mb
    execute store result storage mysterybox:runtime target.z int 1 run scoreboard players get #z mb
    execute store result storage mysterybox:runtime target.y int 1 run random value -63..318
    function mysterybox:placement/request with storage mysterybox:runtime target
''')
function('placement/request', '''
    $execute store success score #already_forced mb run forceload query $(x) $(z)
    scoreboard players set #candidate_owned mb 0
    $execute if score #already_forced mb matches 0 store success score #candidate_owned mb run forceload add $(x) $(z)
    scoreboard players set #phase mb 1
    scoreboard players set #waiting mb 0
''')
function('placement/wait', '''
    scoreboard players add #waiting mb 1
    $execute if loaded $(x) 0 $(z) run return run function mysterybox:placement/probe with storage mysterybox:runtime target
    execute if score #waiting mb matches 40.. run function mysterybox:placement/reject with storage mysterybox:runtime target
''')
function('placement/probe', '''
    $summon marker $(x) $(y) $(z) {Tags:["mysterybox.probe"]}
    execute if score #mode mb matches 0 as @e[tag=mysterybox.probe,limit=1] at @s positioned over world_surface run tp @s ~ ~ ~
    scoreboard players set #good mb 0
    scoreboard players set #depth mb 64
    execute unless score #mode mb matches 1 run scoreboard players set #depth mb 1
    execute as @e[tag=mysterybox.probe,limit=1] at @s run function mysterybox:placement/scan
    execute if score #good mb matches 1 run function mysterybox:placement/accept
    execute if score #good mb matches 0 run function mysterybox:placement/reject with storage mysterybox:runtime target
''')
function('placement/scan', '''
    function mysterybox:placement/check
    execute if score #good mb matches 1 run return 1
    scoreboard players remove #depth mb 1
    execute store result score #height mb run data get entity @s Pos[1]
    execute unless score #height mb matches -62..318 run return 0
    tp @s ~ ~-1 ~
    execute if score #depth mb matches 1.. at @s run function mysterybox:placement/scan
''')
support = ' '.join(f'if block ~{x} ~-1 ~ #mysterybox:support' for x in (-1, 0, 1))
function('placement/check', f'''
    execute {support} {base_clear} run scoreboard players set #good mb 1
''')
# A destination may be in the old footprint's extra forced chunk. Transfer that
# ticket instead of releasing it and treating it as another administrator's.
for offset, key in ((-1, 'left'), (1, 'right')):
    function('collision/transfer_' + key, f'''
        scoreboard players set #candidate_owned mb 1
        data modify entity @e[tag=mysterybox.anchor,limit=1] data.collision.{key}_owned set value 0b
    ''')
function('collision/transfer', '''
    scoreboard players operation #edge_cx mb = #old_cx mb
    scoreboard players remove #edge_cx mb 1
    execute if score #cx mb = #edge_cx mb if score #cz mb = #old_cz mb if entity @e[tag=mysterybox.anchor,nbt={data:{collision:{left_owned:1b}}}] run function mysterybox:collision/transfer_left
    scoreboard players add #edge_cx mb 2
    execute if score #cx mb = #edge_cx mb if score #cz mb = #old_cz mb if entity @e[tag=mysterybox.anchor,nbt={data:{collision:{right_owned:1b}}}] run function mysterybox:collision/transfer_right
''')
function('placement/accept', '''
    function mysterybox:sound/moving with storage mysterybox:config
    function mysterybox:collision/transfer
    function mysterybox:collision/remove
    function mysterybox:box/beam_remove
    execute if entity @e[tag=mysterybox.anchor,nbt={data:{owned_chunk:1b}}] run forceload remove ~ ~
    execute as @e[tag=mysterybox.all] run tp @s @e[tag=mysterybox.probe,limit=1]
    data modify entity @e[tag=mysterybox.anchor,limit=1] data.owned_chunk set value 0b
    execute if score #candidate_owned mb matches 1 run data modify entity @e[tag=mysterybox.anchor,limit=1] data.owned_chunk set value 1b
    data modify storage mysterybox:runtime position set from entity @e[tag=mysterybox.anchor,limit=1] Pos
    kill @e[tag=mysterybox.probe]
    scoreboard players set #state mb 0
    scoreboard players set #phase mb 0
    execute if score #crate mb matches 1 at @e[tag=mysterybox.anchor,limit=1] run function mysterybox:box/beam_spawn
    execute if score #crate mb matches 0 at @e[tag=mysterybox.anchor,limit=1] run function mysterybox:box/spawn
    execute at @e[tag=mysterybox.anchor,limit=1] run function mysterybox:sound/moving with storage mysterybox:config
    execute unless entity @e[tag=mysterybox.anchor,nbt={data:{collision:{active:1b}}}] at @e[tag=mysterybox.anchor,limit=1] run function mysterybox:collision/install
''')
function('placement/reject', '''
    kill @e[tag=mysterybox.probe]
    $execute if score #candidate_owned mb matches 1 run forceload remove $(x) $(z)
    scoreboard players set #phase mb 0
''')
function('placement/abort', '''
    scoreboard players set #state mb 0
    tellraw @a {text:"Mystery box: no clear destination found within 16–64 blocks. The existing box has not moved.",color:"yellow"}
    execute if score #crate mb matches 0 run tellraw @a {text:"No suitable first spawn was found. An operator can use /function mysterybox:admin/place at a chosen Overworld location.",color:"yellow"}
''')
function('admin/place', '''
    execute unless dimension minecraft:overworld run return run tellraw @s {text:"Place the mystery box in the Overworld.",color:"red"}
    scoreboard players set #good mb 0
    execute align xyz positioned ~0.5 ~ ~0.5 run function mysterybox:placement/check
    execute unless score #good mb matches 1 run return run tellraw @s {"text":"The box needs a clear 3-wide, 2-high space over three solid floor blocks; the current box was not changed.","color":"red"}
    execute align xyz positioned ~0.5 ~ ~0.5 run function mysterybox:admin/place_clear
''')
function('admin/place_clear', '''
    function mysterybox:admin/remove
    data remove storage mysterybox:runtime disabled
    execute store success score #forced mb run forceload query ~ ~
    execute if score #forced mb matches 0 run forceload add ~ ~
    summon marker ~ ~ ~ {Tags:["mysterybox.all","mysterybox.anchor"],data:{owned_chunk:0b}}
    execute if score #forced mb matches 0 run data modify entity @e[tag=mysterybox.anchor,limit=1] data.owned_chunk set value 1b
    data modify storage mysterybox:runtime initialized set value 1b
    function mysterybox:box/spawn
''')
function('admin/remove', '''
    execute in minecraft:overworld at @e[tag=mysterybox.anchor,limit=1] run function mysterybox:collision/remove
    execute in minecraft:overworld at @e[tag=mysterybox.anchor,nbt={data:{owned_chunk:1b}},limit=1] run forceload remove ~ ~
    execute if score #phase mb matches 1 in minecraft:overworld run function mysterybox:placement/reject with storage mysterybox:runtime target
    execute in minecraft:overworld run kill @e[tag=mysterybox.all]
    data modify storage mysterybox:runtime disabled set value 1b
    data remove storage mysterybox:runtime initialized
    data remove storage mysterybox:runtime boot_requested
    scoreboard players set #state mb 0
    scoreboard players set #phase mb 0
''')
function('admin/status', '''
    data get storage mysterybox:config
    data get storage mysterybox:runtime position
    scoreboard players get #state mb
''')
for event in ('opening', 'closing', 'dragon', 'teddy', 'moving'):
    function('sound/' + event, f'''
        execute store result score #sound_volume mb run data get storage mysterybox:config {event}_volume
        execute if score #sound_volume mb matches ..0 run return 0
        execute if score #sound_volume mb matches 101.. run scoreboard players set #sound_volume mb 100
        execute store result storage mysterybox:runtime sound.volume double 0.01 run scoreboard players get #sound_volume mb
        $data modify storage mysterybox:runtime sound.sound set value "$({event}_sound)"
        function mysterybox:sound/{'play_global' if event in ('dragon', 'teddy') else 'play_cue'} with storage mysterybox:runtime sound
    ''')
function('sound/play_cue', '$playsound $(sound) block @a[distance=..24] ~ ~ ~ $(volume) 1')
function('sound/play_global', '$execute as @a at @s run playsound $(sound) block @s ~ ~ ~ $(volume) 1')
function('sound/teddy_reveal', '\n'.join(
    f'stopsound @a[distance=..24] block {sound}'
    for sound in sorted({note['sound'] for note in MELODY['notes']})
) + '\nfunction mysterybox:sound/dragon with storage mysterybox:config'
  + '\nschedule function mysterybox:sound/teddy_echo 45t append')
# This outlives the opening timer: the growl is 3 s, so the 1.06 s echo overlaps
# its last 0.75 s without being swallowed by the loud opening of the growl.
function('sound/teddy_echo', 'function mysterybox:sound/teddy with storage mysterybox:config')
function('sound/note', '''
    $scoreboard players set #note_volume mb $(volume)
    scoreboard players operation #note_volume mb *= #music_volume mb
    execute if score #note_volume mb matches 0 run return 0
    execute store result storage mysterybox:runtime note.volume double 0.0001 run scoreboard players get #note_volume mb
    $data modify storage mysterybox:runtime note.pitch set value $(pitch)
    $data modify storage mysterybox:runtime note.sound set value "$(sound)"
    function mysterybox:sound/play_note with storage mysterybox:runtime note
''')
function('sound/play_note', '$playsound $(sound) block @a[distance=..24] ~ ~ ~ $(volume) $(pitch)')
for phase, notes_key, volume_key in (
    ('melody', 'notes', 'melody_volume'),
    ('finished', 'finished_notes', 'finished_volume'),
):
    notes = [
        f'execute store result score #music_volume mb run data get storage mysterybox:config {volume_key}',
        'execute if score #music_volume mb matches ..0 run return 0',
        'execute if score #music_volume mb matches 101.. run scoreboard players set #music_volume mb 100',
    ]
    for event in MELODY[notes_key]:
        args = json.dumps({key: event[key] for key in ('sound', 'pitch', 'volume')}, separators=(',', ':'))
        notes.append(f'execute if score #note_tick mb matches {event["tick"]} run function mysterybox:sound/note {args}')
    function('sound/' + phase, '\n'.join(notes))
function('sound/finished_tick', f'''
    scoreboard players remove #note_tick mb {REVEAL - 1}
    function mysterybox:sound/finished
''')
for preview, teddy in (('preview', False), ('preview_teddy', True)):
    tags = ['mysterybox.music_preview']
    if teddy:
        tags.append('mysterybox.preview_teddy')
    function('sound/' + preview, f'''
        execute unless entity @s[type=player] run return 0
        execute unless dimension minecraft:overworld run return run tellraw @s {{"text":"Run the sound preview in the Overworld.","color":"red"}}
        kill @e[type=marker,tag=mysterybox.music_preview]
        summon marker ~ ~ ~ {{Tags:{json.dumps(tags, separators=(',', ':'))}}}
        scoreboard players set @e[type=marker,tag=mysterybox.music_preview] mb_music 0
        function mysterybox:sound/opening with storage mysterybox:config
        tellraw @s {{"text":"Playing the mystery-box {'teddy' if teddy else 'weapon'} sounds here. No XP points charged.","color":"gold"}}
    ''')
function('sound/preview_tick', f'''
    scoreboard players add @s mb_music 1
    scoreboard players operation #note_tick mb = @s mb_music
    execute if score @s mb_music matches ..{REVEAL-1} run function mysterybox:sound/melody
    execute if score @s mb_music matches {REVEAL} if entity @s[tag=mysterybox.preview_teddy] run function mysterybox:sound/teddy_reveal
    execute if score @s mb_music matches {REVEAL}.. unless entity @s[tag=mysterybox.preview_teddy] run function mysterybox:sound/finished_tick
    execute if score @s mb_music matches {DURATION}.. run function mysterybox:sound/closing with storage mysterybox:config
    execute if score @s mb_music matches {DURATION}.. run kill @s
''')

json_file(OUT / 'pack.mcmeta', {'pack': {'min_format': [121,0], 'max_format': [121,0], 'description': 'Mystery Box gameplay — Java 26.3'}})
# Explicitly owned obsolete output: never sweep unrelated/custom functions.
for obsolete in ('sound/reward', 'charge', 'insufficient', 'sound/stop_dragon', 'sound/teddy_laugh', 'box/beam_upgrade',
                 'box/beam_spin', 'box/beam_tick', *(f'box/beam_opacity_{stage}' for stage in range(9))):
    (OUT / f'data/mysterybox/function/{obsolete}.mcfunction').unlink(missing_ok=True)
(OUT / 'data/mysterybox/tags/block/clear.json').unlink(missing_ok=True)
(OUT / 'data/mysterybox/loot_table/all_gear.json').unlink(missing_ok=True)
for name, commands in FUNCTIONS.items():
    path = OUT / f'data/mysterybox/function/{name}.mcfunction'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(commands)
for tag in ('load', 'tick'):
    json_file(OUT / f'data/minecraft/tags/function/{tag}.json', {'values': ['mysterybox:' + tag]})
for name, table in LOOT_TABLES.items():
    json_file(OUT / f'data/mysterybox/loot_table/{name}.json', table)
json_file(OUT / 'data/mysterybox/tags/item/gear.json', {'values': GEAR})
json_file(OUT / 'data/mysterybox/tags/block/support.json', {'values': ['#minecraft:base_stone_overworld', '#minecraft:dirt', '#minecraft:planks', '#minecraft:logs', '#minecraft:terracotta', '#minecraft:sand', 'minecraft:grass_block', 'minecraft:snow_block', 'minecraft:stone_bricks', 'minecraft:cobblestone', 'minecraft:deepslate_bricks', 'minecraft:bricks', 'minecraft:bedrock', 'minecraft:iron_block', 'minecraft:gold_block', 'minecraft:diamond_block', 'minecraft:emerald_block', 'minecraft:packed_ice', 'minecraft:ice', 'minecraft:sandstone', 'minecraft:red_sandstone']})
(ROOT / 'dist').mkdir(exist_ok=True)
for folder, filename in ((OUT, 'mysterybox-datapack-26.3.zip'), (ROOT/'resourcepack', 'mysterybox-resourcepack-26.3.zip')):
    with zipfile.ZipFile(ROOT/'dist'/filename, 'w', zipfile.ZIP_DEFLATED) as archive:
        archive.write(ROOT/'LICENSE', 'LICENSE')
        for path in sorted(folder.rglob('*')):
            if path.is_file():
                archive.write(path, path.relative_to(folder))
print(json.dumps({'functions': len(FUNCTIONS), 'gear': len(GEAR), 'loot_entries': {name: len(table['pools'][0]['entries']) for name, table in LOOT_TABLES.items()}, 'enchantments': len(CATALOG['enchantments']), 'opening_ticks': REVEAL, 'duration_ticks': DURATION, 'melody_notes': len(MELODY['notes']), 'finished_notes': len(MELODY['finished_notes'])}))
